# Identity personhood and sigil graph contract v0.1

## Status

Contract-only companion lane for materializing HolographMe `PersonhoodBindingRecord` and `IdentitySigilSeal` artifacts into Regis Entity Graph.

This document does not replace base graph schemas, epistemic edge records, proof ingress records, or runtime graph storage. It defines the graph materialization target so person-bound identity does not collapse into object-bound identity.

## Purpose

HolographMe now distinguishes:

- `PersonhoodBindingRecord`: governed continuity claim that a living human subject controls or authorizes an identity mesh;
- `IdentitySigilSeal`: human-facing presentation and authority surface downstream of personhood binding.

Regis must preserve that distinction in graph form.

The graph must be able to represent personhood, sigil presentation, signing authority, delegation, reputation, consent, and transition receipts without letting wallets, portraits, accounts, devices, agents, or reputation scores become the person.

## Required graph node classes

The next schema tranche should support these node classes, either directly or as typed attributes on existing generic nodes:

- `PERSONHOOD_BINDING`
- `BINDING_CEREMONY`
- `IDENTITY_MESH_SUBJECT`
- `HUMAN_DIGITAL_TWIN_REF`
- `SIGIL_ARTIFACT`
- `IDENTITY_SIGIL_SEAL`
- `PORTRAIT_PRESENTATION_POLICY`
- `SIGNING_AUTHORITY`
- `AGENT_DELEGATION_SEAL`
- `DELEGATED_ACTION_RECEIPT`
- `CONTEXTUAL_REPUTATION_CREDENTIAL`
- `RECOVERY_POLICY`
- `REVOCATION_POLICY`
- `GUARDIAN_OR_WITNESS_ATTESTATION`
- `LIVENESS_OR_PRESENCE_EVIDENCE`
- `CREDENTIAL_ATTESTATION`
- `CONSENT_RECEIPT`
- `TRANSITION_RECEIPT`
- `POLICY_DECISION`

## Required graph edge classes

The next schema tranche should support these edge classes:

- `PERSON_BOUND_TO_SUBJECT`
- `SUBJECT_GOVERNS_TWIN`
- `SUPPORTED_BY_EVIDENCE_CLASS`
- `WITNESSED_BY`
- `RECOVERABLE_BY`
- `REVOCABLE_BY`
- `SUBJECT_HAS_SIGIL_SEAL`
- `SEAL_HAS_SIGIL`
- `SEAL_HAS_PORTRAIT_POLICY`
- `SEAL_CONTROLLED_BY_AUTHORITY`
- `AUTHORITY_SCOPED_TO`
- `DELEGATES_TO_AGENT`
- `EMITS_ACTION_RECEIPT`
- `ATTESTS_CONTEXTUAL_REPUTATION`
- `PROJECTED_UNDER_CONSENT`
- `ALLOWED_BY_POLICY`
- `DENIED_BY_POLICY`
- `RECORDED_BY_TRANSITION_RECEIPT`

## Required invariants

A valid graph materialization must preserve these invariants:

1. A personhood binding must not be materialized from a single object class.
2. A wallet, account, device, portrait, credential, agent, or reputation node must not become the person node.
3. `IDENTITY_SIGIL_SEAL` must reference a `PERSONHOOD_BINDING` before it may be treated as person-bound presentation.
4. A portrait edge must carry a non-biometric-default policy or remain non-active / advisory.
5. A signing authority edge must declare scope and forbidden scopes.
6. A delegation edge must reference consent, expiry or revocation posture, and authority band.
7. A reputation edge must declare context and must not imply global human worth.
8. Recovery and revocation paths must be graph-visible for root personhood binding.
9. Graph edges derived from model, summary, extraction, or projection must carry epistemic edge companion records.
10. Public projection must not expose all linked identity contexts unless explicitly approved by policy and consent.

## Epistemic edge posture

The existing Regis epistemic edge lane remains mandatory for high-consequence identity relations.

Examples:

- `reported_relation`: a human says a guardian witnessed a ceremony.
- `observed_relation`: a signed transition receipt records a ceremony step.
- `confirmed_relation`: reviewed evidence supports the personhood binding relation.
- `operational_relation`: a currently active signing authority or delegation relation.
- `contested_relation`: a challenged witness, credential, or reputation relation.

A model-extracted or inferred edge must not become a confirmed personhood edge without evidence and review. No graph goblin gets to put on a judge wig.

## Minimum fixture target

The first executable graph fixture should model:

- one `PERSONHOOD_BINDING` for `sub_example_alpha`;
- one `IDENTITY_SIGIL_SEAL` referencing that binding;
- one scoped DID signing authority;
- one wallet signing authority explicitly barred from `personhood_claim`;
- one guardian/witness attestation edge;
- one recovery policy edge;
- one contextual reputation edge;
- one transition receipt edge;
- companion non-claims preventing person/account/wallet/portrait/agent/reputation collapse.

## Rejected fixture targets

The first rejected graph fixtures should include:

- wallet-only personhood graph;
- portrait-only or biometric-default graph;
- sigil seal without personhood binding;
- global public correlation of all identity contexts;
- reputation edge claiming global human worth;
- delegation edge without consent or revocation posture.

## Non-claims

This document does not implement runtime graph writes.

This document does not define legal identity proofing.

This document does not make any wallet, portrait, account, device, credential, agent, score, or graph edge equivalent to the person.

This document does not authorize public correlation of all identity contexts.
