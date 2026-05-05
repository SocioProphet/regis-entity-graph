#!/usr/bin/env python3
"""Validate Regis graph contract schemas and example graph deltas.

This validator is intentionally lightweight and stdlib-only so the repo has an
immediate `make validate`-friendly proof path before adopting a jsonschema
runtime dependency.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas"
EXAMPLE_DIR = ROOT / "examples"

NODE_KINDS = {
    "PERSON",
    "PSEUDONYM",
    "RECORD",
    "FEATURE_ATOM",
    "EVENT",
    "DEVICE",
    "APP",
    "SCOPE",
    "SESSION",
    "ENTITY_CLUSTER",
    "ORG",
    "ROLE",
    "SERVICE_WORKLOAD",
    "CREDENTIAL",
    "PROOF_ARTIFACT",
    "PROOF_INGRESS_RECORD",
    "POLICY_WITNESS",
    "CONSENT_WITNESS",
    "SOURCE_GRAPH_VIEW",
    "SOURCE_AUDIT_RECORD",
}

EDGE_KINDS = {
    "MATCH_EVIDENCE",
    "MERGE_PROPOSAL",
    "MERGE_ACCEPTED",
    "MERGE_VETOED",
    "UNMERGE",
    "SPLIT_FROM",
    "DISCLOSED_RELATIONSHIP",
    "DERIVED_RELATIONSHIP",
    "FORBIDDEN_RELATIONSHIP",
    "USES_FEATURE",
    "EMITTED_EVENT",
    "OCCURS_IN_SCOPE",
    "HAS_SESSION",
    "HAS_PROOF_INGRESS",
    "HAS_SOURCE_AUDIT_RECORD",
    "MATERIALIZED_AS_SOURCE_GRAPH_VIEW",
    "DELEGATES_TO",
    "EXPORTS_TO",
    "BLOCKED_EXPORT",
    "ATTESTED_BY_PROOF",
    "AUTHORIZED_BY_CONSENT",
}

DELTA_KINDS = {
    "UPSERT_NODE",
    "UPSERT_EDGE",
    "ATTACH_ARTIFACT",
    "ATTACH_WITNESS",
    "VETO_EDGE",
    "SPLIT_ENTITY",
    "UNMERGE_ENTITY",
    "REVOKE_EDGE",
    "EXPIRE_NODE",
    "EXPIRE_EDGE",
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate_schema_files() -> None:
    node_schema = load_json(SCHEMA_DIR / "node.schema.json")
    edge_schema = load_json(SCHEMA_DIR / "edge.schema.json")
    delta_schema = load_json(SCHEMA_DIR / "graph_delta.schema.json")

    require(node_schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema", "node schema must use Draft 2020-12")
    require(edge_schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema", "edge schema must use Draft 2020-12")
    require(delta_schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema", "delta schema must use Draft 2020-12")

    node_enum = set(node_schema["properties"]["kind"]["enum"])
    edge_enum = set(edge_schema["properties"]["kind"]["enum"])

    require(NODE_KINDS <= node_enum, f"node schema missing kinds: {sorted(NODE_KINDS - node_enum)}")
    require(EDGE_KINDS <= edge_enum, f"edge schema missing kinds: {sorted(EDGE_KINDS - edge_enum)}")

    defs = delta_schema.get("$defs", {})
    for kind in [
        "UpsertNodeOperation",
        "UpsertEdgeOperation",
        "AttachArtifactOperation",
        "AttachWitnessOperation",
        "VetoEdgeOperation",
        "SplitEntityOperation",
        "UnmergeEntityOperation",
        "RevokeEdgeOperation",
        "ExpireNodeOperation",
        "ExpireEdgeOperation",
    ]:
        require(kind in defs, f"delta schema missing {kind}")


def validate_node(node: dict[str, Any]) -> None:
    for field in ["node_id", "kind", "valid_time", "system_time", "attrs", "provenance"]:
        require(field in node, f"node missing required field {field}: {node}")
    require(node["kind"] in NODE_KINDS, f"unknown node kind {node['kind']}")
    require("from" in node["valid_time"] and "to" in node["valid_time"], "node valid_time must include from/to")
    require("from_version" in node["system_time"] and "to_version" in node["system_time"], "node system_time must include from_version/to_version")
    prov = node["provenance"]
    require("source_event_ids" in prov and "artifact_ids" in prov, "node provenance must include source_event_ids/artifact_ids")


def validate_edge(edge: dict[str, Any]) -> None:
    for field in ["edge_id", "kind", "src", "dst", "status", "valid_time", "system_time", "provenance"]:
        require(field in edge, f"edge missing required field {field}: {edge}")
    require(edge["kind"] in EDGE_KINDS, f"unknown edge kind {edge['kind']}")
    require(edge["status"] in {"PROPOSED", "ACTIVE", "VETOED", "REVOKED", "EXPIRED"}, f"unknown edge status {edge['status']}")
    require("from" in edge["valid_time"] and "to" in edge["valid_time"], "edge valid_time must include from/to")
    require("from_version" in edge["system_time"] and "to_version" in edge["system_time"], "edge system_time must include from_version/to_version")
    prov = edge["provenance"]
    require("source_event_ids" in prov and "artifact_ids" in prov, "edge provenance must include source_event_ids/artifact_ids")


def validate_delta(path: Path) -> None:
    delta = load_json(path)
    for field in ["delta_id", "schema_version", "emitted_at", "source_repo", "source_run_id", "trace_hash", "operations"]:
        require(field in delta, f"delta missing required field {field}")
    require(delta["operations"], "delta must include at least one operation")

    seen_proof_artifact = False
    seen_proof_ingress = False
    seen_artifact_attachment = False
    seen_veto = False

    for op in delta["operations"]:
        kind = op.get("kind")
        require(kind in DELTA_KINDS, f"unknown delta operation kind {kind}")
        if kind == "UPSERT_NODE":
            validate_node(op["node"])
            seen_proof_artifact |= op["node"]["kind"] == "PROOF_ARTIFACT"
            seen_proof_ingress |= op["node"]["kind"] == "PROOF_INGRESS_RECORD"
        elif kind == "UPSERT_EDGE":
            validate_edge(op["edge"])
            seen_artifact_attachment |= op["edge"]["kind"] == "ATTESTED_BY_PROOF"
        elif kind == "VETO_EDGE":
            seen_veto = True
            for field in ["target_edge_id", "reason_code", "artifact_id"]:
                require(field in op, f"VETO_EDGE missing {field}")

    require(seen_proof_artifact, "Michael example must materialize a PROOF_ARTIFACT node")
    require(seen_proof_ingress, "Michael example must materialize a PROOF_INGRESS_RECORD node")
    require(seen_artifact_attachment, "Michael example must include an ATTESTED_BY_PROOF edge")
    require(seen_veto, "Michael example must include a VETO_EDGE operation")


def main() -> int:
    validate_schema_files()
    validate_delta(EXAMPLE_DIR / "michael_proof_ingress_graph_delta.example.json")
    print("Regis graph contracts validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
