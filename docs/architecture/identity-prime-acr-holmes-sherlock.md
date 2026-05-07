# Regis Entity Graph: Identity Is Prime, ACR, Holmes, Sherlock, and MeshRush

## Purpose

This document defines how Regis Entity Graph receives and operationalizes the Sociosphere Identity Is Prime conformance slice.

Sociosphere now tests the cross-repo contract for Identity Is Prime, Authority Concordance Rex (ACR), Agent Registry, MeshRush, Holmes, and Sherlock Search. Regis is the graph and evidence semantics layer that owns canonical graph objects, identity states, evidence relationships, decision ledger pointers, and proof certificate pointers.

## Product boundary

Regis is not a search index, not a case-management UI, and not the ACR resolver itself. Regis stores graph/evidence semantics and accepts only policy-reduced graph mutations.

- Identity Is Prime supplies the doctrine and policy math.
- ACR supplies concordance, source-to-canonical crosswalks, and golden projection proofs.
- MeshRush explores Regis graph views and produces simulation/evidence traces.
- Holmes reasons over Regis graph, MeshRush traces, ACR proofs, and policy refutations.
- Sherlock Search indexes and retrieves pointer-backed evidence without writing canonical truth.
- Agent Registry declares which agents may submit observations, proposed mutations, certificates, search records, and case findings.

## Required Regis object families

The Sociosphere conformance lane expects Regis to expose or accept these graph object families:

- `IdentityPrime`
- `ScopeFlag`
- `IdentityState`
- `IdentityMixture`
- `IdentityPolytope`
- `WorldlineEvent`
- `AdmissibleTransition`
- `TokenLane`
- `ProofCertificate`
- `TransitionCertificate`
- `NonEscapeCertificate`
- `ConcordanceDecisionCertificate`
- `CanonicalEntity`
- `SourceRecord`
- `ConcordanceLink`
- `DecisionLedgerEntry`
- `SearchIndexRecord`
- `InvestigationCase`
- `EvidenceFinding`
- `MeshRushSimulationTrace`

## Truth discipline

Regis accepts four kinds of upstream material:

1. Assertions: source assertions, extracted evidence, identity prime assignments.
2. Decisions: resolver decisions, survivorship decisions, policy decisions.
3. Certificates: proof artifacts, no-path refutations, non-escape certificates.
4. Proposed mutations: graph changes submitted by agents and reduced by policy.

Regis must reject direct canonical truth writes from agents. Canonical truth requires a policy-reduced mutation or an ACR-backed concordance/golden-record proof.

## Graph edge semantics

Minimum edge vocabulary:

- `ASSERTS`
- `CONCORDS_TO`
- `HAS_PRIME`
- `HAS_SCOPE`
- `TRANSITIONS_TO`
- `OBSERVED_TOKEN`
- `MINTED_TOKEN`
- `PROVES`
- `REFUTES`
- `SUPPORTED_BY_EVIDENCE`
- `CITES_LEDGER`
- `CITES_CERTIFICATE`
- `INDEXES`
- `DERIVED_FROM_TRACE`
- `CROSSES_BOUNDARY`
- `GOVERNED_BY_POLICY`

## Determinism and replay pins

Every object participating in conformance should carry relevant version pins:

- `schema_version`
- `policy_version`
- `resolver_version`, when ACR participates
- `template_version`, when ACR participates
- `simulation_version`, when MeshRush participates
- `case_model_version`, when Holmes participates
- `index_version`, when Sherlock participates
- `fixture_version`, when a Sociosphere fixture participates
- `ledger_pointer`
- `certificate_hash`

## Acceptance alignment

Regis alignment is complete when the graph schemas can receive the Sociosphere fixtures for:

- forbidden patient + ad-tech identity mixtures
- token non-escape violations
- no-admissible-path refutations
- ACR golden-record proofs
- MeshRush simulation traces
- Holmes investigation cases
- Sherlock pointer-backed search records
- agent-submitted evidence with canonical-truth write guards
