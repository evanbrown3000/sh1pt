# Production ML Deployment Triage — 10-Minute Checklist

A compact operator checklist for production ML incidents. Use it to get from “the model is broken” to an evidence-backed next action without changing multiple variables at once.

For the longer field guide, see **[Production ML Deployment Triage](https://leanpub.com/production-ml-deployment-triage)** by Evan Brown on Leanpub (EPUB; minimum price $19).

## 0. Freeze the incident identity

Write down the exact failing deployment before touching it:

- service / endpoint / model name
- model artifact or image digest
- code/config revision
- environment and region
- first known bad timestamp
- last known good revision
- one concrete failing request or metric

If you cannot name the exact failing deployment, you are not ready to change it.

## 1. Ask whether rollback is cheaper than diagnosis

Prefer rollback when all three are true:

- a known-good version exists,
- rollback is reversible and low-risk,
- the incident is currently hurting users or revenue.

Preserve the failed artifact and evidence before rollback so diagnosis is still possible afterward.

## 2. Separate data failure from model failure

Check the live request/data path before blaming weights:

- schema and type drift
- missing/defaulted features
- normalization or preprocessing changes
- category / vocabulary changes
- time-window or timezone errors
- train/serve feature parity
- unexpected null, NaN, empty, or out-of-range rates

Compare one failing production example to the exact representation the model actually receives.

## 3. Prove artifact and configuration identity

Verify that production loaded what you think it loaded:

- model checksum / digest
- tokenizer or feature-transform version
- runtime flags and thresholds
- dependency versions
- environment variables that affect inference
- hardware/backend selection

Do not infer deployment identity from a Git branch name or dashboard label alone.

## 4. Split correctness from availability

A healthy process can serve bad predictions; a correct model can still be operationally unavailable.

Check separately:

**Correctness**
- known examples / golden set
- output distribution shifts
- calibration or threshold behavior
- class/score sanity

**Availability**
- error rate
- latency percentiles
- queue depth
- timeout rate
- memory/VRAM pressure
- cold-start/load failures

## 5. Localize the failing boundary

Walk the request once, in order:

`client -> gateway -> feature/data fetch -> preprocessing -> model runtime -> postprocessing -> downstream consumer`

At each boundary, preserve one input/output pair. Stop when the first incorrect transition appears.

## 6. Check capacity before changing semantics

If the model only fails under load, inspect:

- request concurrency
- batch size
- CPU/RAM/VRAM headroom
- GPU OOM / allocator churn
- thread/process pool saturation
- autoscaling lag
- dependency throttling

Do not “fix” an overloaded service by changing model thresholds or business logic.

## 7. Make one controlled comparison

Choose the smallest experiment that distinguishes two hypotheses, for example:

- old artifact vs. new artifact with identical traffic
- old preprocessing vs. new preprocessing with identical model
- one known request against old and new serving stacks
- canary slice vs. stable slice

Change one causal dimension at a time and record the result.

## 8. Define the stop condition before the next mutation

Examples:

- rollback if p95 latency stays above X for N minutes
- halt rollout if golden-set error exceeds Y
- promote canary only if error/latency remain within the stable baseline
- stop diagnosis and restore known-good state if user impact exceeds a fixed bound

A test without a stop condition easily becomes an outage extension.

## 9. Preserve a minimal evidence packet

Keep enough information that another engineer can continue without repeating the incident:

- exact versions/digests
- failing example(s)
- before/after metric snapshot
- first bad boundary
- experiment performed
- result
- current state
- next hypothesis

Avoid a giant log dump when a small causal packet is sufficient.

## 10. Close the loop at the user-facing effect

“Deployment succeeded” is not the terminal check. Confirm the beneficiary-side outcome:

- production requests succeed,
- prediction/output behavior is sane,
- latency and error rate are acceptable,
- the intended consumer receives the result,
- the incident symptom is actually gone.

---

**Deeper resource:** [Production ML Deployment Triage on Leanpub](https://leanpub.com/production-ml-deployment-triage).
