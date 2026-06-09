#!/usr/bin/env python3
"""Validate Regis identity personhood/sigil graph records.

This validator is intentionally stdlib-only. It mirrors the epistemic-edge
validator style: lightweight shape checks plus semantic invariants for the
identity non-collapse boundary.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "identity-personhood-sigil-graph-record.schema.json"
EXAMPLE_DIR = ROOT / "examples"

REQUIRED_NODE_CLASSES = {
    "PERSONHOOD_BINDING",
    "IDENTITY_MESH_SUBJECT",
    "IDENTITY_SIGIL_SEAL",
}

OBJECT_NODE_CLASSES = {
    "SIGNING_AUTHORITY",
    "SIGIL_ARTIFACT",
    "PORTRAIT_PRESENTATION_POLICY",
    "AGENT_DELEGATION_SEAL",
    "CONTEXTUAL_REPUTATION_CREDENTIAL",
}

REQUIRED_NON_CLAIM_PHRASES = (
    "wallet the person",
    "portrait biometric proof by default",
    "sigil seal is presentation",
    "reputation is contextual evidence",
    "does not authorize public correlation",
)


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
        "apiVersion",
        "kind",
        "recordId",
        "createdAt",
        "sourceArtifacts",
        "nodes",
        "edges",
        "policyDecisionRefs",
        "transitionReceiptRefs",
        "nonClaims",
    ]:
        require(field in required, f"schema missing required field {field}")


def validate_shape(record: dict[str, Any], *, source_label: str) -> None:
    for field in [
        "apiVersion",
        "kind",
        "recordId",
        "createdAt",
        "sourceArtifacts",
        "nodes",
        "edges",
        "policyDecisionRefs",
        "transitionReceiptRefs",
        "nonClaims",
    ]:
        require(field in record, f"{source_label}: missing {field}")
    require(record["apiVersion"] == "regis.entity-graph.identity-personhood-sigil/v1", f"{source_label}: invalid apiVersion")
    require(record["kind"] == "IdentityPersonhoodSigilGraphRecord", f"{source_label}: invalid kind")
    require(record["sourceArtifacts"].get("personhoodBindingRef"), f"{source_label}: missing personhoodBindingRef")
    require(record["sourceArtifacts"].get("identitySigilSealRef"), f"{source_label}: missing identitySigilSealRef")
    require(record["nodes"], f"{source_label}: nodes required")
    require(record["edges"], f"{source_label}: edges required")
    for node in record["nodes"]:
        for field in ["nodeId", "nodeClass", "sourceRef"]:
            require(field in node, f"{source_label}: node missing {field}")
    for edge in record["edges"]:
        for field in ["edgeId", "edgeClass", "src", "dst", "status", "evidenceRefs", "policyRefs", "nonClaims"]:
            require(field in edge, f"{source_label}: edge missing {field}")


def semantic_diagnostics(record: dict[str, Any]) -> list[str]:
    diagnostics: list[str] = []
    node_classes = {node["nodeClass"] for node in record["nodes"]}
    nodes_by_id = {node["nodeId"]: node for node in record["nodes"]}
    edges = record["edges"]
    non_claims = "\n".join(str(item).lower() for item in record.get("nonClaims", []))

    missing_nodes = sorted(REQUIRED_NODE_CLASSES - node_classes)
    if missing_nodes:
        diagnostics.append(f"missing required node classes: {missing_nodes}")

    for phrase in REQUIRED_NON_CLAIM_PHRASES:
        if phrase not in non_claims:
            diagnostics.append(f"missing graph non-claim phrase: {phrase}")

    personhood_edges = [edge for edge in edges if edge["edgeClass"] == "PERSON_BOUND_TO_SUBJECT"]
    if not personhood_edges:
        diagnostics.append("requires PERSON_BOUND_TO_SUBJECT edge")

    for edge in personhood_edges:
        src_class = nodes_by_id.get(edge["src"], {}).get("nodeClass")
        if src_class != "PERSONHOOD_BINDING":
            diagnostics.append("PERSON_BOUND_TO_SUBJECT must originate from PERSONHOOD_BINDING node")
        if src_class in OBJECT_NODE_CLASSES:
            diagnostics.append(f"object node class must not assert personhood: {src_class}")
        if "personhood_claim" in str(edge.get("scope", "")).lower() and src_class != "PERSONHOOD_BINDING":
            diagnostics.append("personhood_claim scope may not originate from object node")
        if len(edge.get("evidenceRefs", [])) < 3:
            diagnostics.append("personhood edge requires at least three evidence refs")
        edge_non_claims = "\n".join(str(item).lower() for item in edge.get("nonClaims", []))
        if "not wallet" not in edge_non_claims and "wallet" not in edge_non_claims:
            diagnostics.append("personhood edge must explicitly reject wallet/object collapse")

    sigil_edges = [edge for edge in edges if edge["edgeClass"] == "SUBJECT_HAS_SIGIL_SEAL"]
    if not sigil_edges:
        diagnostics.append("requires SUBJECT_HAS_SIGIL_SEAL edge")
    for edge in sigil_edges:
        if "pbr_" not in "\n".join(edge.get("evidenceRefs", [])):
            diagnostics.append("SUBJECT_HAS_SIGIL_SEAL requires personhood binding evidence ref")

    wallet_edges = [edge for edge in edges if "wallet" in "\n".join(edge.get("evidenceRefs", [])).lower()]
    for edge in wallet_edges:
        if "personhood_claim" in str(edge.get("scope", "")).lower():
            diagnostics.append("wallet evidence edge must not carry personhood_claim scope")
        edge_non_claims = "\n".join(str(item).lower() for item in edge.get("nonClaims", []))
        if "wallet is not the person" not in edge_non_claims:
            diagnostics.append("wallet edge requires non-claim: Wallet is not the person")

    if "RECOVERY_POLICY" not in node_classes:
        diagnostics.append("requires RECOVERY_POLICY node")
    if not any(edge["edgeClass"] == "RECOVERABLE_BY" for edge in edges):
        diagnostics.append("requires RECOVERABLE_BY edge")

    reputation_edges = [edge for edge in edges if edge["edgeClass"] == "ATTESTS_CONTEXTUAL_REPUTATION"]
    for edge in reputation_edges:
        if "global human worth" in "\n".join(edge.get("evidenceRefs", []) + edge.get("nonClaims", [])).lower():
            diagnostics.append("reputation edge must not encode global human worth")
        if "developer" not in str(edge.get("scope", "")).lower() and "context" not in "\n".join(edge.get("nonClaims", [])).lower():
            diagnostics.append("reputation edge requires contextual scope or contextual non-claim")

    return diagnostics


def expected_result(path: Path) -> str:
    return "fail" if ".rejected." in path.name or path.name.startswith("bad-") else "pass"


def main() -> int:
    validate_schema_posture()
    examples = sorted(EXAMPLE_DIR.glob("personhood-sigil-graph*.json"))
    if not examples:
        raise SystemExit("No identity personhood/sigil graph examples found")

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
