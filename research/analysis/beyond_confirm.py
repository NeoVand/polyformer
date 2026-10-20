"""Read-only BEYOND artifact integrity and final-test confirmation evaluator.

Run with /tmp/beyond-venv/bin/python from the worktree. No research files are
written, no model is trained, and no Modal client is imported.

  ... research/analysis/beyond_confirm.py audit-initial --manifest NAME --output /tmp/audit.json \
      --select-output /tmp/selected.json --alternates-output /tmp/alternates.json
  ... research/analysis/beyond_confirm.py confirm --selection /tmp/selected.json \
      --manifest REFERENCES --manifest CANDIDATE --output /tmp/stage1-confirmation.json
  ... research/analysis/beyond_confirm.py self-test
"""
import argparse
import copy
import hashlib
import importlib
import json
import math
import pathlib
import sys
import tempfile

DEFAULT_RESEARCH = pathlib.Path(__file__).resolve().parents[1]
EPS = 1e-12


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def same_number(a, b):
    return finite(a) and math.isclose(a, b, rel_tol=1e-10, abs_tol=1e-7)


def modules(research_dir):
    research = pathlib.Path(research_dir).resolve()
    if str(research) not in sys.path:
        sys.path.insert(0, str(research))
    protocol = importlib.import_module('beyond_protocol')
    diagnostic = importlib.import_module('beyond_diag')
    if pathlib.Path(protocol.__file__).resolve().parent != research:
        raise ValueError('another research directory is already imported')
    return protocol, diagnostic


def verify_json_hash(document, label):
    if not isinstance(document, dict) or 'sha256' not in document:
        raise ValueError(f'{label} is missing a canonical sha256')
    if digest({k: v for k, v in document.items() if k != 'sha256'}) != document['sha256']:
        raise ValueError(f'{label} canonical sha256 mismatch')


def current_sources(research, names):
    return {n: hashlib.sha256((research / n).read_bytes()).hexdigest() for n in names}


def read_manifests(names, research, p, expected_sources=None):
    records, sources, seen = [], expected_sources, {}
    for name in names:
        path = pathlib.Path(name)
        if not path.exists():
            path = research / 'manifests' / (path.stem + '.json')
        manifest = json.loads(path.read_text())
        verify_json_hash(manifest, str(path))
        identity = {n: manifest.get('source_hashes', {}).get(n) for n in p.MODEL_SOURCES}
        if not all(identity.values()):
            raise ValueError(f'{path}: missing model/data source hash')
        if sources is not None and identity != sources:
            raise ValueError(f'{path}: model/data source identity differs')
        sources = identity
        for job in manifest['jobs']:
            bound = {k: job[k] for k in ('script', 'argv', 'gpu', 'attempt')}
            bound['source_hashes'] = manifest['source_hashes']
            if digest(bound)[:24] != job['id']:
                raise ValueError(f'{path}: job ID does not bind its arguments and source hashes')
            if job['id'] in seen:
                if seen[job['id']] != job:
                    raise ValueError('duplicate job ID has different manifest metadata')
                continue
            seen[job['id']] = job
            records.append((manifest, job))
    sources = sources or {}
    if sources and current_sources(research, p.MODEL_SOURCES) != sources:
        raise ValueError('live model/data sources differ from the frozen experiment; cannot validate its counter')
    return records, sources


def expected_run(job, p, bd):
    args, settings = p.parse_argv(job['argv'])
    ns = argparse.Namespace(**args)
    ns.set = list(settings.items())
    _, context, vocab, pos, _ = bd.TASKS[args['task']]
    cfg = bd.model_config(ns, context, vocab, pos)
    steps, fpt, _ = bd.compute_budget(cfg, context, args['steps'], [], args['task'] == 'regression', args['target_fpt'])
    return args, vars(cfg), context, steps, fpt


