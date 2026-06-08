#!/usr/bin/env python3
"""Validate IOES graph extension fixtures.

This validator is intentionally stdlib-only to match the existing Regis validation
posture. It performs shape-adjacent checks and IOES semantic gates over the
contract fixture format.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_DIR = ROOT / "examples" / "ioes"
SCHEMA = ROOT / "schemas" / "ioes_graph_extension.schema.json"
VALID_FIXTURES = [
    EXAMPLE_DIR / "kept-learning-artifact.ioes-records.valid.json",
]
REJECTED_FIXTURES = [
    EXAMPLE_DIR / "orphaned-learning-artifact.ioes-records.rejected.json",
]

RECORD_KINDS = {
    "StewardshipEdge",
    "KeeperLog",
    "SuccessionRule",
    "OntogenesisState",
    "GaiaDependencyRecord",
    "AbandonmentSignal",
}

ACTIVE_LIKE = {"active", "handoff_pending"}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def parse_dt(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed
    except ValueError:
        return None


def validate_record_shape(record: dict[str, Any]) -> None:
    for field in [
        "ioes_version",
        "record_kind",
        "record_id",
        "entity_ref",
        "status",
        "evidence_refs",
        "policy_refs",
        "valid_time",
        "provenance",
    ]:
        require(field in record, f"record missing required field {field}: {record}")
    require(record["ioes_version"] == "0.1", f"unsupported IOES version {record['ioes_version']}")
    require(record["record_kind"] in RECORD_KINDS, f"unknown IOES record_kind {record['record_kind']}")
    require(isinstance(record["evidence_refs"], list) and record["evidence_refs"], f"record requires evidence_refs: {record['record_id']}")
    require(isinstance(record["policy_refs"], list) and record["policy_refs"], f"record requires policy_refs: {record['record_id']}")
    valid_time = record["valid_time"]
    require("from" in valid_time and "to" in valid_time, f"record valid_time requires from/to: {record['record_id']}")
    prov = record["provenance"]
    require("source_event_ids" in prov and "artifact_ids" in prov, f"record provenance requires source_event_ids/artifact_ids: {record['record_id']}")


def validate_record_semantics(record: dict[str, Any]) -> None:
    kind = record["record_kind"]
    status = record["status"]

    if kind == "StewardshipEdge" and status in ACTIVE_LIKE:
        require(record.get("steward_ref"), f"active StewardshipEdge requires steward_ref: {record['record_id']}")
        require(record.get("authority_refs"), f"active StewardshipEdge requires authority_refs: {record['record_id']}")
        require(record.get("keeper_log_refs"), f"active StewardshipEdge requires keeper_log_refs: {record['record_id']}")
        require(record.get("succession_rule_refs"), f"active StewardshipEdge requires succession_rule_refs: {record['record_id']}")

    if kind == "KeeperLog" and status in ACTIVE_LIKE:
        require(record.get("keeper_ref"), f"active KeeperLog requires keeper_ref: {record['record_id']}")
        require(record.get("authority_refs"), f"active KeeperLog requires authority_refs: {record['record_id']}")
        require(record.get("review_interval_days"), f"active KeeperLog requires review_interval_days: {record['record_id']}")
        require(record.get("last_reviewed_at"), f"active KeeperLog requires last_reviewed_at: {record['record_id']}")

    if kind == "SuccessionRule" and status in ACTIVE_LIKE:
        require(record.get("successor_refs"), f"active SuccessionRule requires successor_refs: {record['record_id']}")
        require(record.get("authority_refs"), f"active SuccessionRule requires authority_refs: {record['record_id']}")

    if kind == "OntogenesisState" and status in ACTIVE_LIKE:
        require(record.get("phase"), f"active OntogenesisState requires phase: {record['record_id']}")
        if record.get("phase") in {"maturity", "transmission"}:
            reviewed_at = parse_dt(record.get("last_reviewed_at"))
            interval = record.get("review_interval_days")
            require(reviewed_at is not None and isinstance(interval, int), f"mature OntogenesisState requires review timestamp and interval: {record['record_id']}")
            policy_now = datetime(2026, 6, 6, tzinfo=timezone.utc)
            age_days = (policy_now - reviewed_at).days
            require(age_days <= interval, f"mature OntogenesisState is past review interval: {record['record_id']}")

    if kind == "GaiaDependencyRecord" and status in ACTIVE_LIKE:
        require(record.get("dependency_type"), f"active GaiaDependencyRecord requires dependency_type: {record['record_id']}")
        require(record.get("criticality"), f"active GaiaDependencyRecord requires criticality: {record['record_id']}")


def validate_fixture(path: Path) -> None:
    fixture = load_json(path)
    require(isinstance(fixture, dict), f"fixture must be an object: {path}")
    require(fixture.get("schema_version") == "0.1", f"fixture must use schema_version 0.1: {path}")
    records = fixture.get("records")
    require(isinstance(records, list) and records, f"fixture must include records: {path}")

    kinds = {record.get("record_kind") for record in records if isinstance(record, dict)}
    for record in records:
        require(isinstance(record, dict), f"record must be object: {path}")
        validate_record_shape(record)
        validate_record_semantics(record)

    if "StewardshipEdge" in kinds:
        require("KeeperLog" in kinds, f"fixture with StewardshipEdge requires KeeperLog: {path}")
        require("SuccessionRule" in kinds, f"fixture with StewardshipEdge requires SuccessionRule: {path}")


def main() -> int:
    require(SCHEMA.exists(), "IOES graph extension schema must exist")
    for path in VALID_FIXTURES:
        validate_fixture(path)
    rejected_errors: list[str] = []
    for path in REJECTED_FIXTURES:
        try:
            validate_fixture(path)
        except AssertionError as exc:
            rejected_errors.append(str(exc))
    require(rejected_errors, "at least one rejected fixture must fail IOES semantic validation")
    print("Regis IOES graph extension fixtures validated")
    for err in rejected_errors:
        print(f"Rejected fixture failed as expected: {err}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
