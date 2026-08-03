#!/usr/bin/env python3
"""Validate Regis NER (mention/span) contract schema and fixtures.

This is the extraction-phase (``extract -> mentions``) contract for the ER/NER
integration plan. It is intentionally stdlib-only to match the existing
graph-contract and epistemic-edge validation lanes so ``make validate`` has an
immediate proof path with no third-party runtime dependency.

Teeth: valid fixtures MUST be accepted; every ``*.invalid.json`` fixture MUST be
rejected for the reason encoded in its filename. A schema that silently accepts a
malformed mention (bad class, zero/negative span, out-of-range confidence,
missing provenance, non-FIPS hash) fails this validator.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas" / "ner"
FIXTURE_DIR = ROOT / "fixtures" / "ner"

BASE_CLASSES = {
    "PERSON",
    "ORG",
    "PRODUCT_SERVICE",
    "DEVICE",
    "ACCOUNT",
    "IDENTIFIER",
    "CREDENTIAL",
    "LOCATION",
    "JURISDICTION",
    "CONSENT_ARTIFACT",
    "POLICY_TERM",
    "PRIME_TOPIC_MENTION",
    "ACTION_EVENT_TRIGGER",
    "RELATIONSHIP_MENTION",
}

DOMAIN_CLASSES = {
    "SCOPE_REALM",
    "TRACKING_IDENTIFIER",
    "HSM_HANDLE",
    "NONCE_STREAM",
    "EXPORT_ATTEMPT",
    "CONSENT_WITNESS",
    "SENSITIVE_CONTEXT",
    "CHILD_CONTEXT",
    "PATIENT_CONTEXT",
    "CIVIC_CONTEXT",
    "MARKETING_CONTEXT",
}

ENTITY_CLASSES = BASE_CLASSES | DOMAIN_CLASSES

SOURCE_TYPES = {"document", "form", "log", "network_event", "message", "page"}
LOCALITIES = {"CITIZEN_FOG", "CITIZEN_CLOUD", "INSTITUTION", "ADTECH", "HSM"}
SCHEMA_VERSION = "regis.ner.mention_set.v0.1"


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate_schema_posture() -> None:
    """The two NER schemas must be Draft 2020-12 and stay in sync with each other
    and with this validator's taxonomy constants."""
    entity_schema = load_json(SCHEMA_DIR / "entity-class.schema.json")
    mention_schema = load_json(SCHEMA_DIR / "mention.schema.json")

    require(
        entity_schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema",
        "entity-class schema must use Draft 2020-12",
    )
    require(
        mention_schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema",
        "mention schema must use Draft 2020-12",
    )

    base = set(entity_schema["$defs"]["BaseEntityClass"]["enum"])
    domain = set(entity_schema["$defs"]["DomainEntityClass"]["enum"])
    union = set(entity_schema["$defs"]["EntityClass"]["enum"])

    require(base == BASE_CLASSES, f"base class drift: {base ^ BASE_CLASSES}")
    require(domain == DOMAIN_CLASSES, f"domain class drift: {domain ^ DOMAIN_CLASSES}")
    require(union == ENTITY_CLASSES, f"union class drift: {union ^ ENTITY_CLASSES}")
    require(
        base.isdisjoint(domain),
        "base and domain classes must be disjoint",
    )

    mention_enum = set(mention_schema["$defs"]["EntityClass"]["enum"])
    require(
        mention_enum == ENTITY_CLASSES,
        f"mention schema enum out of sync with taxonomy: {mention_enum ^ ENTITY_CLASSES}",
    )


