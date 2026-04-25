# Changelog

All notable changes to SecureCode Web will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [2.1.0] — 2026-04-25

Deployment-grade exploitability metadata. Non-breaking — every existing
`metadata.owasp_2021` and other v2.0 field is preserved. New fields are
optional, paired with `*_source` and `*_confidence` markers per ROADMAP §11.4.

### Added

- **OWASP Top 10:2025 dual-field migration.** `metadata.owasp_2025` added
  alongside the existing `metadata.owasp_2021`. Both populated for all 1,378
  examples. Non-breaking — existing pipelines querying `owasp_2021` keep
  working. SSRF (A10:2021) folds into A01:2025 Broken Access Control per the
  official 2025 taxonomy. A10:2025 "Mishandling of Exceptional Conditions"
  is a new category in 2025; current dataset has 0 examples mapped to it
  (documented gap, addressed in v2.5+).
- **EPSS exploit-probability scores.** `metadata.epss_score` and
  `metadata.epss_percentile` from FIRST.org EPSS API. 1,105 examples
  measured directly (CVE-backed); 241 composite examples have severity-bucket
  approximations marked `epss_confidence: approximated`. 97.7% total coverage.
- **CVSS v3.1 vectors.** `metadata.cvss_v3_vector` from NVD API. 1,067
  examples (77.4%).
- **CVSS v4.0 vectors.** `metadata.cvss_v4_vector` from NVD where
  published. 28 examples (2.0% — most CVEs not yet rated v4).
- **MITRE ATT&CK technique mapping.** `metadata.attack_techniques` (heuristic
  from CWE via curated table). 748 examples (54.3%).
- **MITRE CAPEC IDs.** `metadata.capec_ids` derived from CWE via the official
  MITRE CWE catalog (`cwe-2000.csv`). 979 examples (71.0%).
- **Explicit preconditions.** `metadata.preconditions` with `auth_required`,
  `network_position`, `user_interaction`, `prior_access`. Derived from CVSS
  vectors where available, from category/business_impact heuristics for
  composite examples. 1,308 populated (94.9%).
- **Provenance audit trail.** `metadata.provenance` records migration date,
  enrichment date, version, and any data corrections applied per example.
- **Confidence + source markers** on every derived field
  (`*_source`, `*_confidence`) so downstream tools can distinguish measured
  vs. heuristic vs. approximated.
- `scripts/migrate_owasp_2025.py` — non-breaking OWASP migration with
  pre-approved data corrections.
- `scripts/enrich_metadata.py` — Pass 1 enrichment for CVE-backed examples
  (FIRST.org + NVD + MITRE).
- `scripts/enrich_composites.py` — Pass 2 heuristic enrichment for the 241
  composite examples without CVEs.
- `scripts/rebuild_parquet.py` — explicit HF Features schema preserves all
  v2.0 fields and adds v2.1 enrichment cleanly.
- `schema.json` updated to v2.1 with all new optional fields and enum/pattern
  relaxations to match observed data.

### Changed

- **5 SSTI examples** had truncated conversations in JSONL — restored from
  v2.0 parquet content (the parquet had the full release content; the JSONL
  had been corrupted at some point pre-v2.1). Marked in
  `metadata.provenance.v21_conversations_restored_from_v20_parquet: true`.
- README now ships a `## What's new in v2.1` hero section, dataset_info
  YAML reflects the full v2.1 schema, vulnerability-coverage table shows
  both 2021 and 2025 mappings, and example loading code uses the new
  fields.

### Fixed

These were pre-existing data-quality issues in v2.0; surfaced and fixed
during the v2.1 migration with Scott's approval. Each is recorded in
`metadata.provenance.owasp_data_corrections` per affected example.

- 60 SQL examples in `sql_batch_201.jsonl` had `owasp_2021: "Unknown"` and
  `cwe: "CWE-000"`. Triaged to `A03:2021-Injection` and `CWE-89` (they're
  all SQL injection per their `category`/`subcategory`).
- 10 `express_js-injection-*` examples had truncated `owasp_2021: "A03"` —
  corrected to `A03:2021-Injection`.
- 2 SSRF examples had inconsistent `(SSRF)` suffix variants — normalized
  to canonical `A10:2021-Server-Side Request Forgery`.
- 8 examples missing `metadata.complexity` → set to `"moderate"`.
- 6 examples missing `metadata.validated` → set to `true`.
- 4 examples missing `metadata.created` → set placeholder.
- 10 examples with lowercase severity (`critical`, `high`) → uppercased.
- 5 examples with `validation.security_review: "comprehensive"` → `"passed"`.
- 4 examples with non-standard `validation.code_execution` values
  (`validated`, `tested`, `not_applicable`) → normalized.
- 1 example with truncated ID (`design_flaws-008`) → expanded to 6-digit
  format (`design_flaws-000008`).
- 1 example with `validation.duplication_check: "unique"` → `"passed"`.
- 1 example with non-standard `validation.encoding_check` → normalized.
- Type normalizations for parquet schema strictness:
  - 1,376 examples: `metadata.tags` `null` → `[]`
  - 9 examples: `context.affected_versions` list → comma-joined string
  - 1 example: `context.references[].cvss_score` string → float
  - 3 examples: top-level `security_assertions` list → dict

### Moved

- 50 AI/ML examples in `data/ai_security_batch_103-107.jsonl` moved to
  `data/_archived_duplicates/ai_ml_removed/`. These were never included in
  any released parquet split (their content lives in the
  `scthornton/securecode-aiml` sibling dataset), but their JSONL source
  files lagged. Now archived for historical provenance.

### Removed

- `data/sql_advanced_batch_010.jsonl` (was a 0-byte phantom file).

### Schema

`schema.json` updated to JSON Schema draft-07 v2.1 with all new fields as
optional. Several enum/pattern relaxations for compatibility with observed
data (lang accepts `csharp` and `yaml` and `hcl`; complexity is now a
free string; id pattern allows underscores; `cve` allows empty string;
`year` widened to 2010–2027; `validation.code_execution` adds
`drift_detected`).

---

## [2.0.x] — 2025

Initial public releases. See [previous CITATION.bib](CITATION.bib) and
[paper](https://huggingface.co/papers/2512.18542) for v2.0 details:

- 1,378 examples (1,159 baseline + 219 framework additions)
- 4-turn conversational structure
- 100% incident grounding
- 12 programming languages
- OWASP Top 10:2021 coverage (10 categories)
- Train/validation/test splits 1102/138/138