def audit_result(manifest, job, result, p, bd):
    """Artifact-integrity audit. Failed/partial runs may be valid artifacts.

    It never uses a held-out quality score to accept or reject primary tuning.
    A terminal numerical failure is left to the frozen planner's invalid-run
    rule; an identity or accounting mismatch prevents selection entirely.
    """
    report = {'job_id': job['id'], 'manifest': manifest['name'], 'status': 'pending', 'errors': []}
    if result is None:
        return report
    errors = report['errors']
    if not isinstance(result, dict):
        report.update(status='integrity_invalid', errors=['result is not an object'])
        return report
    for key, expected in (('job_id', job['id']), ('argv', job['argv']),
                          ('source_hashes', manifest['source_hashes']), ('script', job['script'])):
        if result.get(key) != expected:
            errors.append(f'{key} differs from manifest')
    for key, expected in (('manifest', manifest['name']), ('manifest_sha256', manifest['sha256'])):
        if key in result and result[key] != expected:
            errors.append(f'{key} differs from manifest')
    args, cfg, context, planned_steps, fpt = expected_run(job, p, bd)
    failed = bool(result.get('error') or result.get('failure') or result.get('nonfinite_fields'))
    if 'source hash mismatch' in str(result.get('error', '')).lower():
        errors.append('worker reported a source hash mismatch')
    if 'source_sha256' in result:
        actual = result['source_sha256']
        if not isinstance(actual, dict) or any(actual.get(n) != manifest['source_hashes'][n] for n in p.MODEL_SOURCES):
            errors.append('worker model/data source_sha256 differs from manifest')
    elif not failed:
        errors.append('successful result has no worker source_sha256')
    exact = {
        'seed': args['seed'], 'task': args['task'], 'layers': args['layers'],
        'arch': args['arch'], 'model': args['arch'], 'opt': args['opt'],
        'batch': args['batch'], 'reference_steps': args['steps'],
        'evalset': args['evalset'], 'testset': args['testset'],
        'validation_seed': 10000 + args['seed'], 'test_seed': 20000 + args['seed'],
    }
    required = set(exact) - {'model'}
    for key, expected in exact.items():
        if key in result and result[key] != expected:
            errors.append(f'{key}={result[key]!r}, expected {expected!r}')
        elif not failed and key in required and key not in result:
            errors.append(f'successful result lacks {key}')
    for key, expected in (('lr', args['lr']), ('flops_per_token', fpt),
                          ('target_flops_per_token', args['target_fpt']),
                          ('reference_train_flops', 3 * args['target_fpt'] * args['steps'] * args['batch'] * context)):
        if key in result and not same_number(result[key], expected):
            errors.append(f'{key} differs from the registered budget')
        elif not failed and key not in result:
            errors.append(f'successful result lacks {key}')
    if 'config' in result:
        actual_cfg = result['config']
        if not isinstance(actual_cfg, dict) or any(actual_cfg.get(k) != v for k, v in cfg.items()):
            errors.append('actual full model config differs from job; report-only extra fields are allowed')
    elif not failed:
        errors.append('successful result lacks config')
    actual_steps = result.get('steps')
    if actual_steps is not None:
        if isinstance(actual_steps, bool) or not isinstance(actual_steps, int) or not 0 <= actual_steps <= planned_steps:
            errors.append('actual steps are outside the registered budget')
        elif not failed and actual_steps != planned_steps:
            errors.append('successful run did not finish its registered update count')
        else:
            for key, expected in (('train_tokens', actual_steps * args['batch'] * context),
                                  ('train_flops', 3 * fpt * actual_steps * args['batch'] * context)):
                if key in result and not same_number(result[key], expected):
                    errors.append(f'{key} disagrees with actual steps and counted architecture')
                elif not failed and key not in result:
                    errors.append(f'successful result lacks {key}')
    elif not failed:
        errors.append('successful result lacks steps')
    if not failed:
        curve = result.get('curve')
        if not isinstance(curve, list) or not curve or curve[-1].get('step') != planned_steps:
            errors.append('final curve entry is absent or not at the registered final step')
        elif result.get('validation') != curve[-1].get('validation'):
            errors.append('selected validation is not the final curve validation')
        # Check evaluation counts, never initial-run held-out accuracy.
        scored_per_sequence = 16 if args['task'] == 'mqar_small' or args['task'].startswith('wp_') else 8
        if args['task'] in ('mqar_small', 'induction_small') or args['task'].startswith('wp_'):
            for name, size in (('validation', args['evalset']), ('test', args['testset'])):
                metric = result.get(name)
                if not isinstance(metric, dict) or metric.get('scored_tokens') != size * scored_per_sequence:
                    errors.append(f'{name} scored-token count differs from the registered evaluation size')
    report.update(status='integrity_invalid' if errors else 'measurement_invalid' if failed else 'complete',
                  actual_steps=actual_steps, planned_steps=planned_steps,
                  flops_per_token=fpt, expected_reference_train_flops=3 * args['target_fpt'] * args['steps'] * args['batch'] * context)
    return report


