# MeshRush Integration

This document defines the Regis Entity Graph integration stance for MeshRush.

MeshRush is the graph-operating runtime for autonomous agents over graph views derived from a typed hypergraph world model. Regis should provide governed graph views, proof/witness attachment surfaces, and replayable graph deltas that MeshRush can operate over.

Regis does not become MeshRush. MeshRush does not become Regis.

---

## 1. Boundary statement

Regis owns:

- temporal entity graph materialization,
- graph node and edge contracts,
- proof and witness attachment surfaces,
- graph delta replay,
- graph query semantics.

MeshRush owns:

- graph traversal and graph-view operation semantics,
- exploratory diffusion over graph views,
- stopping and crystallization behavior,
- local structure compilation,
- reusable graph-operation artifacts,
- traces and learning/evidence surfaces emitted by graph operation.

MeshRush must not silently mutate Regis graph state outside accepted graph-delta paths.

---

## 2. Ecosystem position

The intended relationship is:

```text
Identity Is Prime / Policy Fabric / AgentPlane
  -> proof, policy, execution, and evidence judgments

Regis Entity Graph
  -> materialized graph views, deltas, provenance, proof/witness attachments

MeshRush
  -> graph-operating runtime over those governed graph views

Sociosphere / workspace controllers
  -> workspace context and actuation boundary

Alexandrian Academy / learning surfaces
  -> evaluation, learning, and transfer memory
```

MeshRush should consume governed graph views from Regis and emit operation traces, crystallization artifacts, and evidence refs back into the broader evidence fabric.

---

## 3. Graph view contract

Regis should expose graph views to MeshRush with explicit view metadata:

- `view_id`,
- `graph_version`,
- `policy_view`,
- `scope_tags`,
- `allowed_node_kinds`,
- `allowed_edge_kinds`,
- `redaction_profile`,
- `proof_refs`,
- `audit_refs`.

A MeshRush graph view is not necessarily the full Regis graph. It is a policy-bounded materialized view.

---

## 4. Node and edge implications

Regis schemas should support MeshRush-compatible graph operation by preserving:

- `SOURCE_GRAPH_VIEW` nodes for named materialized views,
- `SOURCE_AUDIT_RECORD` nodes for evidence and audit references,
- proof nodes and proof-ingress nodes,
- session and subject nodes,
- policy and consent witness nodes.

Edges relevant to MeshRush include:

- `MATERIALIZED_AS_SOURCE_GRAPH_VIEW`,
- `HAS_SOURCE_AUDIT_RECORD`,
- `ATTESTED_BY_PROOF`,
- `AUTHORIZED_BY_CONSENT`,
- `OCCURS_IN_SCOPE`,
- `BLOCKED_EXPORT`,
- `MERGE_VETOED`,
- `FORBIDDEN_RELATIONSHIP`.

These allow MeshRush to operate over graph context without bypassing proof and policy boundaries.

---

## 5. Operation trace feedback

MeshRush should emit traces that can be converted into Regis graph deltas or audit records.

Recommended output classes:

- `MESHRUSH_TRAVERSAL_TRACE`,
- `MESHRUSH_DIFFUSION_TRACE`,
- `MESHRUSH_STOPPING_DECISION`,
- `MESHRUSH_CRYSTALLIZATION_ARTIFACT`,
- `MESHRUSH_DISSOLUTION_EVENT`,
- `MESHRUSH_VIEW_REUSE_RECORD`.

These should initially materialize as `SOURCE_AUDIT_RECORD` nodes or proof/evidence attachments rather than direct graph rewrites.

Direct graph rewrites require explicit graph deltas.

---

## 6. Policy posture

MeshRush may traverse only graph views that Regis has materialized under a policy view.

MeshRush must respect:

- redaction profiles,
- scope restrictions,
- forbidden relationship edges,
- blocked export edges,
- proof/witness requirements,
- graph version boundaries.

If MeshRush discovers a candidate relation, it should emit a proposal or audit record, not directly assert truth.

Candidate relation promotion belongs to the reasoning and policy layers, then returns to Regis as an accepted graph delta.

---

## 7. Replay and reversibility

MeshRush operation over Regis views should be replayable enough for audit.

Minimum trace fields:

- source graph view id,
- graph version,
- traversal seed or starting node refs,
- policy view id,
- operation class,
- stopping condition,
- generated artifacts,
- evidence refs,
- timestamp.

Regis should not need to re-run MeshRush to explain the existence of graph state. It should preserve references to MeshRush traces and crystallization artifacts.

---

## 8. Non-goals

This document does not implement:

- MeshRush runtime,
- traversal algorithms,
- diffusion algorithms,
- graph materializer runtime,
- learning/evaluation memory,
- Sociosphere workspace control,
- AgentPlane execution controls.

It only defines how Regis should prepare for MeshRush integration.

---

## 9. Practical reading

Regis gives agents a governed graph memory.

MeshRush gives agents a way to move through that graph.

The integration rule is simple:

```text
Regis materializes governed graph views.
MeshRush operates over those views.
MeshRush emits traces and candidate artifacts.
Regis records those traces and only mutates graph state through accepted deltas.
```

That keeps graph operation powerful without making it ungoverned.
