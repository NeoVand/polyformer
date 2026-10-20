"""Portable CPU proof of the reporting-only LM patch.

Run with the project's JAX/Optax Python environment:
    python research/analysis/test_beyond_lm_reporting.py

Recovers the frozen LM and its layer dependency from Git, applies the saved
patch inside a TemporaryDirectory, and checks arithmetic, APIs, and unchanged
training. It writes only the requested proof JSON; no live Python source changes.
"""
import argparse
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import pickle
import subprocess
import sys
import tempfile
from types import SimpleNamespace

# This is an offline CPU proof, including the two child CLI executions.
os.environ["JAX_PLATFORMS"] = "cpu"
import jax
import jax.numpy as jnp
import numpy as np
import optax

BASE_COMMIT = "c65001b1297089447f59650e7570f451f09018a7"
BASE_LM_SHA256 = "f962a571b97835b4243d8685c39d7830bd3ce7a4ebadc21d45a70936898ebab5"


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def cfg(arch='beyond_b',**kw):
    values=dict(arch=arch,d=20,layers=1,heads=2,nheads=2,ctx=7,vocab=61,
                mlp=40,rank=4,order=3,phase=2.,vac=.05,alpha0=2,cap=0.,fscale=1,
                hops=1,lookback=0,lbdim=4,chart=3,chart_init=.5,lam0=1.,plx_norm=0,
                pos=1,remat=0,gdim=5,gheads=2,group_nh=4,group_order=2,
                group_init='random',branch_scale=.1,nh=4,conv_width=4,bf16=0,
                qkv_conv=3,ablate='none',progress=0,seed=0)
    values.update(kw)
    return SimpleNamespace(**values)


