#!/usr/bin/env python3
"""Validate the Regis temporal fact-supersession + temporal-retrieval-filter contract.

This is the retrieval-plane (``graph -> search consumer``) contract for temporal
knowledge. A classical KB semantically matches an outdated chunk ("CEO is John
Smith") above the correct newer one and answers wrongly. The temporal KB marks
the outdated fact superseded, eliminates it in a high-recall pass, and rates the
most-recent fact for a given ``(entity, relation)`` as authoritative.

It is intentionally stdlib-only to match the existing graph-contract, epistemic-
edge, and NER validation lanes so ``make validate`` has an immediate proof path
with no third-party runtime dependency. The temporal invariants enforced here
(``superseded_at >= valid_from``, ``valid_to >= valid_from``, mandatory
``valid_from``) are ones JSON Schema cannot express on its own.

This record NEVER claims canonical truth; canonical supersession lives in the ACR
decision ledger and epistemic-edge promotion state. ``valid_from``/``valid_to``
are the search-plane projection of node/edge ``valid_time.from/to`` and of the
epistemic-edge ``temporalScope.validFrom/validTo``.

Teeth (both ways):
  * the John-Smith -> Jenna-Brown fixture: the high-recall pass MUST surface both
    facts, the superseded John-Smith fact MUST be excluded, and the max-valid_from
    Jenna-Brown fact MUST be rated authoritative;
  * a fact with no supersession marker MUST pass and be retrievable;
  * every ``*.invalid.json`` fixture MUST be rejected for the reason in its name
    (superseded_at < valid_from, valid_to < valid_from, missing valid_from).
A filter that silently keeps a superseded fact, or a schema that silently accepts
a malformed temporal record, fails this validator.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "search" / "temporal-fact.schema.json"
FIXTURE_DIR = ROOT / "fixtures" / "search"

SCHEMA_VERSION = "regis.search.temporal_fact.v0.1"
SCHEMA_ID = "https://schemas.socioprophet.org/regis/search/temporal-fact.schema.json"

REQUIRED_FIELDS = ["schema_version", "fact_id", "entity", "relation", "value", "valid_from", "provenance"]
ALLOWED_FIELDS = set(REQUIRED_FIELDS) | {
    "valid_to",
    "superseded_by",
    "superseded_at",
    "source_edge_ref",
    "claims_canonical_truth",
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def parse_instant(value: Any, field: str) -> datetime:
    require(isinstance(value, str) and value, f"{field} must be a non-empty RFC3339 date-time string")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:  # pragma: no cover - exercised by malformed fixtures
        raise AssertionError(f"{field} is not a valid date-time: {value!r} ({exc})")


# --------------------------------------------------------------------------- #
# Schema posture
# --------------------------------------------------------------------------- #
def validate_schema_posture() -> None:
    schema = load_json(SCHEMA_PATH)
    require(
        schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema",
        "temporal-fact schema must use Draft 2020-12",
    )
    require(schema.get("$id") == SCHEMA_ID, f"temporal-fact schema $id drift: {schema.get('$id')}")
    require(schema.get("additionalProperties") is False, "temporal-fact schema must forbid additional properties")

    required = set(schema.get("required", []))
    require(required == set(REQUIRED_FIELDS), f"schema required-field drift: {required ^ set(REQUIRED_FIELDS)}")

    props = set(schema.get("properties", {}).keys())
    require(props == ALLOWED_FIELDS, f"schema property drift: {props ^ ALLOWED_FIELDS}")

    require(
        schema["properties"]["schema_version"].get("const") == SCHEMA_VERSION,
        "schema_version const drift",
    )
    require(
        schema["properties"]["claims_canonical_truth"].get("const") is False,
        "claims_canonical_truth must be const false (retrieval plane never claims canonical truth)",
    )


# --------------------------------------------------------------------------- #
# Per-fact validation (rejection teeth)
# --------------------------------------------------------------------------- #
def validate_fact(fact: dict[str, Any]) -> None:
    require(isinstance(fact, dict), f"fact must be an object: {fact!r}")

    unknown = set(fact.keys()) - ALLOWED_FIELDS
    require(not unknown, f"fact has unknown fields: {sorted(unknown)}")

    for field in REQUIRED_FIELDS:
        require(field in fact, f"fact missing required field {field}: {fact.get('fact_id')}")

    require(fact["schema_version"] == SCHEMA_VERSION, f"fact schema_version must be {SCHEMA_VERSION}")
    for field in ["fact_id", "entity", "relation", "value"]:
        require(isinstance(fact[field], str) and fact[field], f"{field} must be a non-empty string")

    if "claims_canonical_truth" in fact:
        require(fact["claims_canonical_truth"] is False, "claims_canonical_truth must be false")

    valid_from = parse_instant(fact["valid_from"], "valid_from")

    valid_to_raw = fact.get("valid_to")
    if valid_to_raw is not None:
        valid_to = parse_instant(valid_to_raw, "valid_to")
        require(
            valid_to >= valid_from,
            f"valid_to ({valid_to_raw}) must be >= valid_from ({fact['valid_from']}) for {fact['fact_id']}",
        )

    superseded_at_raw = fact.get("superseded_at")
    if superseded_at_raw is not None:
        superseded_at = parse_instant(superseded_at_raw, "superseded_at")
        require(
            superseded_at >= valid_from,
            f"superseded_at ({superseded_at_raw}) must be >= valid_from ({fact['valid_from']}) for {fact['fact_id']}",
        )

    superseded_by = fact.get("superseded_by")
    if superseded_by is not None:
        require(isinstance(superseded_by, str) and superseded_by, "superseded_by must be a non-empty fact_id")

    prov = fact["provenance"]
    require(
        isinstance(prov, dict) and "source_event_ids" in prov and "artifact_ids" in prov,
        "fact provenance must include source_event_ids/artifact_ids",
    )


# --------------------------------------------------------------------------- #
# Reference temporal retrieval filter
# --------------------------------------------------------------------------- #
def is_superseded(fact: dict[str, Any]) -> bool:
    """A fact is marked superseded when it carries a supersession pointer or instant."""
    return fact.get("superseded_by") is not None or fact.get("superseded_at") is not None


def temporal_retrieve(
    facts: list[dict[str, Any]], entity: str, relation: str
) -> dict[str, Any]:
    """High-recall candidate pass, then supersession suppression, then max-valid_from wins.

    Returns the retrieval trace: the candidates (high-recall), the suppressed
    (superseded) facts, the surviving facts, and the single authoritative fact
    (or None if nothing survives).
    """
    candidates = [f for f in facts if f["entity"] == entity and f["relation"] == relation]
    suppressed = [f for f in candidates if is_superseded(f)]
    surviving = [f for f in candidates if not is_superseded(f)]
    authoritative: Optional[dict[str, Any]] = None
    if surviving:
        authoritative = max(surviving, key=lambda f: parse_instant(f["valid_from"], "valid_from"))
    return {
        "candidates": candidates,
        "suppressed": suppressed,
        "surviving": surviving,
        "authoritative": authoritative,
    }


# --------------------------------------------------------------------------- #
# Teeth
# --------------------------------------------------------------------------- #
def assert_supersession_teeth() -> None:
    """The John-Smith -> Jenna-Brown fixture proves the filter both ways."""
    facts = load_json(FIXTURE_DIR / "ceo_supersession.facts.valid.json")
    require(isinstance(facts, list) and len(facts) >= 2, "ceo fixture must be a list of >= 2 facts")
    for fact in facts:
        validate_fact(fact)

    entity = "urn:regis:entity:org:abc-corp"
    relation = "HAS_CEO"
    trace = temporal_retrieve(facts, entity, relation)

    # High-recall: BOTH the outdated and the current fact are surfaced as candidates,
    # so the exclusion below is genuine suppression, not mere absence from the index.
    candidate_values = {f["value"] for f in trace["candidates"]}
    require(
        {"John Smith", "Jenna Brown"} <= candidate_values,
        f"high-recall pass must surface both facts, got {candidate_values}",
    )

    # The outdated fact is excluded.
    suppressed_values = {f["value"] for f in trace["suppressed"]}
    require("John Smith" in suppressed_values, "outdated John-Smith fact must be marked superseded and excluded")
    surviving_values = {f["value"] for f in trace["surviving"]}
    require("John Smith" not in surviving_values, "superseded John-Smith fact must not survive the filter")

    # The most-recent fact wins.
    authoritative = trace["authoritative"]
    require(authoritative is not None, "an authoritative fact must survive")
    require(
        authoritative["value"] == "Jenna Brown",
        f"authoritative CEO must be Jenna Brown (max valid_from), got {authoritative['value']!r}",
    )


def assert_no_supersession_passes() -> None:
    """A fact with no supersession marker passes and is retrievable as authoritative."""
    fact = load_json(FIXTURE_DIR / "no_supersession.fact.valid.json")
    validate_fact(fact)
    require(not is_superseded(fact), "no-supersession fixture must not be marked superseded")
    trace = temporal_retrieve([fact], fact["entity"], fact["relation"])
    require(
        trace["authoritative"] is not None and trace["authoritative"]["value"] == fact["value"],
        "non-superseded fact must be retrievable as authoritative",
    )


def assert_invalid_fixtures_rejected() -> int:
    invalid_fixtures = sorted(FIXTURE_DIR.glob("*.invalid.json"))
    require(invalid_fixtures, "expected at least one *.invalid.json rejection fixture")
    for path in invalid_fixtures:
        try:
            validate_fact(load_json(path))
        except AssertionError:
            continue
        raise AssertionError(f"invalid fixture was wrongly accepted: {path.name}")
    return len(invalid_fixtures)


def main() -> int:
    validate_schema_posture()
    assert_supersession_teeth()
    assert_no_supersession_passes()
    n_invalid = assert_invalid_fixtures_rejected()
    print(
        "Regis temporal fact-supersession + retrieval-filter contract validated "
        f"(supersession filter: John Smith excluded, Jenna Brown authoritative; "
        f"1 no-supersession pass + {n_invalid} rejection fixtures)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
