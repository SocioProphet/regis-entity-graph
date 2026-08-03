# Reconciliation — external decision-ledger design vs. estate ACR contracts
Status: draft · scope: what a large external "canonical verdict/decision-ledger" design proposed, checked against what `regis-entity-graph` (and the wider estate) already ship. Records EXISTS (consume) / DELTA (build) / REDUNDANT (discard), so we extend the estate rather than fork it.

## Method
Read the real contracts, not memory: `schemas/acr/*.schema.json`, `contracts/acr-contract-pack.yaml`, `prophet-core-ledger/schemas/operation-evidence.schema.json`, `semantic-serdes/schemas/{agent_decision_artifact,shir_receipt,replay_artifact}.schema.json`, `mellumwork/`.

## Findings
| External proposal | Estate reality | Disposition |
|---|---|---|
| "One decision-ledger unifying match/merge/split/promotion/rejection/override" | **EXISTS** — `acr/decision-ledger-entry.schema.json` `DecisionLedgerEntry.decision_type` already enumerates exactly these (incl. appeal_opened/resolved). | **REDUNDANT** — consume the estate's. |
| CanonicalEntity as a "materialized view / projection under policy" | **EXISTS** — `CanonicalEntity` is described as "Stable entity projection derived from source records, evidence, concordance links, and decision-ledger entries under versioned policy." | **REDUNDANT.** |
| EUTC energy/margin/stability + two-threshold promotion gate | **EXISTS** — `EnergyLedgerEntry` (candidate scores, margin, stability, thresholds, promotion decision) + `PromotionPolicy` + invariant `low_margin_blocks_promotion`. | **REDUNDANT.** |
| Reversibility / compensation for canonical mutations | **EXISTS** — `prophet-core-ledger` `OperationEvidenceLedger` has `compensation`/rollback with `compensated_task_ids`. | **REDUNDANT.** |
| Privacy invariant against unsafe identity aggregation | **EXISTS** — invariant `identity_prime_scope_protection`. (Note: this covers ACR identity; it does NOT cover the capital-markets Feature Registry mobility-PII case — that remains a real DELTA in a different repo.) | Partial — see open items. |
| Signatures on decisions | **PARTIAL** — receipts (`semantic-serdes/shir_receipt`) are signed (signature/blake/hash), but the ACR `DecisionLedgerEntry` itself is not sealed and is not receipt-wrapped. | **DELTA.** |
| Hash-chain / tamper-evidence / fork detection on the ledger | **ABSENT estate-wide** — no schema defines `prev_hash`/`seq`/`merkle`. The ledger is "append-only" by convention only. | **DELTA (strongest).** |
| Idempotency key (replay ≠ duplicate canonical mutation) | **ABSENT** — `DecisionLedgerEntry.replay` pins `policy_version` + `input_hashes` (good for replay) but nothing dedupes a re-emitted decision. | **DELTA.** |
| Content-hash of the applied policy | **PARTIAL** — `replay.policy_version` is a version string, not a content hash. | Minor DELTA — added as optional `policy_hash`. |

## What this branch builds (the DELTAs only)
`DecisionLedgerSeal` (`schemas/acr/decision-ledger-seal.schema.json`) — an **additive** envelope that references a `DecisionLedgerEntry` by `decision_id` and supplies the four missing integrity properties WITHOUT modifying the entry (which stays `additionalProperties:false`):
- **entry_hash** — commits to exact entry content (tamper-evidence).
- **prev_seal_hash + seq + chain_id** — per-scope hash chain + fork detection.
- **signature {ed25519 | ed25519-frost}** — authenticity; FROST threshold for high-blast-radius merge/split/canonical_promoted.
- **idempotency_key** — a replay does not create a second canonical mutation.
- optional **policy_hash** and **merkle_checkpoint** (cross-chain anchoring).

Plus: 3 contract-pack invariants (`decision_ledger_is_tamper_evident`, `decision_seal_chain_is_fork_free`, `decision_seal_is_signed`), a bare + a chain example, and `tools/validate_decision_ledger_seals.py` (SEAL-1..5, wired into `make validate`).

## Explicitly NOT built here (out of scope / separate WOs)
- The external design's whole parallel schema tower (decision_ledger/episode/er_object_model/feature_registry) — **REDUNDANT** with the above; discarded in favour of the estate contracts.
- Capital-markets Feature Registry consent + k-anonymity gate — a **real DELTA** but belongs in `policy-fabric` / a cartridge contract, not here.
- Plugin cosign-verify-before-spawn + effect enforcement — **DELTA** for `prophet-cli`.

## Honest status (E1)
- `hashseal` here = blake3-256 over a JCS **approximation** (sorted keys + compact separators). The estate canonicalizer (exact RFC 8785) must be confirmed and bound before these hashes are treated as wire-compatible. This is the one remaining E1 assumption in this branch.
- Branch cut from local `main` (which was 23 commits behind `origin/main`); rebase onto fresh `origin/main` before PR.
