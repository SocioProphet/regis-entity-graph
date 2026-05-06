# Regis Entity Graph Framework (REGIS)

## Purpose
REGIS is a deterministic, versioned, auditable entity graph framework whose primary deliverables are (1) canonical entities and (2) a concordance (crosswalk) map from source identifiers to canonical identifiers. A point-in-time “golden record” is defined by an explicit replay key (time + resolver version + policy pack version + authority template version), enabling reproducibility and audit.

## Core Concepts
### Canonical Entity (CE)
A stable entity representing the framework’s canonical view. Identifier: **CEID** (e.g., `CE-...`).

### Source Record Reference (SR)
A stable reference to a record in an upstream system:
- `source_id`
- `source_record_id`

### Assertion
A typed, provenance-carrying claim from a source about an entity attribute, including observation/effective timestamps.

### Concordance / Crosswalk
The mapping `(source_id, source_record_id) -> CEID` with confidence and ledger pointers.

### Golden Record
A versioned projection of a CE under an authority template version and policy pack version at an `as_of_time`.

### Decision Ledger
An append-only log of merges/splits/promotions/overrides with Decision IDs (DID) and Resolution Run IDs (RID). All externally visible results MUST carry version pins and ledger pointers.

## Storage Spine (v1)
REGIS is cache-first and requires four logical stores:
1. **Assertion Cache (AC)**: assertions keyed by `(source_id, source_record_id, attribute_path, effective_at)`.
2. **Crosswalk Cache (CC)**: crosswalk entries keyed by `(source_id, source_record_id)`.
3. **Golden Projection Cache (GC)**: materialized projections keyed by `(ceid, as_of_time, template_version, policy_version)`.
4. **Decision Ledger (DL)**: immutable decisions and traces keyed by `(did, rid)`.

## Deterministic Replay Key
A golden record is defined by the tuple:
- `as_of_time`
- `resolver_version`
- `policy_version`
- `template_version`

This tuple must be included in responses to ensure reproducibility.

## Connector + Schema Evolution
Connectors are versioned and must emit Schema Change Events for:
- field add/remove/rename
- type change
- semantic change
- keying strategy change

Mappings from source schema versions to authority template versions must be validated and versioned.

## Resolution Engine
Resolvers are pluggable and must emit:
- candidate set
- scores
- decision (merge/split/link/no-link)
- explainability trace
- ledger entries (RID/DID)

### Safety Lane (unstructured evidence)
For multi-entity unstructured contexts, apply positive-evidence-only by default; track the score margin `Δ = s1 - s2` and use review/insert thresholds to gate promotions.

## TRIT RPC Surface (v1)
Minimum service RPCs:
- `IngestAssertions(source_id, records[]) -> IngestResult`
- `ResolveEntity(entity_hint | source_record_ref) -> ResolutionResult`
- `GetCrosswalk(source_id, source_record_id) -> Crosswalk`
- `GetGolden(ceid, as_of_time?, template_version?, policy_version?) -> GoldenRecord`
- `SimulatePolicyChange(target, from_policy, to_policy) -> DiffReport`
- `OverrideDecision(did, action, reason) -> OverrideResult`

All responses must include:
- `template_version`
- `policy_version`
- `resolver_version`
- `ledger_pointer` (RID/DID)

## Incremental Delta Mechanics
On ingestion, compute the impacted SR/CE set via CC, resolve only impacted items, and update GC with compact diffs. Avoid full reprocessing unless a global policy/template migration is requested.

## Roadmap
- v1.1: Energy ledger + stronger promotion policies.
- v2+: Proof-carrying linkage (Event-IR + ProveLinkage/VerifyCert style certificates).
