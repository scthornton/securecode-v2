# Phase 1 Progress — v2.1 Metadata Enrichment

## Status
- **Phase**: 1 (v2.1 metadata enrichment) — **SHIPPED 2026-04-25**
- **Branch**: `phase-1-metadata` (merged to main and tagged)
- **Started**: 2026-04-25
- **Shipped**: 2026-04-25
- **Current task**: Phase 1 complete
- **% complete**: 100%
- **Cloud budget**: $0 (Phase 1 used only free APIs)
- **Opus review budget**: ~$0 used (Scott was checkpoint reviewer; Opus assistance minimal in Phase 1 since work was deterministic/automated)
- **NVD API key**: ✓ activated and stored in shell rc files

## Completed
- **2026-04-25** Phase 1 kickoff — branch, planning docs, OWASP 2025 verified.
- **2026-04-25** Task 1.1 OWASP 2021→2025 non-breaking migration (commit `03345af`).
  - 1,378 examples migrated to dual-field taxonomy.
  - 5 pre-approved data corrections applied.
  - Migration script committed at `scripts/migrate_owasp_2025.py`.
- **2026-04-25** Task 1.2 metadata enrichment Pass 1 (commit `58dccec`).
  - EPSS, CVSS v3/v4, ATT&CK, CAPEC, preconditions enriched on 1,137 CVE-backed examples.
  - Confidence + source markers per ROADMAP §11.4.
  - Reproducibility manifest in `metadata.provenance`.
  - Script: `scripts/enrich_metadata.py`.
- **2026-04-25** Task 1.2 Pass 2 composite-heuristic enrichment (commit `05f1d03`).
  - 241 composite examples got severity-bucket EPSS + category-heuristic preconditions.
  - All marked `confidence: approximated`.
  - 10% spot-check sample passed.
  - Script: `scripts/enrich_composites.py`.
- **2026-04-25** Schema update + JSONL data quality fixes (commit `4f5ef8e`).
  - schema.json now v2.1 with all enrichment fields, relaxed enums to match data.
  - Pre-existing data issues fixed: missing complexity/validated/created, lowercase severity, non-standard validation values, ID format issue, type-inconsistent fields normalized.
  - 100% (1,378/1,378) schema validation pass.
- **2026-04-25** Parquet rebuild with explicit HF Features (commit `62edda0`).
  - Solved cross-row schema heterogeneity by declaring explicit `V21_FEATURES`.
  - Train: 1,102 rows / 21.6 MB. Validation: 138 / 2.9 MB. Test: 138 / 3.0 MB.
  - All enrichment queryable from HF UI.
  - Script: `scripts/rebuild_parquet.py`.
- **2026-04-25** README + CHANGELOG (commit `8f786a6`).
  - README hero "What's new in v2.1" with fill-rate table.
  - dataset_info YAML reflects full v2.1 schema.
  - Vulnerability-coverage table shows both 2021 and 2025 mappings with computed counts.
  - CHANGELOG.md created with full v2.1 release notes.

## In progress
- (Task #26 — GitHub PR draft prep)

## Upcoming
- **Task #26 — GitHub PR + HF release v2.1.0**:
  - Push `phase-1-metadata` branch to GitHub remote — **requires Scott approval**.
  - Open PR titled "Phase 1: v2.1 metadata enrichment + OWASP 2025 dual-field migration".
  - Scott reviews and merges.
  - After merge: push to HF as `v2.1.0` directly to main (per release policy: v2.1 is backward-compatible, straight-to-main flow). **Also requires Scott approval.**

## Decisions made this phase
- **2026-04-25** OWASP Top 10:2025 verified published; three label corrections vs upstream migration script applied.
- **2026-04-25** AI/ML files (5 files, 50 examples) moved to `_archived_duplicates/ai_ml_removed/` (Scott approved option B).
- **2026-04-25** Non-breaking migration: keep `owasp_2021` (corrected) + add `owasp_2025`. No `_legacy` suffix needed since 2021 field is preserved.
- **2026-04-25** 5 pre-existing data quality issues fixed during Task 1.1 (Scott approved).
- **2026-04-25** Composite heuristic enrichment (Option B, ~3 hr) chosen over fully-manual ~28 hr (Scott approved).
- **2026-04-25** SSTI conversation truncation: 6 examples in JSONL had truncated turn-2 content vs full content in v2.0 parquet. Restored from parquet.
- **2026-04-25** Quality-first directive (Scott): no shortcuts, must-have-upgrade bar. Drove the explicit Features schema decision over JSON-string fallback.
- **2026-04-25** Explicit `V21_FEATURES` schema with type projection — proper Arrow handling vs the JSON-string fallback. Resolved struct-vs-non-struct blocker.

## Open questions / blockers
- **None blocking.** Phase 1 work content-complete. Next is GitHub push + Scott approval.

## Phase 1 deliverables summary
- 1,378 examples enriched with deployment-grade exploitability metadata
- Schema v2.1 with non-breaking dual OWASP fields
- 90+ data quality fixes recorded with per-example provenance
- 4 new automation scripts: migrate, enrich, composite-enrich, rebuild-parquet
- Updated README + new CHANGELOG
- Backups of pre-v2.1 state in `backups/` (gitignored)

## Phase 1 metrics
- **Cloud spend**: $0 (free APIs only — FIRST.org EPSS, NVD CVSS, MITRE catalog)
- **Opus review tokens**: ~$0 (Scott reviewed in main session; no separate Opus session needed for Phase 1's deterministic work)
- **Total time**: ~5 hours of Claude session work compressed into one session (vs. ~75 hr part-time estimate)
- **Files modified**: ~344 JSONL + 3 parquet + schema.json + README + CHANGELOG + 4 scripts + progress doc
- **Commits on phase-1-metadata branch**: 7 (excluding initial plan commit)

## Next checkpoint target
- (none — Phase 1 closed)

## Phase 1 release record (2026-04-25)
- **GitHub**: PR #3 squash-merged to main as commit `7adb660`. PR URL: https://github.com/scthornton/securecode-web/pull/3
- **Hugging Face**: pushed `phase-1-metadata` → `main` (commit `90d3275`). Tagged as `v2.1.0` (tag commit `2036fcd`). Verified live via `load_dataset(..., revision="v2.1.0")` returning enriched data.
- **GitHub tag push**: rejected by secret scanner (ancestor commits contain pre-existing fake test keys); not blocking since HF is the user-facing release. Tag exists locally and on HF.
