# ER+ Regis Graph Contract

Status: v0.1 graph-contract spine.

This document defines how Regis stores ER+ evidence emitted by Identity Is Prime. Identity Is Prime remains the executable reference and policy-evaluation lane. Regis is the graph-of-record surface for canonical entities, source records, path certificates, decision ledger entries, and replay evidence.

## 1. Ownership boundary

Identity Is Prime owns:

- record edit generator semantics;
- approximate `D_R` record path-cost computation;
- approximate `D_E` entity move path-cost computation;
- behavioral delay-coordinate feature extraction;
- neutrality replay execution;
- proof artifact emission.

Regis owns:

- source-record vertices;
- canonical-entity vertices;
- record-path certificate vertices;
- entity-move path certificate vertices;
- behavioral evidence vertices;
- local expansion observations;
- neutrality replay runs;
- decision ledger entries;
- typed edges linking evidence to entities and records.

Regis must not free-write canonical human identity truth from Sherlock, Holmes, Agent Registry, or search outputs. Those systems may propose annotations, findings, retrieval results, or candidate graph mutations. Canonical entity mutation must flow through a governed Regis reducer and emit a ledger entry.

## 2. Graph object families

ER+ introduces these Regis object families:

- `RecordPathCertificate`
- `EntityMovePathCertificate`
- `BehavioralTrajectoryEvidence`
- `BehavioralSimilarityEvidence`
- `LocalExpansionObservation`
- `NeutralityReplayRun`
- `ERPlusDecisionLedgerEntry`

The shared schema in `schemas/er_plus/ERPlusEvidenceBundle.v0.1.json` is a bundle envelope. It allows fixtures and conformance lanes to validate all required evidence families without committing to a database backend.

## 3. Required edge semantics

A valid Regis ER+ bundle must support the following pointer pattern:

```text
SourceRecord -> RecordPathCertificate -> ERPlusDecisionLedgerEntry
CanonicalEntity -> EntityMovePathCertificate -> ERPlusDecisionLedgerEntry
CanonicalEntity -> LocalExpansionObservation
CanonicalEntity -> BehavioralTrajectoryEvidence
BehavioralSimilarityEvidence -> CanonicalEntity
NeutralityReplayRun -> ERPlusDecisionLedgerEntry
```

Every certificate object must pin:

- `schema_version`
- `policy_version`
- `resolver_version`
- `input_hash`
- `result_hash`

If a certificate is used to support a canonical merge, split, or reassignment, it must also be reachable from a decision-ledger entry.

## 4. Path cost discipline

Regis stores `record_path_cost` and `entity_path_cost` as intrinsic path costs. It must not relabel them as true metrics unless the evidence object explicitly declares `metric_claim = metric_under_symmetric_inverse_assumptions`.

Allowed metric claims:

- `path_cost`
- `quasi_metric`
- `metric_under_symmetric_inverse_assumptions`

The default must be `path_cost`.

## 5. Behavioral and expansion evidence

Behavioral evidence is stored as feature evidence, not as a proof of identity by itself. Delay-coordinate features are Takens-inspired and must carry `takens_claim = inspired_feature_only` unless a separate formal embedding assumption file is attached.

Local expansion observations are finite-graph diagnostics. They are not Hausdorff dimensions and must be labeled as `finite_graph_expansion`.

## 6. Neutrality replay evidence

Neutrality is a conformance invariant. A `NeutralityReplayRun` stores canonical order hash, reordered order hash, final state hashes, distance, tolerance, and result. A failed replay is evidence, not a runtime crash. Failed replay outputs should feed Holmes or Regis review queues.

## 7. Defensive graph boundary

ER+ identity evidence must not suppress legitimate cyber-defense correlation. Defensive/investigative edges may be stored separately, but they cannot be silently promoted into canonical human identity merges. Regis must carry distinct edge kinds for:

- identity merge evidence;
- related-but-not-same evidence;
- investigative association;
- defensive correlation;
- search retrieval pointer.

## 8. Conformance fixture

`fixtures/er_plus/er_plus_evidence_bundle.valid.json` is the first portable Regis fixture. It asserts that one source-record pair, one entity move path, one behavioral signal, one expansion diagnostic, and one neutrality replay can be bundled with ledger pointers and deterministic hashes.
