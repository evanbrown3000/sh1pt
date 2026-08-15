# LLM / Agent Reliability Triage — 8-Minute Checklist

A compact operational checklist for agentic systems that are “running” but not reliably producing the intended downstream effect.

For a deeper downloadable protocol, see **[Agent Reliability Audit Protocol](https://ugig.net/skills/agent-reliability-audit-protocol)** on UGIG (active paid skill; 12,000 sats at the last provider readback).

## 1. Name the beneficiary-side failure

Do not start with “the agent crashed” or “the daemon is green.” State the failed outcome:

- user did not receive the intended result
- provider mutation did not happen
- subordinate never acted
- result was produced but not consumed
- external effect happened but attribution/settlement is missing

This prevents process health from becoming a proxy for success.

## 2. Trace one causal chain end to end

For one concrete operation, capture:

`instruction -> custody -> execution -> provider/system effect -> return -> consumer use -> beneficiary outcome`

Mark the first missing transition. Repair that transition before adding another scheduler, queue, retry loop, or observer.

## 3. Separate identity from liveness

Verify independently:

- intended agent/persona/project identity
- actual runtime/process identity
- actual conversation/session/account identity
- current owner of the external resource

A live process with the wrong identity is not a healthy agent.

## 4. Distinguish transport from semantic completion

These are different states:

- request stored
- request delivered
- prompt/message visible
- generation/process started
- substantive work performed
- durable/provider effect created
- return produced
- manager/consumer used the return

Do not promote an earlier stage to a later one because the system is busy.

## 5. Check for stale inputs before retrying

Before replaying an operation, compare:

- current instruction vs. historical instruction
- current target/account/session vs. previous target
- current memory/state vs. the state used by the failed attempt
- current provider response vs. the previous failure fingerprint

If the hypothesis is unchanged, a retry is usually duplication rather than learning.

## 6. Protect singular scarce resources

Identify shared resources whose accidental duplication creates failure:

- authenticated browser/profile
- writer lock
- provider session
- rate-limited API
- GPU/model server
- payment/seller account

Prefer one owner and explicit custody over parallel agents racing the same resource.

## 7. Run one discriminating experiment

Choose the smallest change that can tell two hypotheses apart:

- same instruction, corrected target
- same target, current instruction
- same provider action, known-good account/session
- same child work, explicit return consumption
- same model, corrected data/config

Record the before state, the single changed variable, and the downstream result.

## 8. Close on external or beneficiary evidence

A repair is complete only when the original beneficiary-side symptom changes. Examples:

- provider object exists and is buyer-visible
- child return is consumed into a later changed allocation
- user-facing request succeeds
- settlement appears in provider/account truth
- revenue is actually received

If the final beneficiary evidence is UNKNOWN, report UNKNOWN rather than converting internal progress into success.

---

**Deeper downloadable protocol:** [Agent Reliability Audit Protocol on UGIG](https://ugig.net/skills/agent-reliability-audit-protocol).
