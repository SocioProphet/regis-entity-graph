# Authority Concordance Rex Entity/Evidence/Concordance Contracts

Version: v0.1
Status: draft spec-anchor
Owner: Regis Entity Graph

## Purpose

This specification defines the Authority Concordance Rex (ACR) contract surface for Regis Entity Graph. ACR is the entity, evidence, concordance, and decision-ledger plane for the sovereign civic computation stack. It preserves the existing Regis thesis that identity is prime, role-scoped, event-grounded, and proof-aware while adding the data-mastering contracts required for canonical entities, source records, concordance links, evidence claims, energy-aware resolution, and reversible relationship formation.

## Existing repository foundation

The current repository already states that identity is not a single profile but a product of irreducible roles or prime topics, and that the platform turns this into machine-checkable math, proofs, and enforcement in a citizen fog. It also frames typed Event-IR as the atomic substrate for logs, typed events, and proofs. This ACR surface extends that foundation by adding explicit entity/evidence/concordance records and decision-ledger objects.

## Control-plane alignment

SocioSphere coordinates the cross-estate alignment and conformance lane. Regis Entity Graph implements the entity/evidence/concordance lane.

Related lanes:

- Ontogenesis supplies formation, lifecycle, validity, and derivation semantics.
- SourceOS supplies local-first custody, sync intent, proof emission, and citizen-node runtime behavior.
- Prophet Platform consumes decision ledgers for governance workflow, review, appeal, and policy simulation.
- Policy Fabric supplies executable promotion, survivorship, capability, and governance policy packs.
- TriTRPC and AgentPlane carry proof-bearing requests and scoped capabilities.

## Contract set

### CanonicalEntity

A stable entity projection derived from source records, evidence claims, concordance links, and decision-ledger entries under a versioned policy.

Required semantics:

- Identity is stable; attributes are revisable.
- Canonical state must be replayable from evidence and decisions.
- Entity roles must remain compatible with identity-is-prime constraints.
- Canonical projection must not collapse protected citizen scopes into unsafe aggregate identities.

### SourceRecord

A source-system assertion preserved with raw payload, normalized payload, source identity, contract-validation report, and ingestion metadata.

Required semantics:

- Raw source values are preserved.
- Normalized values are versioned by normalization policy.
- Contract validation errors and warnings are retained.
- Source records can be reprocessed under new policy without losing original evidence.

### ConcordanceLink

A crosswalk edge from a source record to a canonical entity.

Required semantics:

- Links have status: active, pending_review, rejected, superseded, disputed.
- Links carry confidence, resolver run, policy version, and explanation codes.
- Links are not merges by themselves; they are evidence-backed mappings.

### EvidenceClaim

A typed assertion extracted from a source record, document, event, credential, ontology graph, or human stewardship action.

Required semantics:

- Claims carry provenance, confidence, scope, and policy context.
- Claims can be atomic, composed, relational, lifecycle, credential, or event-derived.
- Claims do not overwrite canonical state without promotion.

### DecisionLedgerEntry

An append-only explanation for a match, non-match, merge, split, promotion, rejection, override, or stewardship act.

Required semantics:

- Decisions bind evidence, candidates, policy, actor or agent, reason codes, and replay metadata.
- High-stakes decisions support review and appeal semantics.
- Merge and split decisions preserve prior states and derivation paths.

### EnergyLedgerEntry

A resolver-energy accounting object that records candidate scores, top-vs-runner-up margin, stability checks, policy thresholds, and promotion decision.

Required semantics:

- Resolution margin is first-class.
- Low-margin or unstable resolution is blocked from canonical promotion.
- Positive-evidence-only mode is supported for multi-entity evidence contexts.

### PromotionPolicy

A versioned policy controlling the transition from raw evidence to review, evidence-only insertion, concordance link activation, or canonical projection.

Required semantics:

- Promotion uses thresholds, margin, conflict budget, stability, and policy flags.
- Canonical promotion requires a decision-ledger entry.
- Sensitive or citizen-impacting transitions require review/appeal hooks where applicable.

### RelationshipFormationHook

A bridge object that connects ACR relationships to Ontogenesis lifecycle semantics.

Required semantics:

- Relationship formation references evidence, decision ledger, validity interval, and derivation path.
- Relationship states can be proposed, active, disputed, revoked, superseded, merged, split, or retired.

## Relationship to identity-is-prime

ACR must not become a conventional entity-resolution system that merges every observable record into a single flat person or organization profile. The existing Regis foundation treats identity as a product of irreducible prime topics and uses policy constraints to forbid unsafe mixtures. ACR therefore resolves entities under scope, role, realm, and policy constraints.

Examples of forbidden behavior:

- silently joining health, child, civic, and advertising realms into one behavioral profile
- treating agent access logs as citizen consent
- using downstream enrichment to override citizen-local canonical state without sync intent
- promoting low-margin candidate matches into canonical identity

## Relationship to Ontogenesis

ACR produces the identity/evidence side of formation. Ontogenesis supplies lifecycle validity and becoming semantics.

Mapping:

- CanonicalEntity formation maps to EntityFormationRecord.
- ConcordanceLink activation maps to RelationshipFormationRecord where needed.
- DecisionLedgerEntry maps to GovernanceAct for stewarded or policy-governed decisions.
- RelationshipFormationHook maps to GenesisEvent, ValidityInterval, and DerivationPath.

## Minimal implementation tranche

1. Add machine-readable schema bundle for the ACR contract set.
2. Add examples for source record, canonical entity, concordance link, decision ledger, energy ledger, and promotion policy.
3. Add a reversible merge/split example.
4. Add an Ontogenesis relationship formation example hook.
5. Add validation tooling or a Makefile target that can validate schemas and examples.

## Acceptance criteria

- Every contract has a schema.
- Every schema has at least one example.
- Every canonical transition references a decision-ledger entry.
- Every decision-ledger entry references policy version and evidence.
- Every relationship formation can bind to Ontogenesis lifecycle semantics.
- Every citizen-impacting promotion can be reviewed, appealed, or blocked by policy.
