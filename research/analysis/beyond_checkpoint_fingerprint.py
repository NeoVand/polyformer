"""Download and fingerprint completed final checkpoints without opening pickle.

This preserves the exact inline Python payload used for the original seed-1
monitor. That monitor started before this helper existed and is not replaced
by this file. Its source was preserved from the executed command transcript
after execution began; the digest below is a retrospective source identity,
not a preregistered or contemporaneously recorded hash.

Later invocations reuse that implementation with explicit input/metadata
substitutions. They record both this helper's byte hash and the hash of the
resulting executed Python source. No downloaded content is executed. Only
Modal Volume listing/read operations are used; no App or Function is created.

Example, after a later final manifest is committed:

    python research/analysis/beyond_checkpoint_fingerprint.py \
      --manifest research/manifests/beyond_language_seed2.json \
      --output research/results/beyond_language_checkpoint_fingerprints_seed2.json \
      --checkpoint-root /tmp/beyond-checkpoints --wait

Without --wait, inspect currently settled results once and exit. --describe
prints the planned source identities without contacting Modal or writing files.
--legacy-source prints the exact original seed-1 payload.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


LEGACY_SEED1_MANIFEST_SHA256 = "885508c42fb45ae88553cc76089f95cb372e8f2e4d10cbfb7f1980bb1604c9e9"
LEGACY_SEED1_ARTIFACT = "research/results/beyond_language_checkpoint_fingerprints_seed1.json"
LEGACY_SEED1_INLINE_SOURCE = r"""from datetime import datetime,timezone
import hashlib,json,math,os,pathlib,shutil,subprocess,sys,time
import modal
root=pathlib.Path.cwd(); research=root/'research'
sys.path.insert(0,str(research/'analysis'))
import beyond_language_protocol as protocol
manifest_path=research/'manifests/beyond_language_seed1.json'
manifest_bytes=manifest_path.read_bytes(); manifest=json.loads(manifest_bytes)
plan_path=research/'results/beyond_language_plan.json'; plan=json.loads(plan_path.read_bytes())
artifact=research/'results/beyond_language_checkpoint_fingerprints_seed1.json'
checkpoint_root=pathlib.Path('/tmp/beyond-checkpoints')
arms=['rawS','convS','convP','B','GDN1','DP4']
volume=modal.Volume.from_name('polyformer-beyond-runs',create_if_missing=False)
def now(): return datetime.now(timezone.utc).isoformat()
def digest(x):
 if not isinstance(x,bytes): x=json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
 return hashlib.sha256(x).hexdigest()
def require(ok,message):
 if not ok: raise ValueError(message)
require(manifest['sha256']==digest({k:v for k,v in manifest.items() if k!='sha256'}),'manifest seal mismatch')
require(manifest['source_hashes']==plan['source_hashes'],'manifest/plan source mismatch')
require(len(manifest['jobs'])==len(arms),'unexpected seed-1 job count')
commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
committed=subprocess.check_output(['git','show',f'{commit}:research/manifests/beyond_language_seed1.json'])
require(committed==manifest_bytes,'seed-1 manifest is not committed at observed HEAD')
if artifact.exists():
 evidence=json.loads(artifact.read_bytes())
 require(evidence['sha256']==digest({k:v for k,v in evidence.items() if k!='sha256'}),'existing fingerprint seal mismatch')
 require(evidence['manifest_sha256']==manifest['sha256'],'existing fingerprint names another manifest')
else:
 evidence={'schema':'beyond_language_checkpoint_fingerprints','schema_version':1,'seed':1,'status':'pending',
  'method':'Local control-plane Modal Volume.iterdir/read_file; streamed SHA-256 plus local readback SHA-256; no pickle deserialization, Modal Function, App or GPU execution.',
  'manifest_path':'research/manifests/beyond_language_seed1.json','manifest_sha256':manifest['sha256'],
  'manifest_file_sha256':digest(manifest_bytes),'manifest_observed_commit':commit,
  'plan_sha256':plan['sha256'],'source_hashes':manifest['source_hashes'],
  'volume_name':'polyformer-beyond-runs','checkpoint_root':str(checkpoint_root),
  'started_utc':now(),'last_updated_utc':now(),'completed_utc':None,
  'disk_before_bytes':dict(zip(('total','used','free'),shutil.disk_usage(checkpoint_root.parent))),
  'runtime':{'python':sys.version,'modal':modal.__version__},'jobs':{},
  'limitations':['Source result identity, completion counters and checkpoint metadata are validated; loss values are not inspected or used by this checkpoint-only audit.',
   'The worker records checkpoint size but no original content digest. These hashes fingerprint the subsequently retrieved persisted bytes.',
   'Pre/post size and mtime agreement is checked; the volume is not an immutable atomic snapshot.',
   'Pickle payloads are never deserialized; model semantics are not checked by this fingerprint.']}
