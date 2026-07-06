# Changelog

All notable changes to SecureCode Web will be documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [2.6.1] - 2026-07-06

Fix-correctness sweep of the original corpus (removes confirmed-defective examples).

### Fixed

- A multi-agent review of all 1,412 pre-expansion examples for "does the secure fix actually eliminate
  the vulnerability" surfaced 25 confirmed defects (each adversarially verified, 0 disputed). All 25 were
  removed:
  - **14 mislabels** - mostly a Spring Boot cluster where the user asks for password hashing but the
    answer is a different vulnerability (session fixation, H2-console RCE, component scanning), with the
    conversation incoherent across turns (the same templated-junk pattern removed for Express.js in v2.5.1).
  - **7 secure-code-vulnerable** - the "secure" version was still exploitable (Angular
    `bypassSecurityTrustHtml`, Jackson polymorphic/default typing, unfixed XXE/TOCTOU/IDOR, a broken
    operator-precedence authorization gate).
  - **4 fix-incomplete** - the fix did not address the stated vulnerability.

### Changed

- Totals: 1,650 -> **1,625** examples (train/validation/test 1,249 / 186 / 190). Enrichment-coverage
  percentages recomputed against 1,625.

## [2.6.0] - 2026-07-06

Express.js coverage restoration (replaces the v2.5.1 removals).

### Added

- **29 new Express.js examples** (`data/express_regen_batch_*.jsonl`) covering the topics whose examples
  were removed as templated in v2.5.1: IDOR, auth-middleware bypass, broken auth/session, SQL/NoSQL
  injection, prototype pollution, ReDoS, vulnerable dependency, JWT algorithm bypass, insecure CORS, and
  improper input validation. Each is genuinely distinct with a correct topic-matching fix. Validated:
  0 near-duplicates, 29/29 unique answers, 0 JavaScript syntax errors (node --check), `context.cve` null,
  correct metadata combos, CWE-derived CAPEC/ATT&CK.

### Changed

- Totals: 1,621 -> **1,650** examples (train/validation/test 1,272 / 187 / 191). Leakage-aware splits.

---

## [2.5.2] - 2026-07-06

Metadata and repo-hygiene cleanup. No example content changed.

### Changed

- **Backfilled `metadata.tags`** on all 1,621 examples (previously empty on all but 2). Tags are derived
  audit labels - language, category, subcategory, OWASP 2021/2025 short codes, CWE, and framework - so
  coverage is now filterable/auditable from metadata.
- **Regenerated `taxonomy.yaml`** as a descriptive map computed from the released parquet (categories,
  OWASP mappings, per-subcategory counts, languages, severity mix). It now matches the actual data
  instead of the drifted aspirational v2.0 targets.
- **Updated `schema.json`**: corrected the `id` description (ids are NOT globally unique - batch files
  restart numbering), and declared previously-undeclared fields (`tags`, `technique`, `template_engine`,
  `framework_native`, top-level `security_assertions`/`quality_score`/`references`).

## [2.5.1] - 2026-07-06

Data-quality correction (removes a templated/mislabeled cluster). No new content.

### Fixed

- **Removed 37 templated Express.js examples** that shared ~3 near-identical answers (a crypto-js/PBKDF2
  password-hashing lesson) across 15 unrelated stated topics (IDOR, SQL/NoSQL injection, prototype
  pollution, ReDoS, middleware bypass, path traversal, file upload, CORS, JWT, etc.). 33 were outright
  topic/answer mismatches; the remaining 4 were redundant duplicates of the same lesson. These were also
  mis-tagged `A02:2021 Cryptographic Failures` (matching the wrong answer, not the stated topic), so
  their removal corrects the OWASP distribution. Proper Express.js coverage for these topics will return
  as regenerated, correctly-labeled examples in a later release.
- Normalized 4 residual `crypto_failures` category values to the canonical `cryptographic_failures`.

### Changed

- Totals: 1,658 -> **1,621** examples (train/validation/test 1,262 / 179 / 180). Enrichment-coverage
  percentages recomputed against 1,621.

