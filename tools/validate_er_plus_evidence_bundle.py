#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "er_plus" / "er_plus_evidence_bundle.valid.json"

RESULTS = {"MERGE_VERIFIED", "MERGE_BLOCKED", "RELATED_ONLY", "REQUIRES_REVIEW"}
METRIC_CLAIMS = {"path_cost", "quasi_metric", "metric_under_symmetric_inverse_assumptions"}


def fail(message: str) -> None:
    raise SystemExit(message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def ids(items: list[dict[str, Any]], key: str) -> set[str]:
    return {str(item.get(key)) for item in items}


def main() -> None:
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    require(data.get("schema_version") == "regis.er_plus.evidence_bundle.v0.1", "bad schema_version")

    record_ids = ids(data.get("records", []), "record_id")
    entity_ids = ids(data.get("entities", []), "entity_id")
    certs = data.get("certificates", {})
    cert_ids: set[str] = set()

    for cert in certs.get("record_paths", []):
        require(cert.get("artifact_type") == "RecordPathCertificate", "bad record path artifact_type")
        require(cert.get("metric_claim") in METRIC_CLAIMS, "bad record metric claim")
        require(cert.get("source_record_id") in record_ids, "record path source not found")
        require(cert.get("target_record_id") in record_ids, "record path target not found")
        cert_ids.add(str(cert.get("certificate_id")))

    for cert in certs.get("entity_paths", []):
        require(cert.get("artifact_type") == "EntityMovePathCertificate", "bad entity path artifact_type")
        require(cert.get("metric_claim") in METRIC_CLAIMS, "bad entity metric claim")
        require(cert.get("source_entity_id") in entity_ids, "entity path source not found")
        require(cert.get("target_entity_id") in entity_ids, "entity path target not found")
        cert_ids.add(str(cert.get("certificate_id")))

    for item in certs.get("behavioral_evidence", []):
        require(item.get("takens_claim") == "inspired_feature_only", "behavioral evidence must not overclaim Takens")
        require(item.get("entity_id") in entity_ids, "behavior entity not found")
        cert_ids.add(str(item.get("evidence_id")))

    for item in certs.get("local_expansion", []):
        require(item.get("diagnostic_kind") == "finite_graph_expansion", "local expansion must be finite-graph diagnostic")
        require(item.get("entity_id") in entity_ids, "expansion entity not found")
        cert_ids.add(str(item.get("observation_id")))

    for item in certs.get("neutrality_replays", []):
        require(item.get("artifact_type") == "NeutralityReplayRun", "bad neutrality artifact_type")
        require(item.get("result") in {"VERIFIED", "REFUTED"}, "bad neutrality result")
        cert_ids.add(str(item.get("replay_id")))

    for entry in data.get("decision_ledger", []):
        require(entry.get("artifact_type") == "ERPlusDecisionLedgerEntry", "bad ledger artifact_type")
        require(entry.get("decision") in RESULTS, "bad ledger decision")
        require(bool(entry.get("certificate_ids")), "ledger entry must cite certificates")
        missing = set(map(str, entry.get("certificate_ids", []))) - cert_ids
        require(not missing, f"ledger cites unknown certificates: {sorted(missing)}")

    print("OK: Regis ER+ evidence bundle fixture validated")


if __name__ == "__main__":
    main()
