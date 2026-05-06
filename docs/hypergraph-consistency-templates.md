# Hypergraph Consistency Templates for Concordance-Grade Entity Resolution

This document captures a concordance-grade design pattern for Regis Entity Graph. The purpose is to preserve conflicting source claims, normalize them into canonical legal-entity representations, and expose deterministic downstream projections for analytics, compliance, agent reasoning, and operational consumption.

## Core thesis

Concordance is not just deduplication. Deduplication says two rows are probably the same thing; concordance says which claims survive, which claims conflict, which source asserted each claim, why the canonical value was selected, and what downstream systems are allowed to consume. Tiny goblin distinction, enormous systems consequence.

Regis should model this as a hypergraph because legal entity resolution involves relationships among more than two things at once: a source record, a raw attribute, a normalized attribute, a canonical entity, a policy rule, a confidence score, and evidence. A normal edge can say `A matches B`; a hyperedge can say `A matched B under policy P using evidence E with score S as of time T`.

## Node templates

### CanonicalLegalEntity

Represents the resolved legal entity consumed downstream.

Required fields:

- `id`
- `type = CanonicalLegalEntity`
- `legal_name`
- `canonical_status`
- `confidence`
- `valid_time`
- `transaction_time`
- `provenance`

Common attributes:

- `registered_address`
- `headquarters_address`
- `country_of_registration`
- `jurisdiction`
- `url`
- `entity_type`
- `ultimate_parent_id`
- `coverage_status`
- `quality_flags`

Identifier families:

- `LEI`
- `CIK`
- `DUNS`
- `CUSIP`
- `ISIN`
- `SEDOL`
- `BIC_SWIFT`
- `GICS`
- `NAICS`
- `SIC`
- `MIC`
- `RIC`
- `ticker`
- `exchange`
- `internal_marketing_id`
- `internal_crm_id`

### SourceEntityRecord

Represents one raw upstream row or document fragment from CRM, reference data, vendor feeds, filings, or analyst-curated sources.

Fields:

- `id`
- `source_system`
- `source_primary_key`
- `record_json`
- `extraction_time`
- `ingest_job_id`
- `ingest_version`
- `source_confidence`
- `provenance`

### AttributeClaim

Represents a single asserted field-value pair from any source.

Fields:

- `id`
- `attribute_name`
- `raw_value`
- `normalized_value`
- `datatype`
- `normalization_rule`
- `language`
- `confidence`
- `source_record_id`
- `valid_time`
- `transaction_time`

Examples:

- `name = Tesco Stores`
- `name = Tesco plc`
- `country = UK`
- `country = United Kingdom`
- `postal_code = EN8 9SL`
- `ticker = TSCO`
- `ticker = TSC`

### ExternalIdentifier

Represents a typed identifier rather than burying identifiers as loose strings.

Fields:

- `id`
- `scheme`
- `value`
- `issuer`
- `checksum_status`
- `scope`
- `valid_time`
- `transaction_time`

Supported schemes should include `LEI`, `DUNS`, `ISIN`, `SEDOL`, `CUSIP`, `BIC_SWIFT`, `MIC`, `RIC`, `CIK`, `GICS`, `NAICS`, and `SIC`.

### Authority

Represents regulators, exchanges, rating agencies, and other authoritative sources.

Fields:

- `id`
- `authority_type`
- `name`
- `country`
- `code`
- `url`

Authority subtypes:

- `REGULATOR`
- `EXCHANGE`
- `RATING_AGENCY`
- `REGISTRY`
- `VENDOR_FEED`

## Hyperedge templates

### CONCORDS_WITH

Connects a `SourceEntityRecord`, one or more `AttributeClaim` nodes, a `CanonicalLegalEntity`, policy rules, evidence references, and a decision score.

Properties:

- `score`
- `decision = match | possible_match | no_match | split | merge_review`
- `threshold`
- `contributing_features`
- `policy_rule_ids`
- `reviewer = auto | human | agent`
- `decision_time`

