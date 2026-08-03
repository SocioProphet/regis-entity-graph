#!/usr/bin/env python3
"""Validate Regis epistemic edge companion records.

This validator is intentionally stdlib-only to match the existing graph-contract
validation lane. It checks basic schema posture and semantic invariants that are
not expressible through the lightweight companion schema alone.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "epistemic-edge-record.schema.json"
EXAMPLE_DIR = ROOT / "examples" / "epistemic-edges"

EPISTEMIC_CLASSES = {
    "reported_relation",
    "observed_relation",
    "extracted_relation",
    "inferred_relation",
    "confirmed_relation",
    "legal_contractual_relation",
    "operational_relation",
    "hypothetical_relation",
    "superseded_relation",
    "contested_relation",
}

HIGH_RISK_CONSUMERS = {"entity_merge", "export", "policy", "memory_promotion", "agent_action", "legal_or_contract", "publication"}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate_schema_posture() -> None:
    schema = load_json(SCHEMA)
    require(schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema", "schema must use Draft 2020-12")
    required = set(schema.get("required", []))
    for field in [
        "edgeRef",
        "edgeKind",
        "edgeStatus",
        "epistemicClass",
        "sourceChannel",
        "evidenceRefs",
        "policyDecisionRefs",
        "confidence",
        "promotionState",
        "temporalScope",
        "consumers",
        "review",
        "nonClaims",
    ]:
        require(field in required, f"schema missing required field {field}")


def validate_shape(record: dict[str, Any], *, source_label: str) -> None:
    for field in [
        "apiVersion",
        "kind",
        "recordId",
        "createdAt",
        "edgeRef",
        "edgeKind",
        "edgeStatus",
        "epistemicClass",
        "sourceChannel",
        "evidenceRefs",
        "policyDecisionRefs",
        "confidence",
        "promotionState",
        "temporalScope",
        "consumers",
        "review",
        "nonClaims",
    ]:
        require(field in record, f"{source_label}: missing {field}")
    require(record["apiVersion"] == "regis.entity-graph.epistemic-edge/v1", f"{source_label}: invalid apiVersion")
    require(record["kind"] == "EpistemicEdgeRecord", f"{source_label}: invalid kind")
    require(record["epistemicClass"] in EPISTEMIC_CLASSES, f"{source_label}: unknown epistemicClass")
    require(record["evidenceRefs"], f"{source_label}: evidenceRefs required")
    require(record["policyDecisionRefs"], f"{source_label}: policyDecisionRefs required")
    channel = record["sourceChannel"]
    for field in ["channelRef", "channelClass", "substrate", "captureMethod", "trustBoundary", "knownConfusabilityModes"]:
        require(field in channel, f"{source_label}: sourceChannel missing {field}")
    require(channel["knownConfusabilityModes"], f"{source_label}: knownConfusabilityModes required")
    confidence = record["confidence"]
    for field in ["confidenceType", "level"]:
        require(field in confidence, f"{source_label}: confidence missing {field}")
    consumers = record["consumers"]
    require("allowed" in consumers and "disallowed" in consumers, f"{source_label}: consumers must declare allowed/disallowed")
    review = record["review"]
    for field in ["required", "status", "reviewerRefs", "approvalRef", "repairEventRefs"]:
        require(field in review, f"{source_label}: review missing {field}")


def semantic_diagnostics(record: dict[str, Any]) -> list[str]:
    diagnostics: list[str] = []
    epistemic_class = record["epistemicClass"]
    promotion_state = record["promotionState"]
    edge_status = record["edgeStatus"]
    confidence_type = record["confidence"]["confidenceType"]
    allowed_consumers = set(record["consumers"]["allowed"])
    review = record["review"]
    non_claims = record["nonClaims"]

    if epistemic_class in {"reported_relation", "extracted_relation", "inferred_relation", "hypothetical_relation"}:
        if promotion_state == "confirmed":
            diagnostics.append(f"{epistemic_class} must not use confirmed promotionState")
        if edge_status == "ACTIVE" and review["status"] != "approved":
            diagnostics.append(f"{epistemic_class} must not be ACTIVE without approved review")
        high_risk = sorted(allowed_consumers & HIGH_RISK_CONSUMERS)
        if high_risk:
            diagnostics.append(f"{epistemic_class} cannot allow high-risk consumers without confirmed relation: {high_risk}")

    if epistemic_class == "confirmed_relation":
        if promotion_state != "confirmed":
            diagnostics.append("confirmed_relation requires confirmed promotionState")
        if review["status"] != "approved" or not review.get("approvalRef"):
            diagnostics.append("confirmed_relation requires approved review and approvalRef")
        if confidence_type not in {"artifact_verified", "provenance", "operational"}:
            diagnostics.append("confirmed_relation requires artifact/provenance/operational confidence type")

    if epistemic_class == "legal_contractual_relation":
        if "legal_or_contract" not in allowed_consumers:
            diagnostics.append("legal_contractual_relation should explicitly declare legal_or_contract consumer if used")
        if not any(ref.startswith("contract:") or ref.startswith("legal:") for ref in record["evidenceRefs"]):
            diagnostics.append("legal_contractual_relation requires contract: or legal: evidence ref")

    if epistemic_class in {"reported_relation", "hypothetical_relation", "contested_relation"} and not non_claims:
        diagnostics.append(f"{epistemic_class} requires nonClaims")

    if record["temporalScope"].get("validTo") is None and epistemic_class in {"operational_relation", "reported_relation"}:
        if not record["temporalScope"].get("revalidationRef"):
            diagnostics.append(f"{epistemic_class} with open-ended validTo requires revalidationRef")

    return diagnostics


def expected_result(path: Path) -> str:
    return "fail" if ".rejected" in path.name or path.name.startswith("bad-") else "pass"


def main() -> int:
    validate_schema_posture()
    examples = sorted(EXAMPLE_DIR.glob("*.example.json"))
    if not examples:
        raise SystemExit("No epistemic edge examples found")

    checked = []
    for path in examples:
        record = load_json(path)
        validate_shape(record, source_label=path.name)
        diagnostics = semantic_diagnostics(record)
        actual = "fail" if diagnostics else "pass"
        expected = expected_result(path)
        checked.append({"example": path.name, "expected": expected, "actual": actual, "diagnostics": diagnostics})
        if actual != expected:
            raise AssertionError(json.dumps(checked[-1], indent=2))

    print(json.dumps({"ok": True, "checked": checked}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