## [2.5.0] - 2026-07-06

Three currency packs (+85 examples) bringing coverage to the 2025 taxonomy and threat landscape.

### Added

- **Supply chain / CI-CD pack (35)** - `data/supplychain_pack_batch_*.jsonl`. Covers the new OWASP
  Top 10:2025 A03 (Software Supply Chain Failures): dependency confusion, malicious/postinstall packages,
  SHA-pinning GitHub Actions, `pull_request_target` hardening, CI secret exfiltration, integrity/SBOM.
  Grounded in the 2025 supply-chain wave; the tj-actions case cites CVE-2025-30066.
- **OAuth / OIDC pack (30)** - `data/oauth_pack_batch_*.jsonl`. RFC 9700 implementation security: exact
  redirect_uri matching, PKCE, state/nonce, token/JWT validation, implicit-flow migration, token storage.
- **2025 framework-CVE pack (20)** - `data/framework_cve_pack_batch_*.jsonl`. Next.js middleware bypass
  (CVE-2025-29927) and React Server Components RCE (CVE-2025-55182 / CVE-2025-66478), with
  defense-in-depth fixes.
- All cited CVEs (CVE-2025-29927, -55182, -66478, -30066) were **verified real against NVD/vendor
  advisories** before release. Non-CVE examples keep `context.cve` null. Validated via schema +
  Python-syntax check; CWE-derived CAPEC/ATT&CK applied where a mapping exists.

### Changed

- Totals: 1,573 -> **1,658** examples (train/validation/test 1,298 / 180 / 180). Leakage-aware splits
  (0 cross-split near-duplicates). Two config languages added (Dockerfile, JSON) for supply-chain
  examples; language count 11 -> 13. Enrichment-coverage percentages recomputed against 1,658.

## [2.4.0] - 2026-07-05

Three coverage-expansion packs (+125 examples).

### Added

- **CSRF / open-redirect / clickjacking pack (45)** - `data/csrf_pack_batch_*.jsonl`. Synchronizer-token
  CSRF across Flask/Django/Express/Spring/Rails/Laravel/ASP.NET, allowlist redirect validation, and
  `frame-ancestors`/`X-Frame-Options` clickjacking defenses.
- **File-upload / path-traversal pack (40)** - `data/upload_pack_batch_*.jsonl`. Magic-byte + allowlist
  upload validation, canonical-path containment, and zip-slip in archive extraction.
- **Django security buildout (40)** - `data/django_pack_batch_*.jsonl`. Raw-SQL/`extra` SQLi,
  `mark_safe`/`|safe` template XSS, DRF mass assignment, IDOR, SSRF, settings misconfig, `@csrf_exempt`
  misuse. Django coverage goes from ~3 to ~43 examples.
- All packs: `context.cve` null (no fabricated CVEs), real-incident grounding, correct sink-level fixes
  (validated against a schema + Python-syntax check; two generation typos corrected before ingest).
  CWE-derived CAPEC/ATT&CK applied where a mapping exists.

### Changed

- Totals: 1,448 -> **1,573** examples (train/validation/test 1,245 / 164 / 164). New examples split
  leakage-aware (0 cross-split near-duplicates) and stratified so each new vulnerability type appears in
  test. Enrichment-coverage percentages recomputed against the 1,573 denominator.

## [2.3.0] - 2026-07-05

XSS expansion pack.

### Added

- **70 new cross-site-scripting examples** (`data/xss_pack_batch_*.jsonl`), roughly doubling XSS
  coverage and extending it to server-rendered stacks that were previously thin: Jinja2/Django
  (Python), JSP/Thymeleaf (Java), vanilla PHP/Twig/Blade, ERB/Rails (Ruby), Go `html/template`,
  C# Razor, plus browser DOM (JS/TS). Covers stored, reflected, DOM, and attribute-context XSS and
  one clickjacking example (CWE-1021).