### NORMALIZES_TO

Connects raw and normalized claims.

Examples:

- `UK -> GB`
- `United Kingdom -> GB`
- `www.tescoplc.com -> tescoplc.com`

### CONFLICTS_WITH

Preserves contradictions instead of deleting them.

Examples:

- `ticker = TSCO` conflicts with `ticker = TSC`
- `DUNS = 216854067` conflicts with `DUNS = 216854667`
- `SEDOL = 0884709` conflicts with a checksum-invalid or stale SEDOL

### IDENTIFIED_BY

Connects a canonical legal entity to an external identifier.

Properties:

- `scheme`
- `confidence`
- `verification_status`
- `evidence_refs`
- `valid_time`

### LISTED_ON

Connects a canonical entity to an exchange authority.

Properties:

- `ticker`
- `ric`
- `sedol`
- `isin`
- `mic`
- `first_list_date`
- `last_verified_at`

### RATED_BY

Connects a canonical entity to a rating agency.

Properties:

- `agency`
- `rating`
- `outlook`
- `as_of`
- `instrument_or_issuer_scope`

### REGULATED_BY

Connects a canonical entity to a regulator.

Properties:

- `regulator_id`
- `license_number`
- `regulated_activity`
- `jurisdiction`
- `as_of`

### PARENT_OF

Models ownership or control relationships.

Properties:

- `relationship = ultimate_parent | immediate_parent | subsidiary | affiliate`
- `ownership_percent`
- `control_basis`
- `as_of`

### DERIVED_FROM

Connects canonical attributes back to raw source fields and evidence. This is the anti-handwave edge. Without it, the graph becomes a vibes aquarium.

Properties:

- `source_system`
- `source_pk`
- `field_path`
- `evidence_uri`
- `transform_rule`
- `confidence`

## Consistency policy template

### Coverage rule

A `CanonicalLegalEntity` qualifies for authority-file coverage when at least one of the following is true:

- the entity is listed on a recognized exchange;
- the entity is rated by a recognized rating agency;
- the entity is regulated by a recognized regulator;
- the entity is otherwise admitted by a configured domain authority policy.

### Identifier integrity rules

- `LEI` should be 20 alphanumeric characters and checked against the configured LEI validation policy.
- `ISIN` should be 12 characters and pass checksum validation.
- `SEDOL` should be 7 characters and pass checksum validation where applicable.
- `CUSIP` should be 9 characters and pass checksum validation where applicable.
- `DUNS` should be 9 digits where used.
- `BIC_SWIFT` should be 8 or 11 alphanumeric characters.
- `MIC` should use the exchange code authority configured in the platform.

### Geography and address rules

- `country_of_registration` must normalize to ISO-3166 representation.
- Address claims should preserve raw source text and normalized components.
- Postal-code validation should be jurisdiction-aware.
- Missing city, postal code, country, or street should set explicit quality flags rather than disappearing into the fog machine of enterprise data quality.

### Name normalization rules

- Preserve raw names.
- Normalize Unicode using a configured normal form.
- Strip or classify legal suffixes such as `plc`, `ltd`, `inc`, `corp`, and `gmbh` without destroying the legal name.
- Maintain aliases and rejected aliases as claims with decisions.

## Merge decision template

```json
{
  "edge_type": "CONCORDS_WITH",
  "source_record_id": "ser_crm_C1055598",
  "canonical_entity_id": "cle_tesco_plc",
  "score": 0.931,
  "threshold": 0.92,
  "decision": "match",
  "policy": "regis-concordance-policy-v1",
  "signals": [
    "name_similarity:0.97",
    "postal_code_exact:true",
    "url_domain_match:true",
    "identifier_overlap:1"
  ],
  "reviewer": "auto",
  "decision_time": "2026-01-01T00:00:00Z"
}
```

