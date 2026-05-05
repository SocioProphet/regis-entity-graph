# SourceOS and Platform Alignment

This document aligns Regis Entity Graph with the current SourceOS and Prophet Platform contract direction.

Regis should not invent a competing graph, identity, policy, or proof model. It should materialize governed entity graph state from upstream reasoning and platform contracts.

---

## 1. Position in the ecosystem

Regis owns graph materialization and graph queries.

It should align with four upstream contract families:

```text
SourceOS sourceos-spec
  -> constitutional local-first graph, sync, channel, policy, and audit contracts

Prophet Platform contracts/identity
  -> platform-facing subject, session, and proof-ingress contracts

Identity Is Prime Reference
  -> deep proof artifacts, prime-topic policy reasoning, bounded linkage, examples

Regis Entity Graph
  -> temporal graph ontology, graph deltas, proof/witness attachment, replayable views
```

Regis is therefore a materialization layer, not a separate semantic authority.

---

## 2. Alignment with Prophet Platform identity contracts

Prophet Platform currently defines three identity contract surfaces:

- `IdentitySubjectContext`
- `IdentitySessionContext`
- `IdentityProofIngressRecord`

Regis should materialize these as graph objects instead of redefining them.

### 2.1 Subject context mapping

`IdentitySubjectContext` maps into the graph as a subject-family node:

- `PERSON` for human first-party subjects,
- `PSEUDONYM` for scoped subject presentations,
- `ROLE` for privileged operator or delegated authority contexts,
- `ORG` for institutional context when applicable,
- `SERVICE_WORKLOAD` when Regis adds workload node support.

The graph node should preserve:

- `subject_id`,
- `tenant_id`,
- `subject_class`,
- `assurance_context`,
- `credential_refs`,
- `policy_refs`,
- `created_at`.

### 2.2 Session context mapping

`IdentitySessionContext` maps into a `SESSION` graph node.

Regis should add `SESSION` as a canonical node kind.

The graph node should preserve:

- `session_id`,
- `subject_id`,
- `tenant_id`,
- `issued_at`,
- `expires_at`,
- `last_seen_at`,
- `assurance_context`,
- `stepup_state`,
- `risk_state`,
- `policy_refs`,
- `evidence_refs`.

### 2.3 Proof ingress mapping

`IdentityProofIngressRecord` maps into a `PROOF_INGRESS_RECORD` graph node.

Regis should add `PROOF_INGRESS_RECORD` as a canonical node kind, distinct from `PROOF_ARTIFACT`.

The difference is important:

- `PROOF_ARTIFACT` is the deep evidence object.
- `PROOF_INGRESS_RECORD` is the platform-facing accepted/rejected/inconclusive ingress summary.

The graph should connect them with `ATTESTED_BY_PROOF` or another explicit evidence edge.

---

## 3. Alignment with SourceOS graph direction

SourceOS graph work should be treated as the constitutional layer for local-first graph, identity, sync, policy, channel, and audit semantics.

Regis should be compatible with the following conceptual surfaces:

- `SourceIdentity`
- `SourceGraph`
- `SourceStore`
- `SourceSync`
- `SourcePolicy`
- `SourceChannel`
- `SourceAudit`

Until the SourceOS contracts stabilize fully, Regis should avoid hard-coding incompatible assumptions.

### 3.1 Regis as SourceGraph materialization

Regis should be able to serve as a materialized entity graph view under a SourceOS local-first graph architecture.

This means:

- graph deltas are append-friendly,
- graph state is replayable,
- proof and witness attachments are first-class,
- graph exports are policy-governed,
- sync does not silently widen identity exposure.

### 3.2 SourcePolicy alignment

Regis should not recompute policy semantics independently.

Policy decisions should arrive as:

- proof artifact refs,
- policy witness refs,
- graph delta reason codes,
- blocked/export/veto graph states.

Regis enforces graph invariants and materialization rules, but the policy lattice lives in the reasoning/policy layer.

### 3.3 SourceAudit alignment

Regis should preserve auditability by default:

- every node and edge has provenance,
- every veto or block has an artifact or witness,
- every graph version is replayable from deltas,
- no graph mutation silently destroys prior history.

This lets Regis participate in SourceOS audit surfaces without becoming the audit root by itself.

---

## 4. Required ontology patch

The existing Regis graph ontology should be extended with these node kinds:

- `SESSION`
- `PROOF_INGRESS_RECORD`
- `SERVICE_WORKLOAD`
- `SOURCE_GRAPH_VIEW`
- `SOURCE_AUDIT_RECORD`

Recommended meanings:

### 4.1 SESSION

A materialized platform session context, aligned to `IdentitySessionContext`.

### 4.2 PROOF_INGRESS_RECORD

A platform-facing proof ingress summary, aligned to `IdentityProofIngressRecord`.

### 4.3 SERVICE_WORKLOAD

A non-human workload subject, aligned to workload identity and service-agent contexts.

### 4.4 SOURCE_GRAPH_VIEW

A named materialized SourceGraph-compatible graph snapshot or view.

### 4.5 SOURCE_AUDIT_RECORD

A graph-native pointer to an audit record, receipt, or external evidence bundle.

---

## 5. Graph edge alignment

Regis should preserve the existing proof and governance edges and add platform/source alignment where needed.

Recommended edge usage:

- `ATTESTED_BY_PROOF`: subject/session/edge is backed by a proof artifact.
- `AUTHORIZED_BY_CONSENT`: action or edge is backed by consent witness.
- `OCCURS_IN_SCOPE`: event/session/object is scoped to a trust/exposure boundary.
- `EMITTED_EVENT`: subject/session/device emitted or participated in an event.
- `EXPORTS_TO`: controlled cross-boundary export.
- `BLOCKED_EXPORT`: rejected cross-boundary export.
- `MERGE_VETOED`: proposed entity merge rejected by policy or proof.

Future edge additions may include:

- `HAS_SESSION`
- `HAS_PROOF_INGRESS`
- `HAS_SOURCE_AUDIT_RECORD`
- `MATERIALIZED_AS_SOURCE_GRAPH_VIEW`

---

## 6. Evidence bundle alignment

Across the ecosystem, runtime claims are moving toward evidence bundles and receipts.

Regis should treat the following as related evidence objects:

- Identity Is Prime deep proof artifact,
- Prophet Platform `IdentityProofIngressRecord`,
- SourceOS / Agent Machine release evidence bundles,
- SourceOS audit records,
- Policy Fabric decision reports,
- AgentPlane execution ledgers.

The graph does not need to inline all evidence. It must preserve stable references and attachment edges.

---

## 7. Integration path

Use this integration order:

1. add platform and SourceOS alignment docs,
2. extend Regis node enum with `SESSION` and `PROOF_INGRESS_RECORD`,
3. accept graph deltas that attach proof ingress records,
4. materialize subject/session/proof nodes from platform contract examples,
5. validate replay and query behavior,
6. only then add broader SourceGraph compatibility surfaces.

---

## 8. Non-goals

This document does not implement:

- authentication,
- session storage,
- SourceOS sync engine behavior,
- Policy Fabric decision evaluation,
- proof verification,
- Agent Machine release validation.

It only aligns Regis graph materialization with those upstream contract surfaces.

---

## 9. Practical reading

Regis is the graph memory of identity decisions.

It should know:

- what subject/session/proof records exist,
- which evidence supports them,
- which exports or merges were blocked,
- which graph state existed at which version,
- and how to replay the graph from deltas.

It should not invent independent identity semantics.
