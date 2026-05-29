# Epistemic edge typing v0.1

## Status

Contract-only companion lane for Regis Entity Graph edge records.

This tranche consumes ProCybernetica Reciprocal Channel Governance and the Ontogenesis `rcg:` semantic mirror. It does not replace `schemas/edge.schema.json`, graph deltas, proof-ingress records, or runtime graph storage.

## Purpose

Entity graph edges are high-consequence projections. A graph edge can make an ambiguous text extraction, model inference, ASR transcript, dashboard projection, or agent report look like objective graph truth. Regis must preserve the epistemic status of each relation before the edge is used for search, traversal, merge, export, policy, or memory promotion.

The base edge schema already carries identity, kind, endpoints, status, valid time, system time, and provenance. This lane adds a companion record that explains what kind of knowledge the edge represents and what it may affect.

## Rule

No durable graph edge without evidence class, source channel, promotion state, temporal scope where relevant, and allowed consumers.

Inferred edges must not masquerade as confirmed edges.

## Epistemic edge classes

- `reported_relation` — stated by a human, document, connector, or other source but not independently confirmed.
- `observed_relation` — directly observed by an instrumented event, trace, receipt, or source artifact.
- `extracted_relation` — parsed or extracted from text, OCR, transcript, model output, or structured source.
- `inferred_relation` — produced by a model, resolver, scorer, matcher, or graph algorithm.
- `confirmed_relation` — reviewed and supported by sufficient evidence and policy.
- `legal_contractual_relation` — legally operative only when backed by contract or authoritative legal artifact.
- `operational_relation` — current runtime/workflow relation with expiry or revalidation rules.
- `hypothetical_relation` — analytic or planning relation that must not be treated as active.
- `superseded_relation` — replaced by a newer relation or reconciliation record.
- `contested_relation` — disputed by evidence, policy, user correction, or another graph record.

## Required companion metadata

An epistemic edge record should declare:

1. `edgeRef` pointing to the base graph edge;
2. epistemic class;
3. source channel lineage;
4. percept/interpretant refs where applicable;
5. evidence refs;
6. policy decision refs;
7. confidence type and level;
8. promotion state;
9. temporal scope;
10. allowed and disallowed consumers;
11. repair, review, or confirmation refs;
12. non-claims.

## Forbidden promotions

The edge gate must reject or keep non-active any record where:

- an extracted relation is promoted as confirmed without review or repair;
- an inferred relation is marked `ACTIVE` without evidence and policy refs;
- a reported relation becomes legal/contractual fact without a legal artifact;
- a model summary creates a durable edge without source artifacts;
- a graph slice creates a whole-state relation without projection basis;
- a stale or contested relation remains active without revalidation;
- a high-risk consumer receives an edge whose epistemic class is not allowed.

## Runtime non-claim

This document defines contract and validation posture only. It does not implement runtime graph writes, resolver scoring, merge logic, export policy, or graph storage.