def audit_initial_results(manifests, results_dir=None, research_dir=DEFAULT_RESEARCH, ledger_path=None):
    """Validate primary/alternate artifact identity before frozen planner selection."""
    research = pathlib.Path(research_dir).resolve()
    p, bd = modules(research)
    folder = pathlib.Path(results_dir or research / 'results/beyond_runs')
    entries, sources = read_manifests(manifests, research, p)
    ledger_file = pathlib.Path(ledger_path or research / 'results/beyond_budget.json')
    ledger = json.loads(ledger_file.read_text()).get('jobs', {}) if ledger_file.exists() else {}
    reports = []
    for manifest, job in entries:
        p.identify_job(job)  # Full primary protocol; rejects old unmatched pilots.
        path = folder / (job['id'] + '.json')
        result = json.loads(path.read_text()) if path.exists() else None
        report = audit_result(manifest, job, result, p, bd)
        if result is None and ledger.get(job['id'], {}).get('status') in ('complete', 'error'):
            report.update(status='integrity_invalid', errors=['terminal ledger entry has no settled result artifact'])
        reports.append(report)
    output = {'schema': 'stage1_initial_audit', 'schema_version': 1, 'protocol_id': p.PROTOCOL_ID,
              'model_source_hashes': sources, 'ok': all(not r['errors'] for r in reports),
              'records': reports, 'pending': sum(r['status'] == 'pending' for r in reports),
              'invalid_measurements': sum(r['status'] == 'measurement_invalid' for r in reports)}
    output['sha256'] = digest(output)
    return output


def metric_record(job, result, audit, task, depth, seed, arm, lr, p):
    row = {'job_id': job['id'] if job else None, 'task': task, 'layers': depth, 'seed': seed,
           'arm': arm, 'lr': lr, 'status': 'pending', 'test_score': None, 'metric': 'bal_late' if p.is_word(task) else 'acc',
           'uncertainty': None, 'audit': audit}
    if job is None or result is None:
        return row
    if audit['status'] in ('integrity_invalid', 'measurement_invalid'):
        row.update(status='invalid', error=result.get('error') or result.get('failure') or audit['errors'])
        return row
    metrics = result.get('test')
    score = metrics.get(row['metric']) if isinstance(metrics, dict) else None
    if not finite(score) or not 0 <= score <= 1:
        row.update(status='invalid', error='missing, nonfinite or out-of-range final test score')
        return row
    uncertainty = {'all_position_acc_se_sequences': metrics.get('acc_se_sequences'),
                   'late_metric_se_missing': p.is_word(task),
                   'selected_metric_standard_error': None, 'selected_metric_ci95_normal': None}
    if row['metric'] == 'acc' and finite(metrics.get('acc_se_sequences')):
        se = metrics['acc_se_sequences']
        if se < 0:
            row.update(status='invalid', error='negative sequence standard error')
            return row
        uncertainty.update(selected_metric_standard_error=se,
                           selected_metric_ci95_normal=[max(0., score - 1.96 * se), min(1., score + 1.96 * se)])
    elif row['metric'] == 'bal_late':
        uncertainty['note'] = 'The runner does not report a clustered SE for balanced second-half accuracy; its all-position acc SE is not an SE for this gate metric.'
    exact = metrics.get('seq_acc')
    n = result['testset']
    if finite(exact) and 0 <= exact <= 1 and n > 0:
        z = 1.96
        denom = 1 + z * z / n
        center = (exact + z * z / (2 * n)) / denom
        radius = z * math.sqrt(exact * (1 - exact) / n + z * z / (4 * n * n)) / denom
        uncertainty.update(sequence_exact_match_accuracy=exact,
                           sequence_exact_match_se=math.sqrt(exact * (1 - exact) / n),
                           sequence_exact_match_ci95_wilson=[max(0., center - radius), min(1., center + radius)],
                           independent_sequence_count=n)
    row.update(status='complete', test_score=score, metrics=metrics, uncertainty=uncertainty,
               steps=result['steps'], train_flops=result['train_flops'], testset=result['testset'],
               test_seed=result['test_seed'], wall_seconds=result.get('wall'))
    return row