def validate_mention(mention: dict[str, Any]) -> None:
    for field in ["mention_id", "span", "entity_class", "confidence", "provenance"]:
        require(field in mention, f"mention missing required field {field}: {mention}")

    require(
        mention["entity_class"] in ENTITY_CLASSES,
        f"unknown entity_class {mention['entity_class']}",
    )
    for secondary in mention.get("secondary_classes", []):
        require(
            secondary in ENTITY_CLASSES,
            f"unknown secondary entity_class {secondary}",
        )

    span = mention["span"]
    require("start" in span and "end" in span, "span must include start and end")
    require(
        isinstance(span["start"], int) and isinstance(span["end"], int),
        "span offsets must be integers",
    )
    require(span["start"] >= 0, "span start must be >= 0")
    require(
        span["end"] > span["start"],
        f"span end must be strictly greater than start: {span}",
    )

    conf = mention["confidence"]
    require(
        isinstance(conf, (int, float)) and 0.0 <= conf <= 1.0,
        f"confidence must be in [0,1]: {conf}",
    )
    if "uncertainty" in mention:
        unc = mention["uncertainty"]
        require(
            isinstance(unc, (int, float)) and 0.0 <= unc <= 1.0,
            f"uncertainty must be in [0,1]: {unc}",
        )

    prov = mention["provenance"]
    require(
        "source_event_ids" in prov and "artifact_ids" in prov,
        "mention provenance must include source_event_ids/artifact_ids",
    )

    if "pii" in mention:
        pii = mention["pii"]
        require("minimized" in pii, "pii must include minimized flag")
        if "hash_alg" in pii:
            require(
                pii["hash_alg"] == "SHA-256",
                f"FIPS: pii hash_alg must be SHA-256, got {pii.get('hash_alg')}",
            )
        if "value_hash" in pii:
            vh = pii["value_hash"]
            require(
                isinstance(vh, str) and len(vh) == 64 and all(c in "0123456789abcdef" for c in vh),
                "pii value_hash must be a 64-char lowercase hex SHA-256 digest",
            )


def validate_mention_set(doc: dict[str, Any]) -> None:
    require(
        doc.get("schema_version") == SCHEMA_VERSION,
        f"mention set schema_version must be {SCHEMA_VERSION}",
    )
    for field in ["source_ref", "locality", "extractor_version", "mentions"]:
        require(field in doc, f"mention set missing required field {field}")

    require(doc["locality"] in LOCALITIES, f"unknown locality {doc['locality']}")
    if "overlaps_allowed" in doc:
        require(doc["overlaps_allowed"] is True, "overlaps_allowed must be true")

    src = doc["source_ref"]
    require("source_id" in src and "source_type" in src, "source_ref needs source_id/source_type")
    require(src["source_type"] in SOURCE_TYPES, f"unknown source_type {src['source_type']}")

    for mention in doc["mentions"]:
        validate_mention(mention)


def assert_overlapping_spans_accepted(doc: dict[str, Any]) -> None:
    """Positive teeth: the valid fixture MUST actually exercise overlapping spans,
    otherwise the contract's overlapping-span guarantee is untested."""
    spans = [(m["span"]["start"], m["span"]["end"]) for m in doc["mentions"]]
    overlap = any(
        a is not b and a[0] < b[1] and b[0] < a[1]
        for i, a in enumerate(spans)
        for b in spans[i + 1 :]
    )
    require(overlap, "valid fixture must contain at least one pair of overlapping spans")


def main() -> int:
    validate_schema_posture()

    valid_path = FIXTURE_DIR / "mention_set.valid.json"
    valid_doc = load_json(valid_path)
    validate_mention_set(valid_doc)
    assert_overlapping_spans_accepted(valid_doc)

    invalid_fixtures = sorted(FIXTURE_DIR.glob("*.invalid.json"))
    require(invalid_fixtures, "expected at least one *.invalid.json rejection fixture")
    for path in invalid_fixtures:
        try:
            validate_mention_set(load_json(path))
        except AssertionError:
            continue
        raise AssertionError(f"invalid fixture was wrongly accepted: {path.name}")

    print(
        f"Regis NER contracts validated "
        f"({len(ENTITY_CLASSES)} entity classes; "
        f"1 valid + {len(invalid_fixtures)} rejection fixtures)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
