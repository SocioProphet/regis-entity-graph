#!/usr/bin/env python3
"""Validate cross-layer span alignment between the NLU semantic token tree and
the NER MentionSet (regis-entity-graph#25).

Gap this closes
---------------
#16 (MERGED) gave us ``schemas/ner/mention.schema.json``: mentions carry a span
(start/end) and an ``entity_class``.
#22 (MERGED) gave us ``schemas/nlu/semantic-token-tree.schema.json``: tokens
carry pos/dep/head plus typed ``semantic_roles``, and an optional span.

Nothing checked that the two layers *agree on where an entity is*. A token that
claims an ``ENTITY_TYPE`` semantic role is asserting "there is a typed entity
here"; the NER layer independently asserts the same via a Mention span. If those
two spans disagree — off by one, out of range, or crossing a mention boundary —
the NLU and NER layers have silently drifted and downstream EL/ER grounding will
attach roles to the wrong entity. This lane makes that disagreement fail closed.

Consume-not-fork
----------------
This lane does NOT re-implement the two upstream contracts. It imports and runs
the existing ``validate_semantic_token_tree`` and ``validate_ner_contracts``
lanes on the sub-documents first, so every alignment fixture is a pair of two
*already-valid* documents; any rejection here is therefore attributable to the
alignment defect alone, not to a malformed tree or mention set.

Alignment rule
--------------
A fixture pairs one SemanticTokenTree with one MentionSet over the same source
(linked by ``event_ir_id``). Then:

* Forward (token -> mention): every token that carries an ``ENTITY_TYPE``
  semantic role and has a span MUST align with some Mention span, where "align"
  means the token span EQUALS or is CONTAINED BY the mention span. A token whose
  entity span overlaps no mention, or overlaps one but crosses its boundary, is
  REJECTED.
* Reverse (mention -> token), where required: every Mention whose ``entity_class``
  is a concrete named-entity class (PERSON/ORG/LOCATION/... — not a contextual
  overlay such as CHILD_CONTEXT) MUST contain (or equal) at least one
  ``ENTITY_TYPE`` token span. A named entity the NLU layer never role-typed is
  REJECTED.
* Range: when the tree carries ``text``, every token and mention span must be
  well-formed (0 <= start < end <= len(text)). Out-of-range spans are REJECTED.

Teeth both ways: the aligned fixture MUST pass and MUST exercise both an equality
alignment and a strict-containment alignment; every ``*.invalid.json`` MUST be
rejected for the reason encoded in its filename.

FIPS note: SHA-256 (FIPS-180-4) remains the authoritative digest for any hashing
in the upstream contracts; this lane adds no new crypto.

Stdlib-only, matching the other validate_* lanes in this repo.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT / "tools"
FIXTURE_DIR = ROOT / "fixtures" / "span-alignment"

# Consume, don't fork: reuse the upstream contract validators verbatim.
sys.path.insert(0, str(TOOLS_DIR))
from validate_semantic_token_tree import validate_tree  # noqa: E402
from validate_ner_contracts import validate_mention_set, ENTITY_CLASSES  # noqa: E402

# The semantic-role kind that asserts "a typed entity sits at this token span".
ENTITY_ROLE_KIND = "ENTITY_TYPE"

# Concrete named-entity classes: a Mention of one of these is a claim that a real
# entity occupies its span, so the NLU layer is REQUIRED to have role-typed it.
# Contextual/overlay classes (CHILD_CONTEXT, SENSITIVE_CONTEXT, POLICY_TERM, ...)
# annotate *about* a region and are NOT required to have a matching entity token.
REQUIRE_TOKEN_CLASSES = {
    "PERSON",
    "ORG",
    "PRODUCT_SERVICE",
    "DEVICE",
    "ACCOUNT",
    "IDENTIFIER",
    "CREDENTIAL",
    "LOCATION",
    "JURISDICTION",
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _span(obj: dict[str, Any]) -> tuple[int, int]:
    s = obj["span"]
    return (s["start"], s["end"])


def is_equal(ts: tuple[int, int], ms: tuple[int, int]) -> bool:
    return ts == ms


def is_contained(ts: tuple[int, int], ms: tuple[int, int]) -> bool:
    """token span ts is contained by (or equal to) mention span ms."""
    return ms[0] <= ts[0] and ts[1] <= ms[1]


def is_aligned(ts: tuple[int, int], ms: tuple[int, int]) -> bool:
    return is_contained(ts, ms)  # equality is the boundary case of containment


def spans_overlap(a: tuple[int, int], b: tuple[int, int]) -> bool:
    return a[0] < b[1] and b[0] < a[1]


def entity_typed_tokens(tree: dict[str, Any]) -> list[dict[str, Any]]:
    """Tokens carrying at least one ENTITY_TYPE role AND a span (only spanned
    tokens are checkable against mention spans)."""
    out: list[dict[str, Any]] = []
    for tok in tree["tokens"]:
        if "span" not in tok:
            continue
        if any(r.get("kind") == ENTITY_ROLE_KIND for r in tok.get("semantic_roles", [])):
            out.append(tok)
    return out


def _event_ref(doc: dict[str, Any], ref_key: str) -> Any:
    return doc.get(ref_key, {}).get("event_ir_id")


def validate_alignment(pair: dict[str, Any]) -> dict[str, Any]:
    require("tree" in pair and "mentions" in pair, "fixture must carry 'tree' and 'mentions'")
    tree = pair["tree"]
    mentions_doc = pair["mentions"]

    # 1. Each sub-document must satisfy its own upstream contract first, so any
    #    failure below is an ALIGNMENT failure, not a malformed input.
    validate_tree(tree)
    validate_mention_set(mentions_doc)

    # 2. The two layers must be over the same source (same Event-IR).
    tree_ev = _event_ref(tree, "utterance_ref")
    ner_ev = _event_ref(mentions_doc, "source_ref")
    require(tree_ev is not None, "tree.utterance_ref.event_ir_id required for alignment")
    require(ner_ev is not None, "mentions.source_ref.event_ir_id required for alignment")
    require(
        tree_ev == ner_ev,
        f"tree/mention layers are not over the same source: {tree_ev!r} != {ner_ev!r}",
    )

    mentions = mentions_doc["mentions"]
    mention_spans = [(_span(m), m) for m in mentions]

    # 3. Range check against the canonical text when present.
    text = tree.get("text")
    if isinstance(text, str):
        tlen = len(text)
        for tok in tree["tokens"]:
            if "span" not in tok:
                continue
            ts = _span(tok)
            require(
                0 <= ts[0] < ts[1] <= tlen,
                f"token {tok['token_id']} span {ts} out of range for text len {tlen}",
            )
        for ms, m in mention_spans:
            require(
                0 <= ms[0] < ms[1] <= tlen,
                f"mention {m['mention_id']} span {ms} out of range for text len {tlen}",
            )

    # 4. Forward: every ENTITY_TYPE token span must align with a mention span.
    ent_tokens = entity_typed_tokens(tree)
    equality_hits = 0
    containment_hits = 0
    for tok in ent_tokens:
        ts = _span(tok)
        aligned = [(ms, m) for ms, m in mention_spans if is_aligned(ts, ms)]
        overlapping = [(ms, m) for ms, m in mention_spans if spans_overlap(ts, ms)]
        require(
            aligned,
            f"token {tok['token_id']} claims ENTITY_TYPE at span {ts} but no Mention "
            f"span contains it"
            + (
                f" (crosses boundary of mention(s) "
                f"{[m['mention_id'] for _, m in overlapping]})"
                if overlapping
                else " (no overlapping Mention)"
            ),
        )
        for ms, _ in aligned:
            if is_equal(ts, ms):
                equality_hits += 1
            elif is_contained(ts, ms):
                containment_hits += 1

    # 5. Reverse (where required): every concrete named-entity Mention must
    #    contain/equal at least one ENTITY_TYPE token span.
    for ms, m in mention_spans:
        if m["entity_class"] not in REQUIRE_TOKEN_CLASSES:
            continue
        covering = [tok for tok in ent_tokens if is_aligned(_span(tok), ms)]
        require(
            covering,
            f"mention {m['mention_id']} ({m['entity_class']}) at span {ms} has no "
            f"aligning ENTITY_TYPE token in the semantic tree",
        )

    return {
        "entity_tokens": len(ent_tokens),
        "mentions": len(mentions),
        "equality_alignments": equality_hits,
        "containment_alignments": containment_hits,
    }


def assert_alignment_modes_exercised(pair: dict[str, Any]) -> None:
    """Positive teeth: the valid fixture must exercise BOTH alignment code paths —
    at least one exact-equality match and at least one strict-containment match —
    otherwise one branch of the contract is untested."""
    result = validate_alignment(pair)
    require(
        result["equality_alignments"] >= 1,
        "valid fixture must exercise at least one equality alignment",
    )
    require(
        result["containment_alignments"] >= 1,
        "valid fixture must exercise at least one strict-containment alignment",
    )


def main() -> int:
    # Guard: the entity classes we require token coverage for must all be real
    # classes in the NER taxonomy (fail if the taxonomy is renamed under us).
    require(
        REQUIRE_TOKEN_CLASSES <= ENTITY_CLASSES,
        f"REQUIRE_TOKEN_CLASSES drifted from NER taxonomy: "
        f"{REQUIRE_TOKEN_CLASSES - ENTITY_CLASSES}",
    )

    valid_path = FIXTURE_DIR / "aligned.valid.json"
    require(valid_path.exists(), f"missing valid fixture {valid_path}")
    valid_pair = load_json(valid_path)
    assert_alignment_modes_exercised(valid_pair)

    invalid_fixtures = sorted(FIXTURE_DIR.glob("*.invalid.json"))
    require(invalid_fixtures, "expected at least one *.invalid.json rejection fixture")
    for path in invalid_fixtures:
        try:
            validate_alignment(load_json(path))
        except AssertionError:
            continue
        raise AssertionError(f"invalid alignment fixture was wrongly accepted: {path.name}")

    print(
        f"Regis span-alignment contract validated "
        f"(token.span <-> mention.span; 1 valid + {len(invalid_fixtures)} rejection fixtures)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
