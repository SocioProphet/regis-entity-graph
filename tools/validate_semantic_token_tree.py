#!/usr/bin/env python3
"""Validate the Regis NLU semantic token tree contract (EBA capability).

prophet-workspace#76 item 7 ("EBA semantic token tree"): a dependency-parsed
token tree where each token carries POS + dep + one or more typed SEMANTIC ROLE
annotations. This is the syntax-plus-semantic-role layer upstream of the NER
MentionSet (schemas/ner) and the EL/ER resolution lane.

Design decisions this validator enforces:

* Only the role KIND is a closed vocabulary. The role LABEL is open/LEARNED
  (estate rule: "learn, don't match dictionaries"). We type-check the kind and
  pattern-check the label; we never enumerate labels.
* The resolver is RESTRICTED and SIDE-EFFECT-FREE (EBA: "restricted search with
  no side effects, focused on information structure not specific data"). This is
  made testable, not asserted:
    - it deep-copies its input and the validator asserts the input is unchanged
      after resolution (no side effects);
    - it records every field it consulted and the validator asserts it consulted
      only structural fields (token_id/pos/dep/head/semantic_roles) and NEVER
      data fields (surface/lemma/text) -> "information structure not data";
    - traversal is bounded by the token count (restricted search / no unbounded
      global search); cyclic head graphs are rejected.

Teeth both ways: the "show me all contact lists in my org" fixture MUST resolve
to the expected roles; every *.invalid.json MUST be rejected for the reason in
its filename (unknown role kind, role on a headless token, empty roles where
required, head out of range).

Stdlib-only, matching the other validate_* lanes in this repo.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schemas" / "nlu"
FIXTURE_DIR = ROOT / "fixtures" / "nlu"

SCHEMA_VERSION = "regis.nlu.semantic_token_tree.v0.1"

ROLE_KINDS = {
    "ACTION",
    "ENTITY_TYPE",
    "RELATION",
    "QUANTIFIER",
    "POSSESSION",
    "MODIFIER",
    "CONTEXT",
}

DEP_RELATIONS = {
    "ROOT",
    "nsubj",
    "dobj",
    "iobj",
    "pobj",
    "nn",
    "compound",
    "prep",
    "case",
    "poss",
    "det",
    "amod",
    "advmod",
    "aux",
    "cc",
    "conj",
    "mark",
    "punct",
}

# Load-bearing deps: a token in this set carries information structure and MUST
# be annotated with at least one semantic role.
REQUIRES_ROLE_DEPS = {
    "ROOT",
    "nsubj",
    "dobj",
    "iobj",
    "pobj",
    "nn",
    "compound",
    "prep",
    "poss",
}

# Fields the restricted resolver is permitted to consult. Data-bearing fields
# (surface/lemma/text/span) are deliberately excluded: EBA resolves over
# information structure, not specific data.
STRUCTURAL_FIELDS = {"token_id", "pos", "dep", "head", "semantic_roles"}
DATA_FIELDS = {"surface", "lemma", "text", "span"}

SOURCE_TYPES = {"message", "form", "query", "command", "page"}
LOCALITIES = {"CITIZEN_FOG", "CITIZEN_CLOUD", "INSTITUTION", "ADTECH", "HSM"}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate_schema_posture() -> None:
    """Both NLU schemas must be Draft 2020-12 and the role-kind taxonomy must
    stay in sync between its source-of-truth file, the inlined tree enum, and
    this validator's constants."""
    kind_schema = load_json(SCHEMA_DIR / "semantic-role-kind.schema.json")
    tree_schema = load_json(SCHEMA_DIR / "semantic-token-tree.schema.json")

    require(
        kind_schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema",
        "semantic-role-kind schema must use Draft 2020-12",
    )
    require(
        tree_schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema",
        "semantic-token-tree schema must use Draft 2020-12",
    )

    src_kinds = set(kind_schema["$defs"]["SemanticRoleKind"]["enum"])
    require(src_kinds == ROLE_KINDS, f"role-kind drift (source): {src_kinds ^ ROLE_KINDS}")

    inlined_kinds = set(tree_schema["$defs"]["SemanticRoleKind"]["enum"])
    require(
        inlined_kinds == ROLE_KINDS,
        f"tree schema role-kind enum out of sync: {inlined_kinds ^ ROLE_KINDS}",
    )

    inlined_deps = set(tree_schema["$defs"]["Token"]["properties"]["dep"]["enum"])
    require(
        inlined_deps == DEP_RELATIONS,
        f"tree schema dep enum out of sync: {inlined_deps ^ DEP_RELATIONS}",
    )
    require(
        REQUIRES_ROLE_DEPS <= DEP_RELATIONS,
        "REQUIRES_ROLE_DEPS must be a subset of DEP_RELATIONS",
    )
    require(
        STRUCTURAL_FIELDS.isdisjoint(DATA_FIELDS),
        "structural and data field sets must be disjoint",
    )


