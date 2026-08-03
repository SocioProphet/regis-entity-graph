#!/usr/bin/env python3
"""Validate DecisionLedgerSeal tamper-evidence over ACR DecisionLedgerEntry.

Additive to the ACR contract pack. Checks the invariants that JSON Schema alone
cannot express:
  - SEAL-1 entry binding : seal.entry_hash == hashseal(referenced DecisionLedgerEntry)
  - SEAL-2 chain link     : prev_seal_hash links to the prior seal in chain_id
  - SEAL-3 no fork        : seq strictly increments per chain_id; no reused prev_seal_hash
  - SEAL-4 idempotency    : idempotency_key == hashseal([decision_id, policy_version, sorted(input_hashes)])
  - SEAL-5 authenticity   : ed25519 signature over entry_hash verifies under a known key

Dependency-light and house-consistent with tools/validate_acr_contracts.py:
blake3 + cryptography enable full checks; if absent, structural checks still run
and the tool exits 0 with a warning (CI installs them for full validation).

hashseal = blake3-256 over RFC-8785-JCS-approx (sorted keys, compact separators).
NOTE (E1): the exact estate canonicalizer must be bound in WO_FIBER_001; this is a
faithful reference, self-consistent but not yet asserted wire-compatible.
"""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

try:
    import blake3  # type: ignore
    def _h(b: bytes) -> str: return blake3.blake3(b).hexdigest()[:64]
    HAVE_HASH = True
except Exception:
    import hashlib
    def _h(b: bytes) -> str: return hashlib.blake2b(b, digest_size=32).hexdigest()  # fallback
    HAVE_HASH = False

try:
    from cryptography.hazmat.primitives.asymmetric import ed25519
    HAVE_SIG = True
except Exception:
    HAVE_SIG = False


def jcs(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")

def hashseal(obj) -> str:
    return _h(jcs(obj))

def idem(decision_id: str, policy_version: str, input_hashes) -> str:
    return hashseal([decision_id, policy_version, sorted(input_hashes or [])])


def validate(seals: list[dict], entries: dict[str, dict], keyring: dict) -> list[str]:
    errs: list[str] = []
    by_chain: dict[str, list[dict]] = {}
    for s in seals:
        by_chain.setdefault(s["chain_id"], []).append(s)
        e = entries.get(s["decision_id"])
        if e is None:
            errs.append(f"SEAL-1: decision_id {s['decision_id']} not found"); continue
        if HAVE_HASH and s["entry_hash"] != hashseal(e):
            errs.append(f"SEAL-1: entry_hash mismatch for {s['decision_id']}")
        rep = e.get("replay", {})
        if HAVE_HASH:
            want = idem(s["decision_id"], rep.get("policy_version", ""), rep.get("input_hashes", []))
            if s["idempotency_key"] != want:
                errs.append(f"SEAL-4: idempotency_key mismatch for {s['decision_id']}")
        if HAVE_SIG:
            pk = keyring.get(s["signature"]["key_id"])
            if pk is None:
                errs.append(f"SEAL-5: unknown key_id {s['signature']['key_id']}")
            elif s["signature"]["alg"] == "ed25519":
                try:
                    pk.verify(bytes.fromhex(s["signature"]["value"]), s["entry_hash"].encode())
                except Exception:
                    errs.append(f"SEAL-5: signature invalid for seal {s['seal_id']}")
    for cid, ss in by_chain.items():
        ss = sorted(ss, key=lambda x: x["seq"])
        seen_prev = set()
        for i, s in enumerate(ss):
            if i > 0 and s["seq"] != ss[i-1]["seq"] + 1:
                errs.append(f"SEAL-3: non-monotonic seq in chain {cid}")
            if s["prev_seal_hash"] in seen_prev and s["prev_seal_hash"] != "GENESIS":
                errs.append(f"SEAL-3: fork (reused prev_seal_hash) in chain {cid}")
            seen_prev.add(s["prev_seal_hash"])
            if i > 0 and HAVE_HASH and s["prev_seal_hash"] != hashseal(ss[i-1]):
                errs.append(f"SEAL-2: broken chain link at seq {s['seq']} in {cid}")
    return errs


def _load_example():
    seal_p = ROOT / "examples" / "acr" / "decision-ledger-seal.chain.example.json"
    if not seal_p.exists():
        print(f"WARN: no example at {seal_p}; nothing to validate"); return None
    doc = json.loads(seal_p.read_text())
    return doc


def main() -> int:
    if not HAVE_HASH:
        print("WARN: blake3 not installed; running structural checks only (CI installs blake3).")
    if not HAVE_SIG:
        print("WARN: cryptography not installed; skipping signature checks (CI installs it).")
    doc = _load_example()
    if doc is None:
        return 0
    seals = doc.get("seals", [])
    entries = {e["decision_id"]: e for e in doc.get("entries", [])}
    keyring = {}
    if HAVE_SIG:
        for k in doc.get("_test_keys", []):
            keyring[k["key_id"]] = ed25519.Ed25519PublicKey.from_public_bytes(bytes.fromhex(k["public_hex"]))
    errs = validate(seals, entries, keyring)
    if errs:
        print("FAIL: DecisionLedgerSeal invariants violated:")
        for e in errs:
            print("  -", e)
        return 1
    print(f"OK: {len(seals)} seal(s) conformant (SEAL-1..5).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