def run_tests(base_path, patched_path, patch_path, dependency_path, workspace):
    old = load("lm_reporting_old", base_path)
    new = load("lm_reporting_new", patched_path)
    proof={'status':'running','cases':{},'training_source_audit':{}}
    # Verify all architecture/training functions have identical Python ASTs.
    oldtree=ast.parse(base_path.read_text())
    newtree=ast.parse(patched_path.read_text())
    oldnodes={n.name:n for n in oldtree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
    newnodes={n.name:n for n in newtree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
    changed=[]
    for name,node in oldnodes.items():
        if ast.dump(node,include_attributes=False)!=ast.dump(newnodes[name],include_attributes=False):
            changed.append(name)
    assert changed==['final_ablation_losses','main'], changed
    assert set(newnodes)-set(oldnodes)=={'final_loss_statistics'}
    for name in ('loss_fn','step','poslosses','batch'):
        select=lambda tree:next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name==name)
        assert ast.dump(select(oldnodes['main']),include_attributes=False)==ast.dump(select(newnodes['main']),include_attributes=False),name
    proof['training_source_audit']={'changed_existing_functions':changed,'added_functions':['final_loss_statistics'],
        'identical_nested_functions':['loss_fn','step','poslosses','batch'],
        'all_other_module_functions_identical':True}

    rng=np.random.default_rng(42)
    x=rng.integers(0,61,(11,7),dtype=np.int32)
    y=rng.integers(0,61,(11,7),dtype=np.int32)
    for arch in ('gpt','beyond_b','beyond_c'):
        config=cfg(arch)
        p=old.init(jax.random.key(9),config)
        np.testing.assert_array_equal(old.forward(config,p,x),new.forward(config,p,x))
        @jax.jit
        def legacy_pos(p,x,y):
            return optax.softmax_cross_entropy_with_integer_labels(old.forward(config,p,x),y).sum(0)
        legacy_total=sum(float(np.asarray(legacy_pos(p,x[i:i+4],y[i:i+4])).sum()) for i in range(0,len(x),4))
        legacy_raw=legacy_total/(x.shape[0]*x.shape[1])
        got=new.final_loss_statistics(config,p,x,y,4)
        assert got['loss']==round(legacy_raw,5)
        assert abs(got['loss_raw']-legacy_raw)<1e-7,(arch,got['loss_raw'],legacy_raw)
        manual=np.asarray(optax.softmax_cross_entropy_with_integer_labels(new.forward(config,p,x),y)).mean(-1)
        np.testing.assert_allclose(got['sequence_losses'],manual,rtol=2e-6,atol=2e-6)
        discrepancy=abs(got['loss_raw']-got['sequence_mean_raw'])
        assert discrepancy<2e-6
        default_old=old.final_ablation_losses(config,p,x,y,4)
        default_new=new.final_ablation_losses(config,p,x,y,4)
        assert default_old==default_new,(arch,default_old,default_new)
        details=new.final_ablation_losses(config,p,x,y,4,return_details=True)
        assert default_new=={name:row['loss'] for name,row in details.items()}
        for mode,row in details.items():
            assert len(row['sequence_losses'])==len(x)
            np.testing.assert_allclose(np.mean(row['sequence_losses']),row['loss_raw'],rtol=0,atol=2e-6)
            diffs=np.asarray(row['sequence_losses'])-got['sequence_losses']
            assert abs(float(diffs.mean())-(row['loss_raw']-got['loss_raw']))<3e-6
        # One training update is identical, including gradients and optimizer state.
        loss=lambda module,p: optax.softmax_cross_entropy_with_integer_labels(module.forward(config,p,x),y).mean()
        oldloss,oldgrad=jax.value_and_grad(lambda pp:loss(old,pp))(p)
        newloss,newgrad=jax.value_and_grad(lambda pp:loss(new,pp))(p)
        np.testing.assert_array_equal(oldloss,newloss)
        for a,b in zip(jax.tree_util.tree_leaves(oldgrad),jax.tree_util.tree_leaves(newgrad)):
            np.testing.assert_array_equal(a,b)
        optimizer=old.make_opt('adamw',.001)
        state=optimizer.init(p)
        u0,s0=optimizer.update(oldgrad,state,p)
        u1,s1=optimizer.update(newgrad,state,p)
        for a,b in zip(jax.tree_util.tree_leaves((optax.apply_updates(p,u0),s0)),jax.tree_util.tree_leaves((optax.apply_updates(p,u1),s1))):
            np.testing.assert_array_equal(a,b)
        proof['cases'][arch]={'legacy_loss_raw':legacy_raw,'new_loss_raw':got['loss_raw'],
            'raw_vs_sequence_mean_abs':discrepancy,'sequence_count':len(x),
            'partial_batch':True,'ablation_modes':list(details),'unchanged_forward_gradient_update':True}
        print(json.dumps({'case':arch,'pass':True}),flush=True)

    # Run the actual CLI in both versions and compare final trained parameters.
    folder=workspace/'integration'
    folder.mkdir(exist_ok=True)
    for name,size in (('train',3000),('val',2000)):
        rng.integers(0,64,size,dtype=np.uint16).tofile(folder/(name+'.bin'))
    for arch in ('gpt','beyond_b'):
        outputs=[]
        checkpoints=[]
        for version,script in (('old',base_path),('new',patched_path)):
            artifact=folder/(arch+'-'+version)
            artifact.mkdir(exist_ok=True)
            env={**os.environ,'PYTHONPATH':str(dependency_path.parent),'BEYOND_ARTIFACT_DIR':str(artifact)}
            argv=[sys.executable,script,'--arch',arch,'--data',str(folder),'--vocab','64',
                  '--ctx','8','--d','24','--heads','2','--layers','1','--mlp','48',
                  '--steps','3','--batch','2','--micro','1','--evals','1','--vseqs','5',
                  '--vbig',('1024' if arch=='beyond_b' else '11'),
                  '--ablations',('1' if arch=='beyond_b' else '0'),
                  '--opt','adamw','--lr','.001','--warmup','1','--bf16','0',
                  '--qkv_conv','3','--group_init','random','--save-final','1']
            run=subprocess.run(argv,env=env,capture_output=True,text=True,check=True)
            output=json.loads(run.stdout.splitlines()[-1])
            outputs.append(output)
            with (artifact/'final.pkl').open('rb') as file:
                checkpoints.append(pickle.load(file))
        left,right=outputs
        for a,b in zip(jax.tree_util.tree_leaves(checkpoints[0]['params']),jax.tree_util.tree_leaves(checkpoints[1]['params'])):
            np.testing.assert_array_equal(a,b)
        for field in ('val_loss','val_big','tokens','train_flops','steps','lr','params'):
            assert left[field]==right[field],(arch,field,left[field],right[field])
        assert right['val_loss_raw']==right['curve'][-1]['val_raw']
        assert round(right['val_loss_raw'],4)==right['val_loss']
        assert round(right['val_big_raw'],5)==right['val_big']
        assert len(right['val_big_sequence_losses'])==right['val_big_sample']['sequences']
        assert abs(np.mean(right['val_big_sequence_losses'])-right['val_big_raw'])<2e-6
        if arch=='beyond_b':
            assert left['ablation_val_big']==right['ablation_val_big']
            assert left['ablation_delta_val_big']==right['ablation_delta_val_big']
            for mode in ('composition','precision'):
                assert len(right['ablation_val_big_sequence_losses'][mode])==1024
                np.testing.assert_array_equal(np.asarray(right['ablation_val_big_sequence_losses'][mode])-right['val_big_sequence_losses'],right['ablation_delta_val_big_sequence_losses'][mode])
                assert right['ablation_delta_val_big_raw'][mode]==right['ablation_val_big_raw'][mode]-right['val_big_raw']
        (folder/(arch+'-report.json')).write_text(json.dumps(right,indent=2)+'\n')
        proof['cases'][arch+'_cli']={'identical_final_parameters':True,'identical_legacy_metrics':True,
            'final_sequences':len(right['val_big_sequence_losses']),'train_steps':3,
            'raw_vs_sequence_mean_abs':abs(right['val_big_raw']-right['val_big_sequence_mean_raw'])}
        print(json.dumps({'case':arch+'_cli','pass':True}),flush=True)

    paths = {"old_lm": base_path, "new_lm": patched_path, "patch": patch_path,
             "beyond_layers": dependency_path, "test": Path(__file__)}
    proof.update(
        status="pass", backend=jax.default_backend(), base_commit=BASE_COMMIT,
        versions={"python": sys.version.split()[0], "jax": jax.__version__,
                  "numpy": np.__version__, "optax": optax.__version__},
        source_sha256={name: hashlib.sha256(path.read_bytes()).hexdigest()
                       for name, path in paths.items()},
        bridge_note="Only final/reporting paths change. No layer, initializer, optimizer, sampler, gradient, update, model setting, or FLOP count changes. The Stage1 runner does not call the changed LM main or final-report functions.",
        reduction_note="Legacy scalar reduction order and rounded keys are retained. Additional JIT outputs can change floating-point rounding. Sequence means come from the same forward pass; the proof measures the scalar-versus-sequence reduction discrepancy.",
        reproduction={"command": "python research/analysis/test_beyond_lm_reporting.py",
                      "source_recovery": "git show <base_commit>:research/{lm,beyond_layers}.py",
                      "patch": "research/results/beyond_reporting_patch/lm.patch",
                      "temporary_files": "TemporaryDirectory, removed automatically"},
    )
    return proof


def main():
    worktree = Path(__file__).resolve().parents[2]
    result_dir = worktree / "research/results/beyond_reporting_patch"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=result_dir / "stage0.json")
    args = parser.parse_args()
    patch_path = result_dir / "lm.patch"

    def git_source(name):
        return subprocess.check_output(
            ["git", "show", f"{BASE_COMMIT}:research/{name}"], cwd=worktree,
        )

    baseline = git_source("lm.py")
    if hashlib.sha256(baseline).hexdigest() != BASE_LM_SHA256:
        raise AssertionError("the frozen baseline source does not match its registered hash")
    with tempfile.TemporaryDirectory(prefix="beyond-reporting-proof-") as directory:
        workspace = Path(directory)
        base_path = workspace / "baseline_lm.py"
        base_path.write_bytes(baseline)
        patch_root = workspace / "patched"
        (patch_root / "research").mkdir(parents=True)
        patched_path = patch_root / "research/lm.py"
        patched_path.write_bytes(baseline)
        # git apply works outside a repository, against only these temporary files.
        subprocess.run(["git", "apply", "--check", str(patch_path)], cwd=patch_root, check=True)
        subprocess.run(["git", "apply", str(patch_path)], cwd=patch_root, check=True)
        dependency_path = workspace / "support/beyond_layers.py"
        dependency_path.parent.mkdir()
        dependency_path.write_bytes(git_source("beyond_layers.py"))
        sys.path.insert(0, str(dependency_path.parent))
        previous = sys.modules.pop("beyond_layers", None)
        try:
            proof = run_tests(base_path, patched_path, patch_path, dependency_path, workspace)
        finally:
            sys.path.remove(str(dependency_path.parent))
            sys.modules.pop("beyond_layers", None)
            if previous is not None:
                sys.modules["beyond_layers"] = previous
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(proof, indent=2, allow_nan=False) + "\n")
    print(json.dumps(proof, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
