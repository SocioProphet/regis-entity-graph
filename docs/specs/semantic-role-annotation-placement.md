# Semantic Role Annotation over the Dependency Tree (EBA capability)

Status: v0.1. Integrates the "EBA semantic token tree" NLU capability
(prophet-workspace#76 item 7) into the estate's language-intelligence surface.

This document adds a **semantic-role annotation layer over a dependency-parsed
token tree** to the Regis entity-graph contracts. It is **consume-not-fork**: it
does not add a new parser or resolution model; it adds the missing typed
information-structure head that sits **upstream** of the NER `MentionSet` and the
EL/ER resolution lane already shipping in this repo.

## 1. The capability

A dependency-parsed token tree where each token carries **POS + dep + one or more
typed SEMANTIC ROLE annotations**. Worked example — `show me all contact lists in
my org`:

```
show (VB, ROOT)  : ActionShow            [ACTION]
me   (PRP, iobj) : ActionShow            [ACTION]
all  (DT,  det)  : —                      (function token; no role required)
contact (NN, nn) : ContactLists          [ENTITY_TYPE]
lists (NNS, dobj): ContactLists, Lists   [ENTITY_TYPE]
in   (IN,  prep) : Contains, Relation    [RELATION]
my   (PRP$, poss): Own                    [POSSESSION]
org  (NN,  pobj) : Organization          [ENTITY_TYPE]
```

Per EBA, resolution over this tree uses **restricted search with no side
effects, focused on information structure — not specific data.**

## 2. Where it sits (the genuine gap)

| Layer | Owns | Contract |
|-------|------|----------|
| SynapseIQ (tree-sitter + LSP) | syntax over **source code** | mapping-DSL grammar/lowering (synapseiq#31) |
| Regis NER | mention/span **typing** over text | `schemas/ner/mention.schema.json` (regis #16) |
| GrASP (sociosphere) | masking / tokenization | sociosphere#539 |
| **Semantic token tree (this)** | **semantic roles over an NL dependency tree** | `schemas/nlu/semantic-token-tree.schema.json` (**new**) |

The syntax-plus-semantic-role layer over a natural-language dependency tree is
the piece none of the above carried. It is the typed information-structure input
to NER (`Token.span` aligns to `Mention.span`) and, through NER, to EL/ER.

## 3. What is new

- **`SemanticTokenTree` / `Token`** — provenance/locality-stamped, dependency
  parsed tokens carrying `pos`, `dep`, `head`, and `semantic_roles[]`.
- **`SemanticRole`** — a `{label, kind}` pair. `kind` is a **closed** structural
  taxonomy (`schemas/nlu/semantic-role-kind.schema.json`): `ACTION`,
  `ENTITY_TYPE`, `RELATION`, `QUANTIFIER`, `POSSESSION`, `MODIFIER`, `CONTEXT`.
- **Open, LEARNED labels.** `label` (ActionShow, ContactLists, Organization) is
  **not** enumerated. Per the estate rule *learn, don't match dictionaries*, the
  label vocabulary is produced by a learned resolver over the parse's
  information structure; this contract governs how a label is *typed*, not which
  labels may exist.
- **A restricted, side-effect-free resolver** (`tools/validate_semantic_token_tree.py`)
  whose EBA properties are *tested, not asserted* (see §5).

## 4. Contract shape

- `schema_version`: `regis.nlu.semantic_token_tree.v0.1`
- `utterance_ref` (`utterance_id`, `source_type`), `locality` scope-stamp,
  `parser_version`, optional `text`.
- `tokens[]`: `token_id`, `surface`, `pos`, `dep`, `head` (null iff `ROOT`),
  `semantic_roles[]`, optional `lemma`/`span`.
- Load-bearing deps (`ROOT`, `nsubj`, `dobj`, `iobj`, `pobj`, `nn`, `compound`,
  `prep`, `poss`) **must** carry ≥1 role; function tokens (`det`, `punct`, …)
  may be empty.

## 5. Teeth

`make validate-semantic-token-tree`:

**Positive** — `fixtures/nlu/semantic_token_tree.valid.json` (the exact
"show me all contact lists in my org" utterance) must resolve, and the resolver
output is pinned to the transcribed roles (`show`→ActionShow, `lists`→
ContactLists+Lists, `in`→Contains+Relation, `org`→Organization, `my`→Own).

The EBA properties are made checkable:
- **side-effect-free** — the resolver runs on a deep copy and the validator
  asserts the input is byte-for-byte unchanged afterward;
- **information structure, not data** — the resolver records every field it
  reads and the validator asserts it consulted only structural fields
  (`token_id`/`pos`/`dep`/`head`/`semantic_roles`) and never data fields
  (`surface`/`lemma`/`text`/`span`);
- **restricted search** — head-chain traversal is bounded by the token count;
  cyclic head graphs are rejected.

**Negative** — every `fixtures/nlu/*.invalid.json` is rejected:
- `unknown-role-kind` — a role `kind` outside the taxonomy;
- `role-on-headless-token` — a non-ROOT token carrying a role with a null head;
- `empty-roles-where-required` — a load-bearing dep with empty `semantic_roles`;
- `head-out-of-range` — `head` referencing a non-existent `token_id`.

## 6. Not yet buildable-now (tracked as issues)

- **Live parser wiring** — an actual dependency parser emitting this contract at
  a bounded, side-effect-free locality; cross-ref synapseiq#31 (syntax lane).
- **Learned role-label lexicon** — the LEARNED (not static-dictionary) resolver
  that assigns `label`s over the information structure, with drift/eval; cross-ref
  regis #16 (NER mention contract) for the downstream span alignment.
- **`Token.span` ⇄ `Mention.span` alignment check** — a validator lane proving
  the semantic tree and the NER `MentionSet` index the same offsets.