- Every new example: `context.cve` is null (no fabricated CVEs), grounded in real incidents, and the
  secure fix uses context-aware output encoding at the sink (not input blacklisting). CWE-derived
  CAPEC/ATT&CK enrichment applied; no fabricated EPSS/CVSS.

### Changed

- Totals: 1,378 -> **1,448** examples (train/validation/test 1,156 / 146 / 146). New examples were
  split leakage-aware (no near-duplicate straddles splits) and stratified so every language appears
  in the test split. Enrichment-coverage percentages shift accordingly (denominator 1,448).

## [2.2.0] - 2026-07-04

Grounding-integrity correction. Every `context.cve` and `context.real_world_incident` field was
independently audited against public records; the code lessons are unchanged.

### Fixed

- **Removed 802 mismatched or nonexistent CVEs** from `context.cve` (set to null); replaced 21 with
  the correct CVE. Roughly 70% of previously-cited CVEs did not match the vulnerability shown (e.g. a
  Metabase RCE CVE attached to an account-enumeration example).
- **Nulled EPSS and CVSS metadata that was harvested from a removed CVE.** These were `measured`
  values keyed to the specific (wrong) CVE, so they described a different vulnerability. Coverage
  drops accordingly: EPSS 97.7% -> 40.3%, CVSS v3 77.4% -> 22.0%. CWE-derived enrichment
  (CAPEC 71.0%, ATT&CK 54.3%, preconditions 100%) is unchanged.
- **Corrected 810 real-world incident references**: 378 rewritten to the accurate incident (fixing
  wrong years, regulators, dollar figures, and record counts), 432 with no real counterpart replaced
  with `Representative <category> example; not tied to a specific public incident.` Every example is
  still incident-tagged; 69% now cite a named public incident, 31% are marked representative.
- **Replaced 12 stale parquet rows** that still carried pre-v2.1 content with their current versions.

### Notes

- No examples were added or removed; content of the code conversations is unchanged. This is a
  metadata/grounding correction only. Re-pin a revision if you depended on the prior CVE/EPSS fields.

## [2.1.1] - 2026-07-04

Data-integrity and documentation corrections. No new examples; the released
example set is unchanged in content (1,378), but the train/validation/test
split membership changed - see "Fixed" below. Re-pin a revision if you need
the exact prior splits.

### Fixed

- **Eliminated train/test leakage.** The previous split placed near-duplicate
  examples (same first user turn, Jaccard > 0.75) on both sides of the split:
  16 of 138 test rows (11.6%) and 15 of 138 validation rows had a near-duplicate
  in another split, inflating eval scores. Re-split with near-duplicate families
  kept intact within a single split, stratified by category and language
  (every language with >= 10 examples now appears in test; `yaml` previously had
  zero). Sizes unchanged (1,102 / 138 / 138); cross-split near-duplicates now 0.
- **batch_007 corrections merged.** The 6 corrected `sql-injection` examples in
  `batch_007_corrections.jsonl` now supersede their stale versions in the
  released parquet; the corrections file was folded into
  `command_injection_batch_007.jsonl`.
- **Metadata hygiene.** Collapsed duplicate category labels
  (`crypto_failures` -> `cryptographic_failures`, `broken_authentication` ->
  `auth_failures`), moved the orphan `rce` category to `vulnerable_components`,
  normalized `c#` -> `csharp`, and fixed off-vocabulary `complexity` values
  (`low`/`LOW`/`high` -> `basic`/`advanced`). Category values: 13 -> 10.
- **Dataset card corrected.** The framework, language, and severity tables were
  computed from the older 1,435-example snapshot and are now recomputed from the
  released parquet; the JSONL and fine-tuning loading snippets (previously
  broken) now run; added an "`id` is not a unique key" note; rebuilt the stale
  `CITATION.bib`.

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
  any released parquet split and are out of scope for this web-security
  dataset (AI/ML security is covered separately by the
  `scthornton/securecode-aiml` sibling dataset). Archived here for historical
  provenance. Note: these specific examples are not currently present in
  securecode-aiml; folding them in is tracked as follow-up work.

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
