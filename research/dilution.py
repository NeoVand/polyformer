"""Loss-dilution experiment: paired owner-tracking narratives, causal LM.

Transfers reciprocally exchange ownership between two people (a transposition).
Aliases are snapshot references; assignment overwrites and revocation unbinds.
An unbound handle makes a transfer a no-op. The parcel's initial owner is the
only pair intervention. Since subsequent owner updates are permutations, both
answers ALWAYS differ: no label-dependent rejection or suffix generation.

The intervention changes one early operation and one final label. `p` means
final semantic-decision target share; it does not claim that intervening on an
early token changes a trained LM's loss only at the answer. The output includes
nondecision and per-position losses to quantify that distinction.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import time
from types import SimpleNamespace

import jax
import jax.numpy as jnp
import numpy as np
import optax

import lm
import beyond_layers as bl

PEOPLE = ('A','B','C','D')
ALIASES = ('w','x','y','z')
SPLITS = ('train','id','paraphrase','length','both')
SPLIT_CODES = {name: i+1 for i,name in enumerate(SPLITS)}
WORDS = 'the parcel belongs to owns now transfer ownership between and alias means revoke who . ?'.split()
TOKENS = ('<pad>','<bos>') + tuple(sorted(set(WORDS) | set(PEOPLE) | set(ALIASES)))
VOCAB = {token: i for i,token in enumerate(TOKENS)}

@dataclass(frozen=True)
class Pair:
    ops: tuple
    answers: tuple
    template: int


def resolve(handle, aliases):
    return handle if handle in PEOPLE else aliases.get(handle)


def execute(ops):
    """Scalar reference interpreter, including snapshot aliases."""
    aliases = dict.fromkeys(ALIASES)
    owner = None
    for kind,a,b in ops:
        if kind == 'owner':
            owner = a
        elif kind == 'alias':
            aliases[a] = resolve(b,aliases)
        elif kind == 'revoke':
            aliases[a] = None
        elif kind == 'transfer':
            left,right=resolve(a,aliases),resolve(b,aliases)
            if left is not None and right is not None:
                if owner == left:
                    owner=right
                elif owner == right:
                    owner=left
        else:
            raise ValueError(kind)
    return owner


def execute_matrix(ops):
    """Independent one-hot operator implementation used by brute-force tests."""
    refs={person: np.eye(4,dtype=int)[:,i] for i,person in enumerate(PEOPLE)}
    refs.update({a: np.zeros(4,dtype=int) for a in ALIASES})
    state=np.zeros(4,dtype=int)
    for kind,a,b in ops:
        if kind=='owner':
            state=refs[a].copy()
        elif kind=='alias':
            refs[a]=refs[b].copy()
        elif kind=='revoke':
            refs[a]=np.zeros(4,dtype=int)
        elif kind=='transfer':
            u,v=refs[a],refs[b]
            if u.sum() and v.sum():
                delta=u-v
                state=(np.eye(4,dtype=int)-np.outer(delta,delta))@state
        else:
            raise ValueError(kind)
    return PEOPLE[int(state.argmax())]


def render(ops, answer, template):
    out=['<bos>']
    for kind,a,b in ops:
        if kind=='owner':
            variants=[f'the parcel belongs to {a} .',f'{a} owns the parcel now .',f'now the parcel belongs to {a} .']
        elif kind=='transfer':
            variants=[f'transfer ownership between {a} and {b} .',f'between {a} and {b} transfer ownership .',f'ownership transfer between {a} and {b} .']
        elif kind=='alias':
            variants=[f'alias {a} now means {b} .',f'now {a} means alias {b} .',f'now alias {a} means {b} .']
        elif kind=='revoke':
            variants=[f'revoke alias {a} now .',f'now revoke alias {a} .',f'alias {a} revoke now .']
        else:
            raise ValueError(kind)
        out.extend(variants[template].split())
    out.extend('who owns the parcel now ?'.split())
    out.append(answer)
    return out


def make_pairs(seed, count, split='train', min_ops=None, max_ops=None):
    """Data RNG contains no arm/objective/model seed calls."""
    if split not in SPLITS:
        raise ValueError(split)
    rng=np.random.default_rng(np.random.SeedSequence([int(seed), SPLIT_CODES[split], 90271]))
    low=24 if split in ('length','both') else 8
    high=32 if split in ('length','both') else 20
    low=low if min_ops is None else min_ops
    high=high if max_ops is None else max_ops
    if low<2 or high<low:
        raise ValueError('invalid operation range')
    pairs=[]
    for _ in range(count):
        n=int(rng.integers(low,high+1))
        template=2 if split in ('paraphrase','both') else int(rng.integers(2))
        initial=rng.choice(PEOPLE,2,replace=False).tolist()
        tail=[]
        for _ in range(n-1):
            r=rng.random()
            if r<0.65:
                # Mostly direct endpoints, with 30% alias references individually.
                endpoints=[str(rng.choice(ALIASES if rng.random()<0.30 else PEOPLE)) for _ in range(2)]
                tail.append(('transfer',*endpoints))
            elif r<0.90:
                tail.append(('alias',str(rng.choice(ALIASES)),str(rng.choice(PEOPLE if rng.random()<0.75 else ALIASES))))
            else:
                tail.append(('revoke',str(rng.choice(ALIASES)),''))
        ops=tuple(tuple([('owner',owner,'')]+tail) for owner in initial)
        answers=tuple(execute(op) for op in ops)
        assert answers[0]!=answers[1]
        pairs.append(Pair(ops,answers,template))
    return pairs


def pack(pairs, ctx=None):
    sequences=[render(ops,answer,p.template) for p in pairs for ops,answer in zip(p.ops,p.answers)]
    longest=max(len(seq)-1 for seq in sequences)
    ctx=longest if ctx is None else ctx
    if longest>ctx:
        raise ValueError(f'sequence {longest} exceeds context {ctx}')
    shape=(len(sequences),ctx)
    batch={'x':np.zeros(shape,np.int32),'y':np.zeros(shape,np.int32),
           'valid':np.zeros(shape,np.float32),'decision':np.zeros(shape,np.float32)}
    for i,seq in enumerate(sequences):
        ids=np.array([VOCAB[t] for t in seq],np.int32)
        n=len(ids)-1
        batch['x'][i,:n]=ids[:-1]
        batch['y'][i,:n]=ids[1:]
        batch['valid'][i,:n]=1
        batch['decision'][i,n-1]=1
    return batch


def batch_digest(batch):
    h=hashlib.sha256()
    for key in sorted(batch):
        h.update(key.encode());h.update(np.asarray(batch[key]).tobytes())
    return h.hexdigest()


def config(**kwargs):
    defaults=dict(d=64,layers=2,heads=4,ctx=240,mlp=128,qkv_conv=4,
                  gheads=2,gdim=4,group_nh=2,group_order=0,group_init='paired',
                  branch_scale=0.1,bf16=0,cap=0,causal=1,ablate='precision')
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def init_model(key,cfg,arm):
    keys=iter(jax.random.split(key,5+6*cfg.layers))
    p={'emb':jax.random.normal(next(keys),(len(TOKENS),cfg.d))*0.04,
       'out':lm.dense(next(keys),cfg.d,len(TOKENS)), 'norm':lm.ln_init(cfg.d),'layers':[]}
    for i in range(cfg.layers):
        layer={'n1':lm.ln_init(cfg.d),'n2':lm.ln_init(cfg.d),
               'qkv':lm.dense(next(keys),cfg.d,3*cfg.d),
               'o':lm.dense(next(keys),cfg.d,cfg.d,1/math.sqrt(2*cfg.layers)),
               'qkv_conv':bl.init_qkv_conv(next(keys),cfg.d,cfg.qkv_conv),
               'fc1':lm.dense(next(keys),cfg.d,cfg.mlp),
               'fc2':lm.dense(next(keys),cfg.mlp,cfg.d,1/math.sqrt(2*cfg.layers))}
        # Separate stream preserves ALL common weights across arms.
        if arm=='hybrid':
            layer['branch']=bl.init_layer(jax.random.fold_in(key,100+i),cfg,'prefix')
            layer['branch']['group_mix']*=cfg.branch_scale
        p['layers'].append(layer)
    return p


def sinusoidal(t,d):
    angle=jnp.arange(t,dtype=jnp.float32)[:,None]*jnp.exp(-math.log(10000)*jnp.arange(0,d,2)/d)[None,:]
    return jnp.stack((jnp.sin(angle),jnp.cos(angle)),-1).reshape(t,-1)[:,:d]


def forward(p,x,cfg,arm,ablate=False):
    hidden=p['emb'][x]+0.1*sinusoidal(x.shape[1],cfg.d)[None]
    for layer in p['layers']:
        z=lm.ln(layer['n1'],hidden)
        content=bl.content_attention(cfg,layer,z)[0]
        if arm=='hybrid' and not ablate:
            content=content+bl.apply_layer(cfg,layer['branch'],z,'prefix')
        hidden=hidden+content
        hidden=hidden+lm.lin(layer['fc2'],jax.nn.gelu(lm.lin(layer['fc1'],lm.ln(layer['n2'],hidden))))
    return lm.lin(p['out'],lm.ln(p['norm'],hidden))


def reduce_loss(loss,valid,decision,objective):
    if objective=='token':
        return (loss*valid).sum()/valid.sum()
    if objective=='decision':
        # Equal weight per final semantic decision; one per sequence here.
        return ((loss*decision).sum(-1)/jnp.maximum(decision.sum(-1),1)).mean()
    raise ValueError(objective)


def evaluate(params,pairs,cfg,arm,batch_pairs=16,ctx=240,ablate=False):
    @jax.jit
    def score(batch):
        logits=forward(params,batch['x'],cfg,arm,ablate)
        losses=optax.softmax_cross_entropy_with_integer_labels(logits,batch['y'])
        return losses,jnp.argmax(logits,-1)
    token_sum=decision_sum=other_sum=0.
    tokens=decisions=other=0.
    position_sum=np.zeros(ctx);position_count=np.zeros(ctx)
    correct=[];truth=[];predictions=[];initial_baseline=[];decision_losses=[]
    lengths=[]
    for start in range(0,len(pairs),batch_pairs):
        selected=pairs[start:start+batch_pairs]
        batch=pack(selected,ctx)
        loss,pred=score(batch)
        loss,pred=np.asarray(loss),np.asarray(pred)
        valid,dm=batch['valid'],batch['decision']
        token_sum+=float((loss*valid).sum());tokens+=float(valid.sum())
        decision_sum+=float((loss*dm).sum());decisions+=float(dm.sum())
        other_sum+=float((loss*(valid-dm)).sum());other+=float((valid-dm).sum())
        position_sum+=(loss*valid).sum(0);position_count+=valid.sum(0)
        ix=np.argmax(dm,axis=1)
        got=pred[np.arange(len(pred)),ix];wanted=batch['y'][np.arange(len(pred)),ix]
        predictions.extend(map(int,got));truth.extend(map(int,wanted));correct.extend((got==wanted).tolist())
        decision_losses.extend(map(float,loss[np.arange(len(loss)),ix]))
        for pair in selected:
            lengths.append(len(pair.ops[0]))
            initial_baseline.extend([a==ops[0][1] for a,ops in zip(pair.answers,pair.ops)])
    corr=np.array(correct).reshape(-1,2)
    # Every pair has one shared input edit and one differing answer token.
    labels={person:truth.count(VOCAB[person]) for person in PEOPLE}
    return {'paired_accuracy':float(corr.all(1).mean()),'accuracy':float(corr.mean()),
            'token_ce':token_sum/tokens,'decision_ce':decision_sum/decisions,'other_ce':other_sum/other,
            'p':decisions/tokens,'tokens':int(tokens),'decisions':int(decisions),'pairs':len(pairs),
            'per_position_loss_sum':position_sum.tolist(),'per_position_count':position_count.astype(int).tolist(),
            'label_counts':labels,'initial_owner_accuracy':float(np.mean(initial_baseline)),
            'initial_owner_paired_accuracy':float(np.array(initial_baseline).reshape(-1,2).all(1).mean()),
            'changed_operation_count':1,'changed_input_token_count':1,'changed_final_token_count':1,
            'mean_operations':float(np.mean(lengths)),'predictions':predictions,'targets':truth,
            'per_example_decision_ce':decision_losses}


def run(args):
    if args.batch%2:
        raise ValueError('--batch must be even, preserving pair adjacency')
    cfg=config(d=args.d,layers=args.layers,heads=args.heads,mlp=args.mlp,bf16=args.bf16)
    lm.MM=jnp.bfloat16 if args.bf16 else None
    params=init_model(jax.random.PRNGKey(args.seed),cfg,args.arm)
    warmup=min(100,max(1,args.steps//10))
    schedule=optax.warmup_cosine_decay_schedule(args.lr*0.1,args.lr,warmup,args.steps,end_value=args.lr*0.1)
    optimizer=optax.chain(optax.clip_by_global_norm(1.0),optax.adamw(schedule,weight_decay=0.01))
    state=optimizer.init(params)
    @jax.jit
    def step(params,state,batch):
        def objective(p):
            logits=forward(p,batch['x'],cfg,args.arm)
            loss=optax.softmax_cross_entropy_with_integer_labels(logits,batch['y'])
            return reduce_loss(loss,batch['valid'],batch['decision'],args.objective)
        loss,grad=jax.value_and_grad(objective)(params)
        updates,state=optimizer.update(grad,state,params)
        return optax.apply_updates(params,updates),state,loss
    train_ctx=args.train_max*7+16
    dataset_hash=hashlib.sha256()
    curve=[]
    start=time.monotonic();train_tokens=0
    fixed=make_pairs(100000+args.seed,args.overfit_pairs,'train',args.train_min,args.train_max) if args.overfit_pairs else None
    for i in range(args.steps):
        pairs=(fixed[(i*args.batch//2)%len(fixed):][:args.batch//2] if fixed else
               make_pairs(args.seed*10000000+i,args.batch//2,'train',args.train_min,args.train_max))
        if fixed and len(pairs)<args.batch//2:
            pairs=(pairs+fixed*((args.batch//2)//len(fixed)+1))[:args.batch//2]
        batch=pack(pairs,train_ctx)
        dataset_hash.update(bytes.fromhex(batch_digest(batch)))
        train_tokens+=int(batch['valid'].sum())
        params,state,loss=step(params,state,batch)
        if i==0 or (i+1)%args.log_every==0 or i+1==args.steps:
            value=float(loss)
            row={'step':i+1,'loss':value,'seconds':time.monotonic()-start,'tokens':train_tokens}
            curve.append(row)
            print(json.dumps({'progress':row,'arm':args.arm,'objective':args.objective,'seed':args.seed}),flush=True)
            if not math.isfinite(value):
                raise FloatingPointError('nonfinite training loss')
    train_seconds=time.monotonic()-start
    evaluation={}
    # Eval sample seeds are independent of training/model seed, paired across arms and seeds.
    for split in ('id','paraphrase','length','both'):
        pairs=make_pairs(args.eval_seed,args.eval_pairs,split)
        evaluation[split]=evaluate(params,pairs,cfg,args.arm,ctx=240)
    # Online-training distribution diagnostic, plus shortest registered length.
    evaluation['short']=evaluate(params,make_pairs(args.eval_seed+100,args.eval_pairs,'id',8,8),cfg,args.arm,ctx=240)
    evaluation['train_seen']=evaluate(params,pairs if fixed is None else fixed,cfg,args.arm,ctx=240) if fixed else evaluate(params,make_pairs(args.seed*10000000+args.steps-1,args.batch//2,'train',args.train_min,args.train_max),cfg,args.arm,ctx=240)
    if args.arm=='hybrid':
        evaluation['id_no_composition']=evaluate(params,make_pairs(args.eval_seed,args.eval_pairs,'id'),cfg,args.arm,ctx=240,ablate=True)
        evaluation['both_no_composition']=evaluate(params,make_pairs(args.eval_seed,args.eval_pairs,'both'),cfg,args.arm,ctx=240,ablate=True)
    result={'experiment':'dilution','arm':args.arm,'objective':args.objective,'seed':args.seed,
            'steps':args.steps,'batch':args.batch,'eval_seed':args.eval_seed,'lr':args.lr,'train_min':args.train_min,'train_max':args.train_max,
            'config':vars(cfg),'parameters':sum(x.size for x in jax.tree_util.tree_leaves(params)),
            'training_tokens':train_tokens,'training_padded_tokens':args.steps*args.batch*train_ctx,
            'training_data_sha256':dataset_hash.hexdigest(),'train_seconds':train_seconds,
            'seconds':time.monotonic()-start,'curve':curve,'evaluation':evaluation,
            'p_definition':'share of nonpadding next-token targets that are final semantic answers',
            'task_semantics':'reciprocal ownership transfers; snapshot aliases; overwrite and revoke aliases',
            'objective_definition':'all nonpadding tokens' if args.objective=='token' else 'mean CE per final semantic decision only',
            'overfit_pairs':args.overfit_pairs}
    if args.out:
        path=Path(args.out);path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(result)+'\n')
        if args.checkpoint:
            import pickle
            with path.with_suffix('.pkl').open('wb') as f:
                pickle.dump({'params':jax.device_get(params),'config':vars(cfg),'args':vars(args)},f)
    print(json.dumps(result),flush=True)
    return result


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--arm',choices=('softmax','hybrid'),required=True)
    ap.add_argument('--objective',choices=('token','decision'),required=True)
    ap.add_argument('--seed',type=int,default=0)
    ap.add_argument('--steps',type=int,default=1500)
    ap.add_argument('--batch',type=int,default=64)
    ap.add_argument('--eval-pairs',type=int,default=256)
    ap.add_argument('--eval-seed',type=int,default=73517)
    ap.add_argument('--d',type=int,default=64)
    ap.add_argument('--layers',type=int,default=2)
    ap.add_argument('--heads',type=int,default=4)
    ap.add_argument('--mlp',type=int,default=128)
    ap.add_argument('--lr',type=float,default=0.002)
    ap.add_argument('--bf16',type=int,default=0)
    ap.add_argument('--train-min',type=int,default=8)
    ap.add_argument('--train-max',type=int,default=20)
    ap.add_argument('--overfit-pairs',type=int,default=0)
    ap.add_argument('--log-every',type=int,default=250)
    ap.add_argument('--out',default=str(Path(os.environ['NEXT_ARTIFACT_DIR']) / 'result.json') if os.environ.get('NEXT_ARTIFACT_DIR') else '')
    ap.add_argument('--checkpoint',action='store_true',default=bool(os.environ.get('NEXT_ARTIFACT_DIR')))
    run(ap.parse_args())

if __name__=='__main__':
    main()
