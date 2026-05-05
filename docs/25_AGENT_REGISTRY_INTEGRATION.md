# Agent Registry Integration

This document defines the Regis Entity Graph integration stance for Agent Registry grant and authorization surfaces.

Agent Registry is an authority surface for non-human runtime participants. Regis should materialize Agent Registry grants, revocations, scopes, and activation evidence as graph state without becoming the grant resolver itself.

The naming relationship is intentional: a registry is a governed record of authority, identity, and scope. Regis should be the graph memory of those registry decisions, not a competing registry implementation.

---

## 1. Boundary statement

Regis owns:

- graph materialization of agent identity, grants, revocation, and evidence references;
- graph query and replay of registry-derived relationships;
- proof and audit attachment to agent/runtime graph state;
- temporal visibility into active, expired, denied, and revoked grants.

Agent Registry owns:

- local grant resolution;
- agent identity and requested scope resolution;
- active/missing/expired/revoked/denied/unknown grant status;
- allowed and denied provider/model/tool/cache/memory/storage/evidence scopes;
- revocation hook requirements;
- fail-closed activation decisions when no valid local grant exists.

Regis must not silently authorize an agent. It may only materialize the results of Agent Registry, Policy Fabric, Agent Machine, AgentPlane, and related evidence surfaces.

---

## 2. Ecosystem position

The intended relationship is:

```text
AgentPod / non-human runtime participant
  -> Policy Fabric admission
  -> Agent Registry grant request
  -> optional external verifier inputs
  -> local grant resolution
  -> Agent Machine ActivationDecision
  -> runtime placement or fail-closed
  -> Regis graph materialization of the grant/evidence state
```

Regis records the fact that a grant existed, was denied, expired, or was revoked. It does not decide the grant.

---

## 3. Graph objects Regis should materialize

Regis should be prepared to materialize these Agent Registry concepts as graph nodes and edges.

### 3.1 Recommended node kinds

The current Regis schema should support or later add:

- `SERVICE_WORKLOAD`
- `AGENT_IDENTITY`
- `AGENT_POD`
- `AGENT_REGISTRY_GRANT`
- `ACTIVATION_DECISION`
- `REVOCATION_RECORD`
- `EXTERNAL_TRUST_SIGNAL`
- `POLICY_DECISION`
- `SOURCE_AUDIT_RECORD`

If the initial schema only has `SERVICE_WORKLOAD` and `SOURCE_AUDIT_RECORD`, the other objects may be represented temporarily as typed `CREDENTIAL`, `PROOF_ARTIFACT`, or `SOURCE_AUDIT_RECORD` nodes until the enum is expanded.

### 3.2 Recommended edge kinds

Regis should support or later add:

- `REQUESTS_GRANT`
- `RESOLVED_BY_GRANT`
- `AUTHORIZED_BY_GRANT`
- `DENIED_BY_GRANT`
- `REVOKED_BY`
- `HAS_REVOCATION_HOOK`
- `HAS_ALLOWED_SCOPE`
- `HAS_DENIED_SCOPE`
- `HAS_EXTERNAL_TRUST_SIGNAL`
- `ADMITTED_BY_POLICY`
- `ACTIVATED_BY_DECISION`
- `BLOCKED_BY_DECISION`
- `ATTESTED_BY_PROOF`
- `HAS_SOURCE_AUDIT_RECORD`

The first schema slice may model some of these through generic `ATTESTED_BY_PROOF`, `HAS_SOURCE_AUDIT_RECORD`, `DELEGATES_TO`, or `BLOCKED_EXPORT` edges, but the registry concepts should be explicit in follow-up schemas.

---

## 4. Grant state materialization

Agent Registry grant state should be graph-visible.

Minimum state to preserve:

- requested agent identity ref;
- session ref;
- workroom/topic refs;
- requested provider/model/tool/cache/memory/storage/evidence scopes;
- resolved grant status;
- authorization flag;
- grant ref and digest;
- expiration;
- revocation status;
- revocation hook ref;
- allowed scope;
- denied scope;
- external trust signal refs when present.

This is graph data, but not raw secrets. Regis must preserve the SourceOS safety boundary: no raw prompts, KV-cache material, private memory, API keys, wallet private keys, raw credentials, or raw user data in registry-derived graph nodes.

---

## 5. External trust signal posture

External identity, reputation, certificate-tier, counterparty, or registry inputs can be useful. They are not the Agent Registry.

When such signals appear, Regis should materialize them as non-authoritative verifier inputs.

The graph should preserve:

- provider ref;
- signal type;
- signal ref;
- digest when available;
- verification time;
- authority classification, especially `non-authoritative-verifier-input`.

Regis must not promote an external signal into authorization unless the local Agent Registry grant and Policy Fabric decision allow it.

---

## 6. Fail-closed graph representation

Fail-closed activation paths should be graph-visible.

Examples:

- grant required but missing;
- grant expired;
- grant revoked;
- requested provider absent from allowed scope;
- requested tool absent from allowed scope;
- revocation hook missing;
- unsafe payload included prohibited material.

Regis should materialize these as blocked or denied states, not as absent data. A missing edge is not enough; operators need to see why activation failed.

---

## 7. Relationship to MeshRush

Agent Registry and MeshRush are related but different.

Agent Registry decides whether a non-human runtime participant has an active grant for a requested scope.

MeshRush operates over graph views once an agent is authorized to perform graph operations.

Therefore:

```text
Agent Registry controls whether the agent may act.
Regis materializes the grant and graph view.
MeshRush governs how the authorized agent moves through the graph view.
```

MeshRush should not operate over graph views unless the relevant agent identity and capability scope have an active registry grant or equivalent local authorization.

---

## 8. Graph delta implications

When Identity Is Prime, Agent Machine, AgentPlane, or Policy Fabric emits registry-related evidence, Regis should accept graph deltas that materialize:

- service workload / agent identity nodes;
- grant nodes;
- activation-decision nodes;
- revocation-record nodes;
- external-trust-signal nodes;
- proof and audit attachment edges;
- denied/blocked activation edges.

Recommended delta actions remain:

- `UPSERT_NODE`
- `UPSERT_EDGE`
- `ATTACH_ARTIFACT`
- `ATTACH_WITNESS`
- `REVOKE_EDGE`
- `EXPIRE_NODE`
- `EXPIRE_EDGE`

Additional registry-specific deltas can be added once the graph materializer exists.

---

## 9. Non-goals

This document does not implement:

- Agent Registry grant resolution;
- Agent Machine activation;
- Policy Fabric admission;
- external trust signal verification;
- MeshRush traversal;
- graph runtime mutation.

It only defines how Regis should represent registry-derived authority state.

---

## 10. Practical reading

Regis should remember who or what was allowed to act, under what scope, for how long, with which revocation hook, and backed by which evidence.

Agent Registry is the local authority resolver.
Regis is the graph memory of that resolver.
MeshRush is the graph operation runtime that must respect it.
