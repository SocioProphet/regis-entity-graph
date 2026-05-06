# Prophet Platform Service Binding for Regis / ACR

Version: v0.1
Status: draft service-binding spec
Owner: Regis Entity Graph
Runtime home: `SocioProphet/prophet-platform`
Service target: `regis-acr-api`

## Purpose

This document defines how Regis Entity Graph / Authority Concordance Rex (ACR) moves from domain contracts into a deployable Prophet Platform service.

Regis remains the canonical domain home for entity, evidence, concordance, identity-prime scope protection, decision-ledger, energy-ledger, and Ontogenesis relationship-formation semantics. Prophet Platform is the runtime and deployment hub where those contracts become deployable services, smoke-tested APIs, platform receipts, and Kubernetes-ready deployment assets.

## Ownership split

| Concern | Canonical owner |
|---|---|
| ACR domain semantics | `SocioProphet/regis-entity-graph` |
| ACR schemas and examples | `SocioProphet/regis-entity-graph` |
| ACR service runtime | `SocioProphet/prophet-platform/apps/regis-acr-api` |
| Platform-facing contracts | `SocioProphet/prophet-platform/contracts/acr` |
| Platform smoke/validation | `SocioProphet/prophet-platform/tools` and `Makefile` |
| Cross-estate coordination | `SocioProphet/sociosphere` |
| Lifecycle binding | `SocioProphet/ontogenesis` |
| Policy gates | `SocioProphet/policy-fabric` |

## Domain-to-runtime contract projection

The ACR contract pack in this repository is the normative domain source. Prophet Platform should mirror or adapt it into platform-facing request/response contracts.

Required projection:

- `SourceRecord` -> `RegisAcr.IngestSourceRecord.REQ`
- `EvidenceClaim` -> `RegisAcr.IngestSourceRecord.RES.evidence_claims[]`
- `ConcordanceLink` -> `RegisAcr.ProposeConcordance.RES.concordance_links[]`
- `PromotionPolicy` + resolver scores -> `RegisAcr.EvaluatePromotion.REQ`
- `EnergyLedgerEntry` -> `RegisAcr.EvaluatePromotion.RES.energy_ledger_entry`
- `DecisionLedgerEntry` -> all consequential responses
- `RelationshipFormationHook` -> `RegisAcr.EmitRelationshipFormationHook.RES.relationship_formation_hook`

## Service methods

Initial platform service surface:

- `GET /healthz`
- `POST /v1/source-records`
- `POST /v1/concordance/proposals`
- `POST /v1/promotion/evaluate`
- `POST /v1/relationships/formation-hooks`

TriTRPC method names reserved for the internal platform binding:

- `RegisAcr.Health.Ping`
- `RegisAcr.IngestSourceRecord`
- `RegisAcr.ProposeConcordance`
- `RegisAcr.EvaluatePromotion`
- `RegisAcr.EmitDecisionLedger`
- `RegisAcr.EmitRelationshipFormationHook`

## Safety invariants

### No automatic canonical mutation in the first tranche

The runtime service may ingest evidence and propose concordance, but it must not perform irreversible canonical merge or split automation in the bootstrap tranche.

### Evidence-first promotion

Source records and extracted evidence become evidence objects before they become canonical state. Evidence does not overwrite truth.

### Low-margin protection

Energy-ledger outputs with low top-vs-runner-up margin, high winner-flip rate, or conflicting policy flags must be blocked or routed to review.

### Identity-prime protection

The service must preserve protected identity-prime scope boundaries. Health, child, civic, advertising, agent, and device scopes must not be silently collapsed into an unsafe aggregate profile.

### Ontogenesis hook discipline

Relationship formation hooks are emitted for Ontogenesis binding. They are not forced into active lifecycle state without Ontogenesis validation, policy basis, and decision-ledger trace.

## Required platform receipts

Every consequential service action should emit or return receipt metadata with:

- correlation id
- service name
- action
- subject reference
- status
- payload reference
- event reference
- receipt reference
- created timestamp

Required actions:

- `SourceRecordIngest`
- `ConcordanceProposal`
- `PromotionEvaluation`
- `DecisionLedgerWrite`
- `RelationshipFormationHook`

## Deployment readiness gates

Regis is considered platform-integrated when Prophet Platform can pass:

- `make validate-regis-acr-integration`
- `make smoke-regis-acr-service`

Minimum smoke coverage:

1. health endpoint returns service identity and contract list
2. source-record ingest returns evidence claim and decision-ledger entry
3. concordance proposal returns pending-review link, not canonical mutation
4. promotion evaluation blocks low-margin candidate
5. promotion evaluation allows only evidence-first eligible candidate when gates pass
6. relationship-formation hook returns Ontogenesis binding requirements

## Regis-side acceptance criteria

This repository must provide:

- ACR contract pack manifest
- schemas for core ACR domain objects
- examples for core ACR flows
- this Prophet Platform binding document
- clear statement that Prophet Platform is the runtime deployment home

## Prophet-side acceptance criteria

Prophet Platform must provide:

- `apps/regis-acr-api/`
- `contracts/acr/regis-acr-platform-contract.yaml`
- service smoke tests
- integration validation tooling
- Makefile targets
- Kustomize or local deployment profile in a follow-on tranche

## Implementation status

Initial platform service bootstrap has started in `SocioProphet/prophet-platform` with a fixture-backed FastAPI service and platform contract. Regis now records the domain-to-runtime binding from the domain side so SocioSphere, Regis, and Prophet Platform agree on where each responsibility lives.
