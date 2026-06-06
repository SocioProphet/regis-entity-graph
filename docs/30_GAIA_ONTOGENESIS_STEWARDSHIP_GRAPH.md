# Gaia Ontogenesis Stewardship Graph Contract

## Purpose

This document defines the Regis Entity Graph contract target for IOES materialization.

IOES means Identity, Ontogenesis, Ecology, and Stewardship.

Regis should not merely remember entity matches, proof ingress, and policy state. It should materialize living developmental relationships: what persists, what develops, what interconnects, and what is entrusted.

## Position

Regis is the graph memory of governed identity and evidence decisions.

For IOES, Regis becomes the materialization surface for:

Identity continuity.

Ontogenesis state.

Gaia dependency and impact context.

Stewardship relations.

Keeper logs.

Succession posture.

Policy and evidence bindings.

Regis does not decide policy, run agents, or define curriculum. It records graph state and preserves replayable provenance.

## New node kinds

The schema should eventually support these node kinds.

LIVING_ENTITY

ONTOGENESIS_STATE

GAIA_DEPENDENCY_RECORD

STEWARDSHIP_RECORD

KEEPER_LOG

SUCCESSION_RULE

ABANDONMENT_SIGNAL

LEARNING_ARTIFACT

DELIVERY_OUTCOME_RECORD

POLICY_DECISION

CONSENT_RECEIPT

PROJECTION_RECORD

These may initially be represented through existing node kinds with typed attrs, but they should become explicit once the schema is expanded.

## New edge kinds

The schema should eventually support these edge kinds.

STEWARD_OF

GUARDIAN_OF

MENTOR_OF

APPRENTICE_OF

SUCCESSOR_OF

PRESERVES

TRANSMITS_TO

CARES_FOR

HAS_KEEPER_LOG

HAS_SUCCESSION_RULE

HAS_ABANDONMENT_SIGNAL

HAS_ONTOGENESIS_STATE

DEPENDS_ON

CONTRIBUTES_TO

IMPACTS

CO_EVOLVES_WITH

REGENERATES

DEGRADES

AUTHORIZED_BY_CONSENT

ALLOWED_BY_POLICY

DENIED_BY_POLICY

ATTESTED_BY_PROOF

EMITTED_BY_EXECUTION

HAS_DELIVERY_OUTCOME

HAS_LEARNING_CHANGESET

## StewardshipEdge

A StewardshipEdge records responsibility without ownership.

Minimum fields:

edge_id

kind

src

dst

status

scope

duties

limits

authority_refs

consent_refs

policy_refs

evidence_refs

keeper_log_refs

succession_rule_refs

valid_time

system_time

provenance

Required invariant:

A stewardship edge must not imply ownership unless a separate ownership edge or authority artifact exists.

## OntogenesisState

An OntogenesisState records developmental phase and trajectory.

Minimum fields:

state_id

entity_ref

phase

phase_history

entered_at

review_status

confidence

evidence_refs

policy_refs

review_refs

next_phase_candidates

blocked_transition_reasons

repair_refs

Allowed generic phases:

seed

formation

growth

maturity

transmission

transformation

decline

succession

archive

termination

Domain profiles may refine these phases for learners, projects, repositories, theories, organizations, communities, and ecosystems.

Required invariant:

Model inference alone must not promote developmental state to canonical human-impacting truth.

## GaiaDependencyRecord

A GaiaDependencyRecord records ecological, community, infrastructure, standards, energy, evidence, or knowledge dependencies.

Minimum fields:

record_id

entity_ref

dependency_ref

dependency_type

criticality

reciprocity

impact_direction

risk_state

steward_refs

evidence_refs

policy_refs

review_interval

valid_time

provenance

Dependency types may include:

community

family

education

energy

water

food

infrastructure

software

compute

language

standards

evidence_source

jurisdiction

ecosystem

Required invariant:

Material dependencies must not be stripped merely to simplify projection or execution.

## KeeperLog

A KeeperLog records continuity of stewardship.

Minimum fields:

log_id

stewardship_ref

keeper_ref

accepted_at

authority_refs

consent_refs

duty_scope

review_interval

last_reviewed_at

review_records

handoff_records

termination_records

provenance

Required invariant:

A stewardship record without an active keeper should become needs_review or orphaned, not silently remain healthy.

## SuccessionRule

A SuccessionRule records how responsibility transfers.

Minimum fields:

rule_id

stewardship_ref

primary_keeper_ref

successor_refs

transfer_conditions

abandonment_threshold

emergency_authority_refs

review_required

policy_refs

consent_refs

valid_time

provenance

Required invariant:

Automated succession must require explicit rule authority and must preserve a review trail.

## AbandonmentSignal

An AbandonmentSignal records risk that stewardship is failing.

Minimum fields:

signal_id

stewardship_ref

signal_type

severity

detected_at

evidence_refs

repair_recommendation

policy_refs

status

Signal types may include:

no_active_keeper

no_successor

review_overdue

broken_contact

stale_evidence

contested_authority

critical_dependency_failed

orphaned_artifact

Required invariant:

Abandonment is a graph state, not absence of graph data.

## First graph delta scenario

The first fixture should model a kept learning artifact.

Nodes:

Living entity for learner or community.

Learning artifact.

Evidence bundle.

Stewardship record.

Keeper log.

Succession rule.

Policy decision.

AgentPlane execution evidence.

Delivery outcome record.

Edges:

STEWARD_OF from keeper to artifact.

SUCCESSOR_OF from successor candidate to keeper role or stewardship record.

HAS_KEEPER_LOG from stewardship record to keeper log.

HAS_SUCCESSION_RULE from stewardship record to succession rule.

ATTESTED_BY_PROOF from artifact and stewardship record to evidence.

ALLOWED_BY_POLICY or DENIED_BY_POLICY from promotion attempt to policy decision.

EMITTED_BY_EXECUTION from graph delta to AgentPlane evidence.

HAS_DELIVERY_OUTCOME from learning artifact to Delivery Excellence record.

## Non-goals

This document does not change the current Regis JSON schemas.

It does not implement RDF, OWL, SHACL, or validators.

It defines the graph materialization contract for the next schema tranche.

## Next implementation targets

Extend node and edge enums.

Add stewardship-edge schema.

Add ontogenesis-state schema.

Add gaia-dependency-record schema.

Add keeper-log schema.

Add succession-rule schema.

Add abandonment-signal schema.

Add valid and rejected graph delta fixtures.

Add validator coverage.
