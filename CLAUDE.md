# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository type

This is a **Hugging Face dataset repository**, not a software project. There is no build system, test runner, or lint tooling. "Code" here means dataset examples (JSONL/Parquet) plus three governance documents: `README.md` (the HF dataset card), `schema.json`, and `taxonomy.yaml`. Changes are almost always to data, metadata, or those three files.

The dataset is **SecureCode Web**: 1,378 web/application-security training examples (OWASP Top 10 2021). It is the web-only sibling of `scthornton/securecode` (combined) and `scthornton/securecode-aiml` (AI/ML only). Do not re-introduce AI/ML examples here — they were deliberately removed (see recent commits `17acc7f`, `391f661`, `6f9cb38`).

## Commonly used commands

```bash
# Count examples across all JSONL files (each line = one example in baseline; whole file = one pretty-printed example in framework files — see "Two JSONL formats" below)
find data -name "*.jsonl" -not -path "*/_archived_duplicates/*" | xargs wc -l

# Validate a single example against the schema
python -c "import json, jsonschema; jsonschema.validate(json.load(open('data/express_js-injection-000001.jsonl')), json.load(open('schema.json')))"

# Inspect the parquet splits
python -c "from datasets import load_dataset; d = load_dataset('parquet', data_files={'train':'data/train-00000-of-00001.parquet','validation':'data/validation-00000-of-00001.parquet','test':'data/test-00000-of-00001.parquet'}); print(d)"
```

Parquet files are git-LFS tracked (see `.gitattributes`). They are the canonical distribution artifact and must stay in sync with the JSONL sources — if you add/remove/edit examples, the parquet splits need to be rebuilt. The recent commits (`17acc7f`, `391f661`, `6f9cb38`) are the pattern for rebuilding train/validation/test splits.

Split sizes are fixed at **1102 / 138 / 138** (train / validation / test, totaling 1378) and are declared in the `README.md` YAML frontmatter (`dataset_info.splits`). If the split sizes change, update the frontmatter and the stats tables in the README body in the same commit.

## Dataset architecture

### Example structure (the "big picture")

Every example is a single JSON object validated by `schema.json`. The required top-level keys are `id`, `metadata`, `conversations`, `validation`; `context` is strongly encouraged. The non-negotiable shape:

- **`id`**: `^[a-z0-9-]+-\d{6}$` — baseline IDs use vuln-class prefixes (e.g. `sql-injection-000001`); framework IDs use `<framework>-<subcategory>-<NNNNNN>` (e.g. `express_js-injection-000001`).
- **`conversations`**: exactly **4 turns** in human/assistant/human/assistant order. This is the core contract of the dataset — enforced by `CONTRIBUTING.md`, not by `schema.json` (the schema only requires `minItems: 2`). Never produce 3-turn or 5-turn examples.
  - Turn 1: developer asks for functionality
  - Turn 2: assistant delivers **vulnerable + secure** implementations with attack demo
  - Turn 3: developer escalates (scale, performance, advanced scenario)
  - Turn 4: assistant delivers defense-in-depth (SIEM, logging, detection, infra hardening)
- **`metadata.owasp_2021`**: must match `^A\d{2}:2021-.+` (e.g. `A02:2021-Cryptographic Failures`). The string `"Modern Threats"` is permitted by the schema but should not be used for new web examples — AI/ML content lives in the sibling dataset.
- **`metadata.category`**: snake_case enum from `schema.json` (`broken_access_control`, `cryptographic_failures`, `injection`, …). Do not invent new categories without updating the schema.
- **`metadata.cwe`**: `^CWE-\d+$`.
- **`context.cve`**: `^CVE-\d{4}-\d+$` or `null`. `CONTRIBUTING.md` also allows the literal string `"N/A"`, but `schema.json` currently only accepts `string|null`. Prefer `null` to stay schema-valid.
- **`context.year`**: schema caps at 2025 even though today's date is later. If you add a 2026 incident, bump the schema's `maximum` in the same commit.

### Two JSONL formats (important gotcha)

Files in `data/` come in two physical shapes despite both ending in `.jsonl`:

1. **Baseline batches** (`*_batch_NNN.jsonl`, e.g. `authentication_batch_016.jsonl`) — true JSONL: ~10 one-line JSON objects per file, one example per line.
2. **Framework additions** (`<framework>-<subcat>-NNNNNN.jsonl`, e.g. `express_js-injection-000001.jsonl`) — one pretty-printed JSON object spanning ~130 lines. The whole file is one example.

Any loader/validator that walks `data/*.jsonl` must handle both: try line-by-line first, fall back to parsing the whole file as a single object. The README's "Load All Examples" snippet assumes line-by-line only and would miss the 219 framework examples — fix this when using it programmatically.

Rebuilding parquet splits: iterate both formats, combine, then write the 1102/138/138 split.

### Taxonomy and target counts

`taxonomy.yaml` declares target example counts per OWASP category and per subcategory (e.g. `broken_access_control.target_examples: 150`, `idor: 30`). These are aspirational targets from the original design, not current reality — the README's "Vulnerability Coverage" table reflects actual counts. When adding examples, prefer underrepresented categories per the README stats (not the taxonomy targets).

### Archived duplicates

`data/_archived_duplicates/` holds historical/backup copies (e.g. `command_injection_batch_007_backup.jsonl`). Exclude this directory from counts, validation, and parquet rebuilds. Do not delete — it is intentional historical provenance.

### `batch_007_corrections` files

`data/batch_007_corrections.jsonl` and its companion `.md`/`.txt` docs are a one-off corrections record. Treat as read-only history; don't fold them into normal batch processing without checking whether their contents are already applied upstream.

## Editing conventions specific to this repo

- When changing example counts, dataset identity, or split sizes, update **both** the README YAML frontmatter and the human-readable stats tables in the README body, in the same commit. Recent commit `8bd3d60` shows the pattern for identity renames (SecureCode v2 → SecureCode Web).
- Framework-specific examples should use the framework's **idiomatic** security primitives (Django ORM, Spring Security filters, Express middleware, etc.) — not generic language-level patterns. That's the whole point of the framework subset.
- Every example must tie to a real-world incident or CVE in `context.real_world_incident` / `context.cve`. Composite scenarios are allowed when no single CVE fits, but the impact must still be grounded. No hypothetical "imagine an attacker…" framing.
- Severity defaults: when in doubt between HIGH and CRITICAL, pick **HIGH** and justify in `context.business_impact` (per `CONTRIBUTING.md`).
