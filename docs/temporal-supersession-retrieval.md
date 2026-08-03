# Temporal fact-supersession & temporal-retrieval-filter

Status: additive contract, v0.1. Search/retrieval plane. Never claims canonical truth.

## Problem

A classical KB answers "Who is the CEO of ABC?" wrongly because the query
semantically matches an **outdated** chunk ("CEO is John Smith") above the
**current** one ("Jenna Brown became CEO in Jan 2025, replacing John Smith").
Semantic similarity has no notion of time, so the stale fact wins on relevance.

## Capability

A temporal KB **marks** the outdated fact superseded, **eliminates** it in a
high-recall candidate pass, and rates the most-recent fact for a given
`(entity, relation)` as **authoritative**. The correct answer (Jenna Brown) is
returned.

## Contract

`schemas/search/temporal-fact.schema.json` — a fact carries:

| field | role |
|---|---|
| `entity`, `relation` | the supersession key `(entity, relation)` |
| `value` | object of the relation (the answer surfaced) |
| `valid_from` (required) | valid-time start; a fact with no `valid_from` cannot be ordered and is rejected |
| `valid_to` (optional) | valid-time end; when present must be `>= valid_from` |
| `superseded_by` (optional) | `fact_id` of the replacing fact; presence marks this fact superseded |
| `superseded_at` (optional) | instant of supersession; when present must be `>= valid_from` |
| `source_edge_ref` (optional) | upstream `edge_id` / epistemic-edge `recordId` |

This is the search-plane projection of the estate's three-time model:
`valid_from`/`valid_to` correspond to node/edge `valid_time.from`/`to`
(`schemas/node.schema.json`, `schemas/edge.schema.json`) and to the
epistemic-edge `temporalScope.validFrom`/`validTo`
(`schemas/epistemic-edge-record.schema.json`). Canonical supersession authority
remains with the ACR decision ledger (`schemas/acr/`) and epistemic-edge
`promotionState: superseded` / `epistemicClass: superseded_relation`; this record
sets `claims_canonical_truth: false` like every other search-plane record.

## Reference retrieval filter

`tools/validate_temporal_supersession.py :: temporal_retrieve(facts, entity, relation)`:

1. **High-recall pass** — collect every candidate matching `(entity, relation)`
   (both the outdated and the current fact are surfaced).
2. **Suppress superseded** — drop any candidate marked superseded
   (`superseded_by` or `superseded_at` present).
3. **Most-recent wins** — among survivors, the maximum-`valid_from` fact is
   authoritative.

## Teeth

`make validate-temporal-supersession` proves the filter both ways:

- `fixtures/search/ceo_supersession.facts.valid.json` — high-recall surfaces both
  John Smith and Jenna Brown; John Smith is suppressed; Jenna Brown (max
  `valid_from`) is authoritative.
- `fixtures/search/no_supersession.fact.valid.json` — a fact with no supersession
  marker passes and is retrievable.
- `fixtures/search/*.invalid.json` — rejected: `superseded_at < valid_from`,
  `valid_to < valid_from`, missing `valid_from`.

## Runtime (out of scope for this contract PR)

Wiring the filter into the live retriever / re-ranker is tracked separately
(see the linked runtime issue and prophet-workspace#76). This PR delivers the
contract, the reference filter, and the fixtures only.