def save():
 evidence['last_updated_utc']=now()
 evidence['disk_current_bytes']=dict(zip(('total','used','free'),shutil.disk_usage(checkpoint_root.parent)))
 evidence['sha256']=digest({k:v for k,v in evidence.items() if k!='sha256'})
 with artifact.open('w') as f:
  f.write(json.dumps(evidence,sort_keys=True,indent=2,allow_nan=False)+'\n');f.flush();os.fsync(f.fileno())
def snapshot(job_id):
 path=f'{job_id}/final.pkl'
 rows=[e for e in volume.iterdir(job_id,recursive=False) if e.path.lstrip('/')==path]
 require(len(rows)==1,'persisted final.pkl missing or ambiguous')
 e=rows[0]
 return {'volume_path':e.path.lstrip('/'),'bytes':int(e.size),'modified_unix':int(e.mtime),'modified_utc':datetime.fromtimestamp(e.mtime,timezone.utc).isoformat()}
def file_hash(path):
 h=hashlib.sha256();size=0
 with path.open('rb') as f:
  while block:=f.read(8*1024*1024): h.update(block);size+=len(block)
 return h.hexdigest(),size
save()
while True:
 for arm,job in zip(arms,manifest['jobs']):
  jid=job['id']
  if evidence['jobs'].get(jid,{}).get('status')=='complete': continue
  rp=research/'results/beyond_runs'/f'{jid}.json'
  if not rp.is_file(): continue
  rb=rp.read_bytes();result=json.loads(rb)
  args=dict(zip(job['argv'][::2],job['argv'][1::2]))
  cfg=protocol.expected_config(plan,arm,'final',float(args['--lr']),1)
  try:
   require(not protocol.is_failure(result),'terminal result has explicit failure/nonfinite marker; no checkpoint admitted')
   protocol.validate_result_identity(plan,job,result,cfg)
   require(result.get('manifest_sha256')==manifest['sha256'] and result.get('manifest')==manifest['name'],'result manifest mismatch')
   require(result.get('prediction_commit')==manifest['prediction_commit'],'prediction commit mismatch')
   require(result.get('stage')=='language','result stage mismatch')
   require(result.get('curve') and result['curve'][-1].get('step')==cfg['steps'],'final update count mismatch')
   info=plan['arms'][arm];tokens=cfg['steps']*cfg['batch']*cfg['ctx']
   require(result.get('tokens')==tokens==info['main_tokens'],'final token count mismatch')
   require(result.get('flops_per_token')==info['forward_fpt'] and result.get('train_flops_per_token')==info['training_fpt'],'per-token compute mismatch')
   require(math.isclose(result.get('train_flops',-1),info['main_training_flops'],rel_tol=1e-12),'final compute mismatch')
   cp=result.get('checkpoint',{});size=cp.get('bytes')
   require(cp.get('schema')==1 and cp.get('path')==f'/runs/{jid}/final.pkl','checkpoint metadata identity mismatch')
   require(isinstance(size,int) and not isinstance(size,bool) and size>0,'invalid checkpoint expected size')
   entries=[a for a in result.get('artifacts',[]) if a.get('name')=='final.pkl']
   require(len(entries)==1 and entries[0].get('bytes')==size,'worker artifact listing does not match checkpoint metadata')
   require(result.get('log_volume')=='polyformer-beyond-runs' and result.get('log_directory')==jid,'worker volume identity mismatch')
   before=snapshot(jid);require(before['bytes']==size,'persisted checkpoint size differs from result')
   require(shutil.disk_usage(checkpoint_root.parent).free>size*2+1024**3,'insufficient local free disk space')
   evidence['volume_object_id']=volume.object_id
   dest=checkpoint_root/jid/'final.pkl';dest.parent.mkdir(parents=True,exist_ok=True)
   require(not dest.exists(),'local checkpoint exists without completed evidence; refusing silent replacement')
   started=now();start=time.monotonic();h=hashlib.sha256();count=0
   print(json.dumps({'event':'download_started','arm':arm,'job_id':jid,'bytes':size,'utc':started}),flush=True)
   with dest.open('xb') as out:
    for chunk in volume.read_file(before['volume_path']):
     out.write(chunk);h.update(chunk);count+=len(chunk)
     require(count<=size,'download exceeds expected checkpoint size')
    out.flush();os.fsync(out.fileno())
   require(count==size,'download truncated')
   after=snapshot(jid);require(after==before,'persisted checkpoint size/mtime changed during download')
   local_hash,local_size=file_hash(dest)
   require(local_size==size and local_hash==h.hexdigest(),'local readback differs from downloaded stream')
   require(rp.read_bytes()==rb,'source result changed during checkpoint fingerprint')
   evidence['jobs'][jid]={'status':'complete','arm':arm,'seed':1,'job_id':jid,
    'source_result_path':str(rp.relative_to(root)),'source_result_file_sha256':digest(rb),
    'source_result_file_bytes':len(rb),'source_result_remote_completed_at':result.get('remote_completed_at'),
    'manifest_sha256':manifest['sha256'],'source_hashes':result['source_hashes'],
    'terminal_metadata_validation':{'status':'passed','steps':cfg['steps'],'tokens':tokens,
      'config_sha256':digest(result['config']),'runtime_versions':result['installed_versions'],
      'no_explicit_failure_or_nonfinite_marker':True,'quality_values_inspected':False},
    'checkpoint_schema':cp['schema'],'worker_path':cp['path'],'expected_bytes':size,
    'volume_name':'polyformer-beyond-runs','volume_object_id':volume.object_id,'volume_path':before['volume_path'],
    'volume_metadata_before':before,'volume_metadata_after':after,'volume_metadata_stable':True,
    'local_path':str(dest),'local_bytes':local_size,'local_sha256':local_hash,'stream_sha256':h.hexdigest(),
    'local_readback_matches_stream':True,'pickle_deserialized':False,
    'download_started_utc':started,'fingerprinted_utc':now(),'elapsed_seconds':round(time.monotonic()-start,3)}
   save();print(json.dumps({'event':'checkpoint_complete','arm':arm,'job_id':jid,'bytes':local_size,'sha256':local_hash,'completed':len(evidence['jobs'])}),flush=True)
  except Exception as e:
   evidence['status']='attention_required';evidence['issue']={'arm':arm,'job_id':jid,'utc':now(),'reason':str(e)};save()
   print(json.dumps({'event':'attention_required',**evidence['issue']}),flush=True);raise
 if len(evidence['jobs'])==len(arms):
  evidence['status']='complete';evidence['completed_utc']=now();save()
  print(json.dumps({'event':'all_complete','artifact':str(artifact.relative_to(root)),'sha256':evidence['sha256'],'checkpoints':len(evidence['jobs'])}),flush=True);break
 print(json.dumps({'event':'waiting','completed':len(evidence['jobs']),'remaining':[a for a,j in zip(arms,manifest['jobs']) if j['id'] not in evidence['jobs']],'utc':now()}),flush=True)
 time.sleep(60)
