# AUDIT: an independent check of every number before the paper (proposed 24 Oct; needs Neo's go)

The auditor must be a session that wrote none of the experiment code. Read-only except for its own report and for
reruns it registers. Cap $15.

1. **Provenance.** Every number in research/master/master_table.md (built by build_master.py) traces to a raw record,
   the record to a code commit and a config. List any number without a record.
2. **Protocol, automated.** For every record: selection only after every term is fully on, never on test lengths;
   test sets disjoint from training sets (hash the examples); the arm's config differs from the O arm only in the
   intended flags (diff the configs); the same exact-metric definition in every domain.
3. **Leakage hunt, by reading code.** Teacher forcing at test time; true states or labels reaching the model's input
   at test; the simulator's labels used for training in the soft arm; partners built from test examples; evaluation
   on fewer examples than reported.
4. **Floors.** A shallow baseline per domain (a model that ignores the history, or reads only the last event) must sit
   at chance at the long length. If a floor scores high, the task is easier than claimed.
5. **Independent reruns.** From a clean checkout, rerun one seed of FULL+N and of O in every domain and compare with
   the table within tolerance. These scripts become the release repo's reproduction path.
Report: a table of checks (pass / fail / not checkable) per domain, and every discrepancy with its fix.