def confirmation_artifact(selection, manifests, results_dir=None, research_dir=DEFAULT_RESEARCH):
    research = pathlib.Path(research_dir).resolve()
    p, bd = modules(research)
    if not isinstance(selection, dict):
        selection = json.loads(pathlib.Path(selection).read_text())
    verify_json_hash(selection, 'frozen seed0 selection')
    if selection.get('protocol_id') != p.PROTOCOL_ID:
        raise ValueError('frozen selection belongs to another protocol')
    sources = selection.get('model_source_hashes')
    if not isinstance(sources, dict) or set(sources) != set(p.MODEL_SOURCES):
        raise ValueError('selection must identify exactly the five model/data source files')
    expected = p.confirmation_jobs(selection, 'all')
    if not expected:
        raise ValueError('no seed0-surviving candidate is eligible for confirmation')
    by_arguments = {digest(j['argv']): j for j in expected}
    entries, _ = read_manifests(manifests, research, p, sources)
    folder = pathlib.Path(results_dir or research / 'results/beyond_runs')
    found = {}
    for manifest, job in entries:
        key = digest(job['argv'])
        if key not in by_arguments:
            raise ValueError(f"{job['id']}: confirmation job differs from frozen rate/arm/seed/compute selection")
        if job.get('script') != 'beyond_diag.py' or job.get('attempt') != 0:
            raise ValueError('unregistered confirmation script or retry')
        if key in found:
            raise ValueError('multiple confirmation jobs exist for one frozen experimental identity')
        prototype = by_arguments[key]
        for field in ('id', 'frozen_selection_sha256', 'selected_seed0_job'):
            if job.get('protocol', {}).get(field) != prototype['protocol'][field]:
                raise ValueError(f'confirmation {field} does not bind the frozen selection')
        path = folder / (job['id'] + '.json')
        result = json.loads(path.read_text()) if path.exists() else None
        audit = audit_result(manifest, job, result, p, bd)
        found[key] = (job, result, audit)

    def read_cell(task, depth, seed, selected):
        arm, lr = selected['arm'], selected['lr']
        key = digest(p.make_job(task, depth, arm, lr, seed, phase='confirmation')['argv'])
        job, result, audit = found.get(key, (None, None, None))
        return metric_record(job, result, audit, task, depth, seed, arm, lr, p)

    references = {}
    for task, depth in p.PRIMARY_CELLS:
        selected = selection['references'][p.cell_key(task, depth)]['selected']
        for seed in (1, 2, 3):
            references[f'{p.cell_key(task, depth)}/seed{seed}'] = read_cell(task, depth, seed, selected)
    candidates = {}
    for arm in p.PRIORITY:
        if arm not in selection['survivors']:
            candidates[arm] = {'status': 'rejected', 'reason': 'did_not_pass_seed0_screen',
                               'cells': [], 'pass_job_ids': [], 'reference_job_ids': []}
            continue
        cells = []
        for task, depth in p.PRIMARY_CELLS:
            selected = selection['selected'][p.cell_key(task, depth, arm)]['selected']
            for seed in (1, 2, 3):
                candidate = read_cell(task, depth, seed, selected)
                reference = references[f'{p.cell_key(task, depth)}/seed{seed}']
                floor = .95 if p.is_word(task) else .90
                status = 'pending'
                if candidate['status'] == 'invalid':
                    status = 'invalid'
                elif reference['status'] == 'invalid':
                    status = 'reference_invalid'
                elif reference['status'] == 'complete' and not p.at_least(reference['test_score'], floor):
                    status = 'reference_failed'
                elif candidate['status'] == 'complete' and not p.at_least(candidate['test_score'], floor):
                    status = 'rejected'
                elif candidate['status'] == reference['status'] == 'complete':
                    status = 'passed' if p.at_least(candidate['test_score'] + .03, reference['test_score']) else 'rejected'
                cells.append({'task': task, 'layers': depth, 'seed': seed, 'candidate': candidate,
                              'reference': reference, 'gate': {'status': status, 'floor': floor, 'maximum_reference_gap': .03,
                                                            'threshold_tolerance': p.EPS}})
        states = {c['gate']['status'] for c in cells}
        # A bad positive control never licenses a pass against a weaker baseline.
        status = ('invalid' if 'invalid' in states else 'rejected' if 'rejected' in states
                  else 'unconfirmed' if states & {'reference_failed', 'reference_invalid'}
                  else 'pending' if 'pending' in states else 'passed')
        candidates[arm] = {'status': status, 'cells': cells,
                           'pass_job_ids': [c['candidate']['job_id'] for c in cells if c['gate']['status'] == 'passed'],
                           'reference_job_ids': sorted({c['reference']['job_id'] for c in cells if c['reference']['job_id']}),
                           'confirmation_required_cells': 18, 'confirmation_passed_cells': sum(c['gate']['status'] == 'passed' for c in cells)}
    artifact = {
        'schema': 'stage1_confirmation', 'schema_version': 1, 'protocol_id': p.PROTOCOL_ID,
        'frozen_selection_sha256': selection['sha256'], 'model_source_hashes': sources,
        'candidates': candidates, 'references': references,
        'passed_candidates': [a for a in p.PRIORITY if candidates[a]['status'] == 'passed'],
        'primary_cells': [list(x) for x in p.PRIMARY_CELLS], 'seeds': [1, 2, 3],
        'source_manifest_hashes': sorted({m['sha256'] for m, _ in entries}),
        'gate_measurement': 'independent final TEST only; seed0 selected rates/reference arms are frozen',
        'status_definitions': {'passed': 'all18 final-test cells pass with valid positive controls',
                              'rejected': 'a valid candidate test fails its floor/margin, or candidate failed seed0',
                              'pending': 'one or more needed results are absent/running',
                              'invalid': 'candidate artifact or measurement is invalid',
                              'unconfirmed': 'the frozen positive control is invalid or fails its absolute floor; no substitution'},
        'evaluator_sha256': hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
    }
    artifact['sha256'] = digest(artifact)
    return artifact