"""
LEGACY_SEED1_INLINE_SHA256 = hashlib.sha256(
    LEGACY_SEED1_INLINE_SOURCE.encode()
).hexdigest()


def arm_for(job):
    argv = job["argv"]
    if len(argv) % 2:
        raise ValueError("expected the frozen paired flag/value argv")
    cfg = dict(zip(argv[::2], argv[1::2]))
    arch = cfg["--arch"]
    if arch == "gpt":
        return "rawS" if int(cfg["--qkv_conv"]) == 0 else "convS"
    if arch == "plx":
        return "convP"
    if arch in ("beyond_a", "beyond_b", "beyond_c"):
        return arch[-1].upper()
    if arch == "gated_delta" and cfg["--nh"] in ("1", "4"):
        return {"1": "GDN1", "4": "DP4"}[cfg["--nh"]]
    raise ValueError(f"unknown final arm: {arch}")


def build_source(args):
    root = args.repository.resolve()
    manifest_path = args.manifest.resolve()
    output = args.output.resolve()
    manifest_relative = manifest_path.relative_to(root).as_posix()
    output.relative_to(root)
    manifest = json.loads(manifest_path.read_bytes())
    jobs = manifest["jobs"]
    seeds = {int(j["argv"][j["argv"].index("--seed") + 1]) for j in jobs}
    if len(seeds) != 1:
        raise ValueError("each checkpoint collection must contain exactly one seed")
    seed = seeds.pop()
    if seed not in (1, 2, 3) or manifest.get("stage") != "language":
        raise ValueError("expected a final language seed 1, 2, or 3")
    arms = [arm_for(j) for j in jobs]
    if len(set(arms)) != len(arms):
        raise ValueError("duplicate arm in final manifest")
    if args.poll_seconds <= 0 or args.poll_seconds > 60:
        raise ValueError("poll-seconds must be positive and at most 60")
    substitutions = [
        ("root=pathlib.Path.cwd(); research=root/'research'",
         f"root=pathlib.Path({str(root)!r}); research=root/'research'"),
        ("manifest_path=research/'manifests/beyond_language_seed1.json'",
         f"manifest_path=pathlib.Path({str(manifest_path)!r})"),
        ("plan_path=research/'results/beyond_language_plan.json'; plan=json.loads(plan_path.read_bytes())",
         f"plan_path=pathlib.Path({str(args.plan.resolve())!r}); plan=json.loads(plan_path.read_bytes())"),
        ("artifact=research/'results/beyond_language_checkpoint_fingerprints_seed1.json'",
         f"artifact=pathlib.Path({str(output)!r})"),
        ("checkpoint_root=pathlib.Path('/tmp/beyond-checkpoints')",
         f"checkpoint_root=pathlib.Path({str(args.checkpoint_root.resolve())!r})"),
        ("arms=['rawS','convS','convP','B','GDN1','DP4']", f"arms={arms!r}"),
        ("f'{commit}:research/manifests/beyond_language_seed1.json'",
         f"f'{{commit}}:{manifest_relative}'"),
        ("'manifest_path':'research/manifests/beyond_language_seed1.json'",
         f"'manifest_path':{manifest_relative!r}"),
        ("protocol.expected_config(plan,arm,'final',float(args['--lr']),1)",
         f"protocol.expected_config(plan,arm,'final',float(args['--lr']),{seed})"),
        ("'seed':1", f"'seed':{seed}"),
        ("'unexpected seed-1 job count'", "'unexpected final job count'"),
        ("'seed-1 manifest is not committed at observed HEAD'",
         "'final manifest is not committed at observed HEAD'"),
        (" time.sleep(60)",
         f" if not {args.wait!r}: break\n time.sleep({args.poll_seconds!r})"),
    ]
    source = LEGACY_SEED1_INLINE_SOURCE
    for old, new in substitutions:
        expected = 2 if old == "'seed':1" else 1
        if source.count(old) != expected:
            raise ValueError(f"legacy source substitution is ambiguous: {old}")
        source = source.replace(old, new)
    source = source.replace(
        " require(evidence['manifest_sha256']==manifest['sha256'],'existing fingerprint names another manifest')",
        " require(evidence['manifest_sha256']==manifest['sha256'],'existing fingerprint names another manifest')\n"
        " require(evidence.get('collector')==COLLECTOR_PROVENANCE,'existing evidence was produced by a different collector source; preserve it separately')",
        1,
    )
    source = source.replace(
        "def save():\n",
        "evidence['collector']=COLLECTOR_PROVENANCE\n"
        "artifact.parent.mkdir(parents=True,exist_ok=True)\n"
        "def save():\n",
        1,
    )
    compile(source, "<beyond-checkpoint-collector>", "exec")
    provenance = {
        "helper_path": str(Path(__file__).resolve().relative_to(root)),
        "helper_file_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "executed_source_sha256": hashlib.sha256(source.encode()).hexdigest(),
        "legacy_seed1_inline_source_sha256": LEGACY_SEED1_INLINE_SHA256,
        "legacy_seed1_manifest_sha256": LEGACY_SEED1_MANIFEST_SHA256,
        "legacy_source_preservation": (
            "Exact original inline payload preserved from the executed command transcript "
            "after seed-1 execution began; not a contemporaneously recorded source hash. "
            "The original seed-1 artifact is not rewritten or attributed to this helper."
        ),
        "changes_from_legacy": (
            "CLI paths, manifest-derived arm identities and seed, optional once-only polling, "
            "output-directory creation, and explicit collector-source metadata/resume checks. "
            "Checkpoint validation, download, streaming/local hashes and metadata checks are unchanged."
        ),
    }
    return source, provenance


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--plan", type=Path, default=Path("research/results/beyond_language_plan.json"))
    parser.add_argument("--checkpoint-root", type=Path, default=Path("/tmp/beyond-checkpoints"))
    parser.add_argument("--wait", action="store_true")
    parser.add_argument("--poll-seconds", type=float, default=60)
    parser.add_argument("--describe", action="store_true")
    parser.add_argument("--legacy-source", action="store_true")
    args = parser.parse_args()
    if args.legacy_source:
        print(LEGACY_SEED1_INLINE_SOURCE, end="")
        return
    if args.manifest is None or args.output is None:
        parser.error("--manifest and --output are required unless --legacy-source is used")
    source, provenance = build_source(args)
    if args.describe:
        print(json.dumps(provenance, sort_keys=True, indent=2))
        return
    exec(compile(source, "<beyond-checkpoint-collector>", "exec"),
         {"__name__": "__main__", "COLLECTOR_PROVENANCE": provenance})


if __name__ == "__main__":
    main()