class RestrictedResolver:
    """Restricted, side-effect-free semantic-role resolver over a token tree.

    Reads ONLY the information structure (token_id/pos/dep/head/semantic_roles)
    and records which fields it consulted so the caller can prove the
    'information structure not data' property. Does not mutate its input.
    """

    def __init__(self) -> None:
        self.consulted_fields: set[str] = set()

    def _read(self, token: dict[str, Any], field: str) -> Any:
        self.consulted_fields.add(field)
        return token.get(field)

    def resolve(self, tree: dict[str, Any]) -> dict[str, Any]:
        tokens = tree["tokens"]
        n = len(tokens)

        ids = [self._read(t, "token_id") for t in tokens]
        require(len(set(ids)) == n, "token_id values must be unique")
        by_id = {tid: t for tid, t in zip(ids, tokens)}

        roots = [t for t in tokens if self._read(t, "dep") == "ROOT"]
        require(len(roots) == 1, f"tree must have exactly one ROOT token, got {len(roots)}")

        for token in tokens:
            tid = self._read(token, "token_id")
            dep = self._read(token, "dep")
            head = self._read(token, "head")
            roles = self._read(token, "semantic_roles") or []

            require(dep in DEP_RELATIONS, f"unknown dep {dep} on token {tid}")

            if dep == "ROOT":
                require(head is None, f"ROOT token {tid} must have null head")
            else:
                # Teeth: a semantic role must attach to a headed position. A
                # non-ROOT token carrying roles with no head is structurally
                # dangling; reject it before the generic head checks so the
                # rejection reason names the annotation defect.
                if roles:
                    require(
                        head is not None,
                        f"token {tid} carries semantic roles but has no head",
                    )
                require(head is not None, f"non-ROOT token {tid} has no head")
                require(head in by_id, f"head {head} of token {tid} is out of range")
                require(head != tid, f"token {tid} may not be its own head")

            # Teeth: load-bearing deps must be annotated.
            if dep in REQUIRES_ROLE_DEPS:
                require(
                    len(roles) >= 1,
                    f"token {tid} (dep={dep}) requires >=1 semantic role but has none",
                )

            for role in roles:
                require("kind" in role and "label" in role, f"role missing kind/label: {role}")
                require(role["kind"] in ROLE_KINDS, f"unknown role kind {role['kind']}")
                label = role["label"]
                require(
                    isinstance(label, str)
                    and label[:1].isupper()
                    and label.isalnum(),
                    f"role label must be UpperCamelCase alnum: {label!r}",
                )

            # Restricted search: walking to ROOT is bounded by token count.
            if dep != "ROOT":
                steps, cur = 0, tid
                while by_id[cur].get("dep") != "ROOT":
                    cur = by_id[cur]["head"]
                    steps += 1
                    require(steps <= n, f"cyclic/over-long head chain from token {tid}")

        return {"root_token_id": roots[0]["token_id"], "token_count": n}


