"""QKV convolution integration proofs; run: python research/test_beyond_conv.py."""
import copy
from types import SimpleNamespace
import jax
import jax.numpy as jnp
import numpy as np
import lm
import beyond_layers as bl


def cfg(arch='gpt', **kw):
    values = dict(arch=arch,d=20,layers=2,heads=2,nheads=2,ctx=7,vocab=61,
                  mlp=40,rank=4,order=3,phase=2.,vac=.05,alpha0=2,cap=0.,fscale=1,
                  hops=1,lookback=0,lbdim=4,chart=3,chart_init=.5,lam0=1.,plx_norm=0,
                  pos=1,remat=0,gdim=5,gheads=2,group_nh=4,group_order=2,
                  group_init='random',branch_scale=.1,nh=4,conv_width=4,bf16=0,qkv_conv=3)
    values.update(kw)
    return SimpleNamespace(**values)


def close(a,b,tol=3e-5):
    error=float(jnp.max(jnp.abs(a-b)))
    assert error < tol, error

key=jax.random.key(105)
models={name:lm.init(key,cfg(name)) for name in lm.QKV_CONV_ARCHS}
raw=lm.init(key,cfg(qkv_conv=0))
for name,p in models.items():
    for layer,reference in zip(p['layers'],models['gpt']['layers']):
        np.testing.assert_array_equal(layer['qkv_conv'],reference['qkv_conv'])
        assert layer['qkv_conv'].shape==(3,60)
        assert float(jnp.max(jnp.abs(layer['qkv_conv'])))<=1/np.sqrt(3)
        for weight in ('qkv','o','fc1','fc2'):
            np.testing.assert_array_equal(layer[weight]['w'],reference[weight]['w'])
    for layer,reference in zip(p['layers'],raw['layers']):
        np.testing.assert_array_equal(layer['qkv']['w'],reference['qkv']['w'])
    actual=lm.flops_per_token(cfg(name),7)-lm.flops_per_token(cfg(name,qkv_conv=0),7)
    assert abs(actual-6*3*20*2)<1e-6,(name,actual)

x=jax.random.normal(jax.random.key(2),(2,7,20))
layer=models['gpt']['layers'][0]
packed=np.asarray(lm.lin(layer['qkv'],x))
expected=np.zeros_like(packed)
for t in range(7):
    for lag in range(min(2,t)+1):
        expected[:,t]+=packed[:,t-lag]*np.asarray(layer['qkv_conv'][lag])
close(jnp.concatenate(lm.project_qkv(layer,x),-1),expected)

ids=jax.random.randint(jax.random.key(6),(2,7),0,61)
changed=ids.at[:,4:].set((ids[:,4:]+9)%61)
for name,p in models.items():
    base=lm.forward(cfg(name),p,ids)
    close(base[:,:4],lm.forward(cfg(name),p,changed)[:,:4])
    assert bool(jnp.isfinite(base).all())
    grad=jax.grad(lambda pp:jnp.mean(lm.forward(cfg(name),pp,ids)**2))(p)
    assert bool(jnp.isfinite(grad['layers'][0]['qkv_conv']).all())
    assert float(jnp.linalg.norm(grad['layers'][0]['qkv_conv']))>0
close(lm.forward(cfg('plx'),models['plx'],ids),lm.forward(cfg('gpt'),models['gpt'],ids))
for name in ('beyond_a','beyond_b','beyond_c'):
    close(lm.forward(cfg(name,ablate='composition'),models[name],ids),lm.forward(cfg('plx'),models['plx'],ids))
    assert lm.flops_per_token(cfg(name,ablate='composition'),7)==lm.flops_per_token(cfg('plx'),7)

# Use nonzero rho so stats and candidate-content equivalence exercise precision.
p=copy.deepcopy(models['plx']['layers'][0])
p['wr']['w']=.02*jax.random.normal(jax.random.key(99),(20,20))
stats=[]
local=lm.local_attention(cfg('plx'),p,x,stats)
content,weights,values=bl.content_attention(cfg('beyond_b'),p,x)
close(local,content)
q,k,v=lm.project_qkv(p,x)
shape=lambda z:z.reshape(2,7,2,10).transpose(0,2,1,3)
q,k,v=map(shape,(q,k,v))
soft=jax.nn.softmax(jnp.where(jnp.tril(jnp.ones((7,7),bool)),q@k.swapaxes(-1,-2)/np.sqrt(10),-1e9),-1)
w=soft*(1-lm.plx_correction(cfg('plx'),p,x,k,soft))
y=w@v
ordinary=soft@v
expected_cor=jnp.mean(jnp.linalg.norm(y-ordinary,axis=-1)/(jnp.linalg.norm(ordinary,axis=-1)+1e-6))
close(stats[0]['cor'],expected_cor)
close(stats[0]['wmin'],w.min())
close(stats[0]['wmax'],w.max())
for c in (cfg('prefix'),cfg('gated_delta'),cfg('lla'),cfg(qkv_conv=-1),cfg(qkv_conv=1.5)):
    try:
        lm.init(key,c)
    except ValueError:
        pass
    else:
        raise AssertionError('invalid conv configuration was accepted')
print('PASS: shared init, no-common-weight drift, manual causal FIR, whole-model causality, gradients, Parallax probe consistency, reductions, exact FLOP increments, invalid configs')