def write_json(path, value):
    text = json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n'
    if path:
        pathlib.Path(path).write_text(text)
    else:
        print(text, end='')


def self_test(research):
    p, bd = modules(research)
    sources = current_sources(research, p.MODEL_SOURCES)

    def synthetic_result(job, manifest, score=.99):
        args, cfg, context, steps, fpt = expected_run(job, p, bd)
        count = 8 if args['task'] == 'induction_small' else 16
        val = {'acc': .99, 'bal_late': .99, 'scored_tokens': args['evalset'] * count}
        test = {'acc': score, 'bal_late': score, 'acc_se_sequences': .001, 'scored_tokens': args['testset'] * count}
        return {'job_id': job['id'], 'argv': job['argv'], 'script': job['script'], 'source_hashes': sources,
                'source_sha256': sources, 'manifest': manifest['name'], 'manifest_sha256': manifest['sha256'],
                'config': cfg, **{k: args[k] for k in ('seed', 'task', 'layers', 'arch', 'opt', 'batch', 'lr', 'evalset', 'testset')},
                'model': args['arch'], 'steps': steps, 'reference_steps': args['steps'],
                'validation_seed': 10000 + args['seed'], 'test_seed': 20000 + args['seed'],
                'flops_per_token': fpt, 'target_flops_per_token': args['target_fpt'],
                'train_tokens': steps * args['batch'] * context, 'train_flops': 3 * fpt * steps * args['batch'] * context,
                'reference_train_flops': 3 * args['target_fpt'] * args['steps'] * args['batch'] * context,
                'validation': val, 'curve': [{'step': steps, 'validation': val}], 'test': test}

    with tempfile.TemporaryDirectory() as temp:
        folder = pathlib.Path(temp); results = folder / 'results'; results.mkdir()
        def install(name, jobs):
            for job in jobs:
                bound = {k: job[k] for k in ('script', 'argv', 'gpu', 'attempt')}; bound['source_hashes'] = sources
                job['id'] = digest(bound)[:24]
            manifest = {'name': name, 'jobs': jobs, 'source_hashes': sources}; manifest['sha256'] = digest(manifest)
            path = folder / (name + '.json'); path.write_text(json.dumps(manifest))
            for job in jobs:
                (results / (job['id'] + '.json')).write_text(json.dumps(synthetic_result(job, manifest)))
            return path, manifest
        initial, first = install('initial', p.initial_jobs())
        assert audit_initial_results([initial], results, research)['ok']
        records = [p.make_record(j, synthetic_result(j, first)) for j in first['jobs']]
        selection = p.select(records, sources)
        confirm_path, manifest = install('confirmation', p.confirmation_jobs(selection, 'all'))
        artifact = confirmation_artifact(selection, [confirm_path], results, research)
        assert artifact['passed_candidates'] == list(p.PRIORITY)
        assert all(len(c['cells']) == 18 for c in artifact['candidates'].values())
        assert all(len(c['pass_job_ids']) == 18 for c in artifact['candidates'].values())
        assert set(artifact['model_source_hashes']) == set(p.MODEL_SOURCES)
        verify_json_hash(artifact, 'synthetic final artifact')
        bjob = next(j for j in manifest['jobs'] if j['protocol']['arm'] == 'B')
        bpath = results / (bjob['id'] + '.json'); original = json.loads(bpath.read_text())
        wrong = copy.deepcopy(original); wrong['test']['bal_late'] = .94; wrong['test']['acc'] = .94
        bpath.write_text(json.dumps(wrong))
        assert confirmation_artifact(selection, [confirm_path], results, research)['candidates']['B']['status'] == 'rejected'
        bpath.unlink()
        assert confirmation_artifact(selection, [confirm_path], results, research)['candidates']['B']['status'] == 'pending'
        wrong = copy.deepcopy(original); wrong['seed'] += 1; bpath.write_text(json.dumps(wrong))
        assert confirmation_artifact(selection, [confirm_path], results, research)['candidates']['B']['status'] == 'invalid'
        bpath.write_text(json.dumps(original))
        refjob = next(j for j in manifest['jobs'] if j['protocol']['arm'] == 'prefix')
        refpath = results / (refjob['id'] + '.json'); refresult = json.loads(refpath.read_text()); refresult['test']['bal_late'] = .94
        refpath.write_text(json.dumps(refresult))
        assert confirmation_artifact(selection, [confirm_path], results, research)['candidates']['B']['status'] == 'unconfirmed'
        # Metadata/accounting/worker-source mismatches are independently rejected.
        firstjob = first['jobs'][0]; good = synthetic_result(firstjob, first)
        for field, bad in (('job_id', 'swapped'), ('argv', []), ('lr', .123), ('steps', good['steps'] - 1),
                           ('train_flops', good['train_flops'] * 1.01), ('evalset', 999), ('source_sha256', {})):
            bad_result = copy.deepcopy(good); bad_result[field] = bad
            assert audit_result(first, firstjob, bad_result, p, bd)['status'] == 'integrity_invalid', field
        # Low held-out scores cannot affect initial selection/integrity.
        low_test = copy.deepcopy(good); low_test['test'].update(acc=0., bal_late=0.)
        assert audit_result(first, firstjob, low_test, p, bd)['status'] == 'complete'
        # A true partial numerical failure remains an invalid measurement, not an integrity failure.
        failed = copy.deepcopy(good); failed.update(failure='nonfinite_training_loss', steps=10)
        _, _, context, _, fpt = expected_run(firstjob, p, bd)
        failed['train_tokens'] = 10 * 64 * context; failed['train_flops'] = 3 * fpt * 10 * 64 * context
        assert audit_result(first, firstjob, failed, p, bd)['status'] == 'measurement_invalid'
    return {'passed': True, 'checks': ['all18 final-test gates', 'canonical artifact hash', 'frozen rates and variants',
            'pending/invalid/rejected separation', 'failed positive reference cannot pass', 'source/metadata/FLOP integrity',
            'held-out quality does not affect initial audit', 'partial failures retain correct semantics']}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--research-dir', type=pathlib.Path, default=DEFAULT_RESEARCH)
    sub = ap.add_subparsers(dest='command', required=True)
    for name in ('audit-initial', 'confirm'):
        cmd = sub.add_parser(name); cmd.add_argument('--manifest', action='append', required=True)
        cmd.add_argument('--results-dir', type=pathlib.Path); cmd.add_argument('--output')
        if name == 'confirm':
            cmd.add_argument('--selection', required=True, type=pathlib.Path)
        else:
            cmd.add_argument('--ledger', type=pathlib.Path)
            cmd.add_argument('--select-output'); cmd.add_argument('--alternates-output')
    sub.add_parser('self-test')
    args = ap.parse_args(); research = args.research_dir.resolve()
    if args.command == 'self-test':
        write_json(None, self_test(research)); return
    if args.command == 'confirm':
        artifact = confirmation_artifact(args.selection, args.manifest, args.results_dir, research)
        write_json(args.output, artifact)
    else:
        artifact = audit_initial_results(args.manifest, args.results_dir, research, args.ledger)
        write_json(args.output, artifact)
        if not artifact['ok']:
            raise SystemExit('Artifact integrity audit failed; frozen selector was not invoked.')
        if args.select_output or args.alternates_output:
            p, _ = modules(research)
            records, sources = p.load_records(args.manifest, args.results_dir or research / 'results/beyond_runs',
                                             args.ledger or research / 'results/beyond_budget.json')
            if args.select_output:
                write_json(args.select_output, p.select(records, sources))
            if args.alternates_output:
                write_json(args.alternates_output, p.alternate_jobs(records))
    if args.output:
        print(json.dumps({'output': args.output, 'schema': artifact['schema'], 'sha256': artifact['sha256'], 'launched': False}))


if __name__ == '__main__':
    main()
