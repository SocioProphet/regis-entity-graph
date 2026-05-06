#!/usr/bin/env python3
"""Validate Regis ACR contract pack, schemas, and examples.

This tool is intentionally small and dependency-light. It validates:
- the ACR contract-pack YAML can be parsed;
- every referenced schema and example path exists;
- JSON schemas can be parsed as JSON;
- examples validate against their referenced JSON schemas when jsonschema is installed.

If jsonschema is not installed, the tool still performs structural path and JSON parse checks
and exits successfully with a warning. CI should install jsonschema for full validation.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PACK = ROOT / "contracts" / "acr-contract-pack.yaml"

try:
    import yaml  # type: ignore
except Exception as exc:  # pragma: no cover
    print(f"ERROR: PyYAML is required to parse {CONTRACT_PACK}: {exc}", file=sys.stderr)
    sys.exit(2)

try:
    from jsonschema import Draft202012Validator  # type: ignore
except Exception:  # pragma: no cover
    Draft202012Validator = None  # type: ignore


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise AssertionError(f"invalid JSON: {path}: {exc}") from exc


def main() -> int:
    errors: List[str] = []
    warnings: List[str] = []

    if not CONTRACT_PACK.exists():
        print(f"ERROR: missing contract pack: {CONTRACT_PACK}", file=sys.stderr)
        return 2

    try:
        pack: Dict[str, Any] = yaml.safe_load(CONTRACT_PACK.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ERROR: invalid YAML contract pack: {exc}", file=sys.stderr)
        return 2

    contracts = pack.get("contracts") or {}
    if not isinstance(contracts, dict) or not contracts:
        print("ERROR: contract pack has no contracts", file=sys.stderr)
        return 2

    for name, contract in contracts.items():
        schema_rel = contract.get("path")
        if not schema_rel:
            errors.append(f"{name}: missing schema path")
            continue
        schema_path = ROOT / schema_rel
        if not schema_path.exists():
            errors.append(f"{name}: missing schema file {schema_rel}")
            continue

        try:
            schema = load_json(schema_path)
        except AssertionError as exc:
            errors.append(str(exc))
            continue

        examples = contract.get("required_examples") or []
        if not examples:
            warnings.append(f"{name}: no required_examples listed")

        for example_rel in examples:
            example_path = ROOT / example_rel
            if not example_path.exists():
                errors.append(f"{name}: missing example file {example_rel}")
                continue
            try:
                example = load_json(example_path)
            except AssertionError as exc:
                errors.append(str(exc))
                continue

            if Draft202012Validator is None:
                warnings.append(f"{name}: jsonschema not installed; skipped schema validation for {example_rel}")
                continue

            validator = Draft202012Validator(schema)
            validation_errors = sorted(validator.iter_errors(example), key=lambda e: list(e.path))
            for err in validation_errors:
                loc = "/".join(str(part) for part in err.path) or "<root>"
                errors.append(f"{name}: {example_rel}: {loc}: {err.message}")

    if warnings:
        print("WARNINGS:")
        for warning in warnings:
            print(f"- {warning}")

    if errors:
        print("ERRORS:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(json.dumps({"ok": True, "contracts_checked": len(contracts), "contract_pack": str(CONTRACT_PACK.relative_to(ROOT))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
