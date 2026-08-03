# NER / EL / ER Task Placement and Integration

Status: v0.1 (integrates the "Updated Resynthesis, Realignment, and ER/NER
Integration Plan").

This document integrates the NER (mention/span) phase into the existing Regis
entity-graph contracts. It does **not** fork a new resolution model — it adds the
missing upstream `extract -> mentions` head of the executable identity spine and
wires it into the resolution and graph contracts that already ship in this repo.

## 1. The executable spine

```
observe -> Event-IR -> extract -> candidate generate -> resolve
        -> policy veto -> graph update -> proof artifact
        -> search / materialize -> feedback -> retrain
```

NER, EL, and ER are **separate but coupled** phases:

| Phase | Question | Output | Contract (this repo) |
|-------|----------|--------|----------------------|
| NER   | Where are the mentions/spans, and of what class? | `MentionSet` | `schemas/ner/mention.schema.json` (**new**) |
| EL    | Which KB / canonical entity does a mention ground to? | candidate/concordance | `schemas/acr/concordance-link.schema.json`, `schemas/acr/evidence-claim.schema.json` |
| ER    | Which records/events/entities cluster into one identity, over time and sources? | resolution decision + evidence bundle | `schemas/er_plus/ERPlusEvidenceBundle.v0.1.json`, `schemas/acr/decision-ledger-entry.schema.json`, `schemas/acr/canonical-entity.schema.json` |
| Graph | Materialize resolved state as append-only, unmergeable graph | node/edge/delta | `schemas/node.schema.json`, `schemas/edge.schema.json`, `schemas/graph_delta.schema.json`, `schemas/epistemic-edge-record.schema.json` |
| Proof | Externalize system judgment | proof certificate | `schemas/proof/proof-certificate.schema.json` |

`Mention.el_candidate_refs` is the forward link from NER into EL/ER: a mention
carries the concordance/candidate ids it grounds to, so the resolution lane
consumes NER output without a new interface.

## 2. What is new here (the SOTA delta)

Everything from `extract ->` downward already existed as contracts. The NER phase
did not. This delta adds:

- **`MentionSet` / `Mention`** typed, provenance-bearing, scope-stamped spans.
- The **base + domain entity-class taxonomy** (`schemas/ner/entity-class.schema.json`).
- **First-class overlapping / multi-labelled spans** — a phrase may be at once a
  named entity, a prime-topic marker, and a policy-sensitive context cue.
- **Local-first + FIPS handling on the span** — `locality` scope stamp and
  `pii` minimization with SHA-256 authoritative hashing.

## 3. Entity-class taxonomy

Base classes (domain-neutral): `PERSON`, `ORG`, `PRODUCT_SERVICE`, `DEVICE`,
`ACCOUNT`, `IDENTIFIER`, `CREDENTIAL`, `LOCATION`, `JURISDICTION`,
`CONSENT_ARTIFACT`, `POLICY_TERM`, `PRIME_TOPIC_MENTION`, `ACTION_EVENT_TRIGGER`,
`RELATIONSHIP_MENTION`.

Domain classes (sovereignty / consent / scope concerns): `SCOPE_REALM`,
`TRACKING_IDENTIFIER`, `HSM_HANDLE`, `NONCE_STREAM`, `EXPORT_ATTEMPT`,
`CONSENT_WITNESS`, `SENSITIVE_CONTEXT`, `CHILD_CONTEXT`, `PATIENT_CONTEXT`,
`CIVIC_CONTEXT`, `MARKETING_CONTEXT`.

`entity-class.schema.json` is the single source of truth; the enum inlined into
`mention.schema.json` is asserted in sync by `tools/validate_ner_contracts.py`.

## 4. Task placement (local-first)

Following the plan's placement rules:

- **Entry time / near source (local-first, on device / citizen-fog):** source
  typing, scope capture, deterministic identifier parsing, lightweight
  dictionary NER for high-value classes, tokenization/normalization, immediate
  PII minimization/hashing, prime-topic hinting, consent/preference lookup.
- **Nearline local (still local-first, async):** statistical NER / span
  categorizer, entity linking to local KB, event/relation extraction, candidate
  pair/block generation, feature-atom typing, preliminary graph upsert.
- **Citizen cloud / regional (assistive, bounded):** heavier ER clustering,
  graph-wide consistency checks, sequence-neutral replay / unmerge analysis,
  ontology alignment, embedding/index rebuild, retraining prep.
- **Federated / institutional (only under explicit contract and policy):**
  cross-party candidate exchange, limited identity proof exchange, federated
  training/eval, aggregate analytics, policy broadcast.

`MentionSet.locality` records which boundary an extraction actually ran in
(`CITIZEN_FOG`, `CITIZEN_CLOUD`, `INSTITUTION`, `ADTECH`, `HSM`).

## 5. Teeth

`make validate-ner-contracts` accepts `fixtures/ner/mention_set.valid.json`
(which must contain overlapping spans and a FIPS-hashed PII field) and rejects
every `fixtures/ner/*.invalid.json` — unknown class, zero/negative span,
out-of-range confidence, missing provenance, non-FIPS hash algorithm.

## 6. Not yet buildable-now (tracked as issues)

The plan's full ER service boundary (promotion from library to service with the
`/extract`, `/resolve`, `/policy`, `/graph`, `/proof`, `/search` API surface),
adding `uncertainty` + `reversibility/action_class` to every resolution output,
and the glossary/ontology versioning + retraining loop are tracked as separate
issues rather than expanding this contract PR.