## Downstream consumption templates

### Canonical wide view

Purpose: warehouses, BI, compliance reporting, and simple service integrations.

Columns:

- `canonical_entity_id`
- `legal_name`
- `country_of_registration`
- `jurisdiction`
- `entity_type`
- `hq_street`
- `hq_city`
- `hq_postal_code`
- `hq_country`
- `LEI`
- `DUNS`
- `CUSIP`
- `ISIN`
- `SEDOL`
- `BIC_SWIFT`
- `ticker`
- `exchange_mic`
- `primary_ric`
- `rating_fitch`
- `rating_moodys`
- `rating_sp`
- `primary_regulator`
- `regulator_ids_json`
- `ultimate_parent_id`
- `ultimate_parent_name`
- `coverage_status`
- `quality_flags_json`
- `canonical_confidence`
- `canonical_version`
- `last_reconciled_at`

### Evidence and disagreement view

Purpose: audit, review, lineage, legal discovery, model debugging, and agent confidence accounting.

Columns:

- `canonical_entity_id`
- `attribute_name`
- `canonical_value`
- `source_system`
- `source_primary_key`
- `source_value`
- `normalized_source_value`
- `decision = accepted | rejected | pending | conflict`
- `reason_code`
- `policy_rule_id`
- `confidence`
- `evidence_uri`
- `transaction_time`

### Agent reasoning view

Purpose: agent-plane consumption without forcing agents to drink the entire graph firehose.

Payload:

```json
{
  "canonical_entity_id": "cle_tesco_plc",
  "entity_type": "LegalEntity",
  "canonical_claims": {
    "legal_name": "Tesco plc",
    "country_of_registration": "GB",
    "ticker": "TSCO",
    "exchange_mic": "XLON"
  },
  "confidence": 0.93,
  "open_conflicts": [
    {
      "attribute": "ticker",
      "accepted": "TSCO",
      "rejected": "TSC",
      "reason": "exchange_confirmed_symbol_preferred"
    }
  ],
  "evidence_refs": [
    "SER:ReferenceData:C1055",
    "SER:CRM:C1055598"
  ]
}
```

### Feature-store view

Purpose: entity resolution model training, model monitoring, drift detection, and data-quality scoring.

Features:

- `name_similarity_max`
- `name_similarity_mean`
- `address_similarity_max`
- `postal_code_exact_count`
- `url_domain_match_count`
- `identifier_overlap_count`
- `checksum_valid_identifier_count`
- `source_count`
- `conflict_count`
- `accepted_claim_count`
- `rejected_claim_count`
- `authority_coverage_count`
- `dq_score`
- `canonical_confidence`

## Minimal file layout for Regis

```text
schema/hypergraph/core.yaml
schema/hypergraph/legal-entity.yaml
schema/hypergraph/authority.yaml
policy/concordance/merge-rules.yaml
policy/concordance/identifier-integrity.yaml
policy/concordance/address-normalization.yaml
exports/sql/canonical-legal-entity-view.sql
exports/sql/entity-evidence-disagreement-view.sql
exports/jsonld/legal-entity.context.jsonld
examples/tesco-concordance-example.json
```

## Acceptance criteria

- Raw source claims are never overwritten by canonical values.
- Canonical values are always traceable to source claims and policy decisions.
- Conflicts are represented explicitly.
- Downstream exports are stable contracts, not ad hoc query goblinry.
- Bitemporal reconstruction is possible for regulatory, analytical, and agentic reasoning use cases.
- Agents can consume bounded views that expose confidence, evidence, and open conflicts without requiring direct write access to the canonical graph.

## Integration notes

Regis should own the entity-identity and concordance semantics. Adjacent platform components should consume views, events, or typed contracts rather than reimplementing identity resolution locally. Agent-plane integrations should treat Regis as the authority for entity identity, attribute confidence, merge/split decisions, and evidence lineage.