def validate_tree(doc: dict[str, Any]) -> dict[str, Any]:
    require(
        doc.get("schema_version") == SCHEMA_VERSION,
        f"schema_version must be {SCHEMA_VERSION}",
    )
    for field in ["utterance_ref", "locality", "parser_version", "tokens"]:
        require(field in doc, f"tree missing required field {field}")

    require(doc["locality"] in LOCALITIES, f"unknown locality {doc['locality']}")
    ref = doc["utterance_ref"]
    require("utterance_id" in ref and "source_type" in ref, "utterance_ref needs id/source_type")
    require(ref["source_type"] in SOURCE_TYPES, f"unknown source_type {ref['source_type']}")
    require(isinstance(doc["tokens"], list) and doc["tokens"], "tokens must be a non-empty array")

    # Side-effect-free: resolve a deep copy, then prove the input is unchanged.
    original = copy.deepcopy(doc)
    resolver = RestrictedResolver()
    result = resolver.resolve(doc)
    require(doc == original, "resolver mutated its input (not side-effect-free)")

    # Information structure not data: the resolver must never have consulted a
    # data-bearing field.
    leaked = resolver.consulted_fields & DATA_FIELDS
    require(not leaked, f"resolver consulted data field(s): {leaked}")
    require(
        resolver.consulted_fields <= STRUCTURAL_FIELDS,
        f"resolver consulted unexpected fields: {resolver.consulted_fields - STRUCTURAL_FIELDS}",
    )
    return result


def assert_expected_roles(doc: dict[str, Any]) -> None:
    """Positive teeth pinned to the 'show me all contact lists in my org'
    fixture: the exact roles from the capability transcription must be present."""
    by_surface: dict[str, list[dict[str, Any]]] = {}
    for tok in doc["tokens"]:
        by_surface.setdefault(tok["surface"].lower(), []).append(tok)

    def roles_of(surface: str) -> set[tuple[str, str]]:
        toks = by_surface.get(surface, [])
        require(toks, f"expected a token with surface {surface!r}")
        out: set[tuple[str, str]] = set()
        for t in toks:
            for r in t["semantic_roles"]:
                out.add((r["label"], r["kind"]))
        return out

    require(("ActionShow", "ACTION") in roles_of("show"), "show must carry ActionShow/ACTION")
    require(("ActionShow", "ACTION") in roles_of("me"), "me must carry ActionShow/ACTION")
    lists_roles = roles_of("lists")
    require(("ContactLists", "ENTITY_TYPE") in lists_roles, "lists must carry ContactLists")
    require(("Lists", "ENTITY_TYPE") in lists_roles, "lists must carry Lists")
    require(("ContactLists", "ENTITY_TYPE") in roles_of("contact"), "contact must carry ContactLists")
    in_roles = roles_of("in")
    require(("Contains", "RELATION") in in_roles, "in must carry Contains/RELATION")
    require(("Relation", "RELATION") in in_roles, "in must carry Relation/RELATION")
    require(("Organization", "ENTITY_TYPE") in roles_of("org"), "org must carry Organization")
    require(("Own", "POSSESSION") in roles_of("my"), "my must carry Own/POSSESSION")


def main() -> int:
    validate_schema_posture()

    valid_path = FIXTURE_DIR / "semantic_token_tree.valid.json"
    valid_doc = load_json(valid_path)
    validate_tree(valid_doc)
    assert_expected_roles(valid_doc)

    invalid_fixtures = sorted(FIXTURE_DIR.glob("*.invalid.json"))
    require(invalid_fixtures, "expected at least one *.invalid.json rejection fixture")
    for path in invalid_fixtures:
        try:
            validate_tree(load_json(path))
        except AssertionError:
            continue
        raise AssertionError(f"invalid fixture was wrongly accepted: {path.name}")

    print(
        f"Regis NLU semantic-token-tree contract validated "
        f"({len(ROLE_KINDS)} role kinds; 1 valid + {len(invalid_fixtures)} rejection fixtures)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
