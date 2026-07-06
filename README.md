---
language:
- en
license: cc-by-nc-sa-4.0
size_categories:
- 1K<n<10K
task_categories:
- text-generation
- question-answering
pretty_name: SecureCode Web
tags:
- security
- owasp
- owasp-2025
- cve
- epss
- mitre-attack
- mitre-capec
- cvss
- secure-coding
- vulnerability-detection
- cybersecurity
- code-security
- web-security
- siem
- penetration-testing
- incident-grounding
- defense-in-depth
- framework-security
- exploit-prediction
arxiv: 2512.18542
dataset_info:
  features:
  - name: id
    dtype: string
  - name: metadata
    struct:
    - name: category
      dtype: string
    - name: complexity
      dtype: string
    - name: created
      dtype: string
    - name: cwe
      dtype: string
    - name: lang
      dtype: string
    - name: owasp_2021
      dtype: string
    - name: severity
      dtype: string
    - name: subcategory
      dtype: string
    - name: tags
      list: string
    - name: technique
      dtype: string
    - name: template_engine
      dtype: string
    - name: validated
      dtype: bool
    - name: owasp_2025
      dtype: string
    - name: epss_score
      dtype: float64
    - name: epss_percentile
      dtype: float64
    - name: epss_date
      dtype: string
    - name: epss_source
      dtype: string
    - name: epss_confidence
      dtype: string
    - name: cvss_v3_vector
      dtype: string
    - name: cvss_v3_source
      dtype: string
    - name: cvss_v3_confidence
      dtype: string
    - name: cvss_v4_vector
      dtype: string
    - name: cvss_v4_source
      dtype: string
    - name: cvss_v4_confidence
      dtype: string
    - name: attack_techniques
      list: string
    - name: attack_techniques_source
      dtype: string
    - name: attack_techniques_confidence
      dtype: string
    - name: capec_ids
      list: string
    - name: capec_ids_source
      dtype: string
    - name: capec_ids_confidence
      dtype: string
    - name: preconditions
      struct:
      - name: auth_required
        dtype: bool
      - name: network_position
        dtype: string
      - name: user_interaction
        dtype: string
      - name: prior_access
        dtype: string
    - name: preconditions_source
      dtype: string
    - name: preconditions_confidence
      dtype: string
    - name: preconditions_text_overrides
      list: string
    - name: provenance
      struct:
      - name: owasp_migration_date
        dtype: string
      - name: owasp_data_corrections
        list: string
      - name: enrichment_date
        dtype: string
      - name: enrichment_version
        dtype: string
      - name: composite_heuristic_date
        dtype: string
      - name: composite_heuristic_version
        dtype: string
      - name: v21_conversations_restored_from_v20_parquet
        dtype: bool
  - name: context
    struct:
    - name: affected_systems
      dtype: string
    - name: attack_vector
      dtype: string
    - name: business_impact
      dtype: string
    - name: cve
      dtype: string
    - name: impact
      dtype: string
    - name: real_world_incident
      dtype: string
    - name: year
      dtype: int64
  - name: conversations
    list:
    - name: from
      dtype: string
    - name: turn
      dtype: int64
    - name: value
      dtype: string
  - name: validation
    struct:
    - name: code_execution
      dtype: string
    - name: duplication_check
      dtype: string
    - name: encoding_check
      dtype: string
    - name: issues
      list: string
    - name: review_date
      dtype: string
    - name: reviewed_by
      dtype: string
    - name: security_review
      dtype: string
    - name: syntax_check
      dtype: string
  splits:
  - name: train
    num_examples: 1249
  - name: validation
    num_examples: 186
  - name: test
    num_examples: 190
configs:
- config_name: default
  data_files:
  - split: train
    path: data/train-00000-of-00001.parquet
  - split: validation
    path: data/validation-00000-of-00001.parquet
  - split: test
    path: data/test-00000-of-00001.parquet
---
<center>
SecureCode Web: Traditional Web & Application Security Dataset
</center>

<div align="center">

![Version](https://img.shields.io/badge/version-2.6.1-blueviolet.svg)
![License](https://img.shields.io/badge/license-CC%20BY--NC--SA%204.0-blue.svg)
![Examples](https://img.shields.io/badge/examples-1,625-green.svg)
![Languages](https://img.shields.io/badge/languages-13-orange.svg)
![Quality](https://img.shields.io/badge/quality-100%25_validated-brightgreen.svg)
![Incident Grounding](https://img.shields.io/badge/incident_grounding-100%25-blue.svg)
![EPSS](https://img.shields.io/badge/EPSS-34%25_coverage-blue.svg)
![OWASP](https://img.shields.io/badge/OWASP-2021%20%7C%202025-orange.svg)

**Production-grade web security vulnerability dataset with complete incident grounding, 4-turn conversational structure, and comprehensive operational guidance**

[Paper](https://huggingface.co/papers/2512.18542) | [GitHub](https://github.com/scthornton/securecode-web) | [Dataset](https://huggingface.co/datasets/scthornton/securecode-web) | [Model Collection](https://huggingface.co/collections/scthornton/securecode) | [Blog Post](https://huggingface.co/blog/scthornton/securecode-models)

</div>

---

## What's new in v2.6

v2.6 restores proper Express.js coverage for the topics whose examples were removed in v2.5.1 (they had
shared one reused answer). **29 new, genuinely distinct Express.js examples** - IDOR, auth-middleware
bypass, broken auth/session, SQL and NoSQL injection, prototype pollution, ReDoS, vulnerable dependency,
JWT algorithm bypass, insecure CORS, and input validation - each with a correct, topic-matching fix
(validated: 0 near-duplicates, 29/29 distinct answers, 0 JavaScript syntax errors, `cve` null). Totals
move to 1,650 examples (1,272 / 187 / 191).

## What's new in v2.5

v2.5 adds **85 examples across three currency packs** that bring the dataset up to the 2025 threat and
taxonomy landscape:

- **Software supply chain / CI-CD (35):** the brand-new **OWASP Top 10:2025 A03 - Software Supply Chain
  Failures**, previously uncovered. Dependency confusion, malicious/typosquatted packages, postinstall
  scripts, SHA-pinning of GitHub Actions, `pull_request_target` hardening, CI secret exfiltration, and
  integrity/SBOM verification - grounded in the real 2025 wave (npm chalk/debug, the Shai-Hulud worm,
  and the `tj-actions/changed-files` compromise, CVE-2025-30066).
- **OAuth 2.0 / OIDC (30):** implementation-level flaws per RFC 9700 - exact `redirect_uri` matching,
  mandatory PKCE, `state`/`nonce`, full token validation (signature/`iss`/`aud`/`alg`), implicit-flow
  migration, and secure token storage.
- **2025 framework CVEs (20):** the Next.js middleware authorization bypass (CVE-2025-29927) and the
  React Server Components deserialization RCE "React2Shell" (CVE-2025-55182 / CVE-2025-66478), taught
  with defense-in-depth fixes, not just "upgrade".

The CVE-citing examples reference **only verified real CVEs** (each confirmed against NVD/vendor advisories
before release) - the inverse of the v2.2 problem, showing the dataset grounds on real CVEs correctly.
Totals move to 1,658 examples (1,298 / 180 / 180); splits are leakage-aware.

## What's new in v2.4

v2.4 adds **125 examples across three coverage packs**, targeting the highest-frequency web gaps that
prior versions barely covered:

- **CSRF / open-redirect / clickjacking (45):** synchronizer-token CSRF (Flask-WTF, Django, Express,
  Spring, Rails, Laravel, ASP.NET antiforgery), allowlist-based redirect validation, and
  `frame-ancestors` / `X-Frame-Options` clickjacking defenses.
- **File-upload / path-traversal (40):** magic-byte + allowlist upload validation, canonical-path
  containment (`realpath` + `commonpath`, `filepath.Clean`, `GetFullPath` prefix checks), and zip-slip
  in archive extraction.
- **Django buildout (40):** ORM raw/`extra` SQLi, template `mark_safe`/`|safe` XSS, DRF mass assignment,
  object-level authz (IDOR), SSRF, `DEBUG`/`SECRET_KEY`/`ALLOWED_HOSTS` misconfig, and `@csrf_exempt`
  misuse - lifting Django from ~3 to ~43 examples.

Every pack follows the v2.2/v2.3 rules: `context.cve` null (no fabricated CVEs), real-incident grounding,
and each secure fix uses the correct defense at the sink (not input blacklisting). All examples passed a
schema + Python-syntax check; splits are leakage-aware. Totals move to 1,573 examples (1,245 / 164 / 164).

## What's new in v2.3

v2.3 adds a **70-example XSS expansion pack**, roughly doubling cross-site-scripting coverage (the most
under-represented high-frequency web vulnerability in prior versions) and broadening it well beyond
JavaScript. The pack covers **stored, reflected, DOM, and attribute-context XSS plus one clickjacking
example (CWE-1021)** across seven server-rendered stacks: Jinja2/Django (Python), JSP/Thymeleaf (Java),
vanilla PHP/Twig/Blade, ERB/Rails (Ruby), `html/template` (Go), Razor (C#), and browser DOM (JS/TS).

Every example follows the anti-fabrication rules learned from the v2.2 audit: **`context.cve` is null**
(app-level XSS rarely maps to a CVE), grounding uses real incidents (British Airways/Magecart, Samy, etc.),
and each secure fix uses **context-aware output encoding at the sink** (template auto-escaping,
`htmlspecialchars` with `ENT_QUOTES`, `textContent`, DOMPurify, `html/template`, `c:out`, `@Html`
encoding) rather than input blacklisting. Split membership is leakage-aware (no near-duplicate straddles
train/test). Totals move to 1,448 examples (1,156 / 146 / 146).

## What's new in v2.2

v2.2 is a **grounding-integrity correction**. An independent audit of every `context.cve` and
`context.real_world_incident` field found that a large share of the CVE and incident references were
mismatched or fabricated (for example, a Metabase RCE CVE cited on an account-enumeration example).
We corrected the grounding and, critically, **removed the EPSS/CVSS metadata that had been harvested
from those wrong CVEs** - those scores described a different vulnerability and were misleading.

- **802 mismatched/nonexistent CVEs removed** (`context.cve` set to null); 21 replaced with the correct CVE.
- **EPSS and CVSS vectors nulled** wherever they were derived from a removed CVE (they were all
  `measured` values keyed to that specific CVE, not heuristic estimates).
- **810 real-world incidents corrected**: 378 rewritten to the accurate incident, 432 that had no
  real counterpart replaced with an honest `Representative <category> example; not tied to a specific
  public incident.` line.
- CWE-derived enrichment (**CAPEC, ATT&CK, preconditions**) is unaffected - it never depended on the CVE.

The net effect is a smaller but **honest** exploitability layer. Coverage below reflects the corrected data.

| Field | Coverage (v2.2, corrected) | Source |
|---|---|---|
| **EPSS** (exploit-probability score + percentile) | 33.7% (547 / 1,625) | FIRST.org EPSS API, kept only where the CVE is verified |
| **CVSS v3.1 vector** | 18.3% (297 / 1,625) | NVD API, kept only where the CVE is verified |
| **CVSS v4.0 vector** | 0.2% (3 / 1,625) | NVD API where published |
| **Preconditions** (auth_required, network_position, user_interaction, prior_access) | 81.0% (1,316 / 1,625) | Parsed from CVSS or category-heuristic (CWE-based) |
| **MITRE CAPEC IDs** | 69.4% (1,128 / 1,625) | Derived from CWE via MITRE catalog |
| **MITRE ATT&CK techniques** | 55.0% (893 / 1,625) | Heuristic mapping from CWE |
| **OWASP Top 10:2025 dual-field** | 100% (1,625 / 1,625) | Migrated from 2021 with non-breaking dual fields |
| **Real-world incident** | 100% populated (69% named incident, 31% marked representative) | Audited and corrected in v2.2 |

Every derived field carries paired `*_source` and `*_confidence` markers so you can distinguish measured from heuristic-derived values. Confidence enum: `measured` | `heuristic` | `approximated` | `absent`.

## What's new in v2.1

v2.1 added **deployment-grade exploitability metadata** to every example (EPSS, CVSS, CAPEC, ATT&CK,
preconditions) alongside the OWASP 2021->2025 dual-field migration. The v2.2 audit above corrected the
CVE-derived parts of this layer; the coverage table under "What's new in v2.2" supersedes the original
v2.1 figures.

### Non-breaking migration

v2.1 is fully backward compatible. The existing `metadata.owasp_2021` field is preserved (and corrected — see below). New `metadata.owasp_2025` is added alongside. Existing pipelines querying `owasp_2021` keep working.

### Data-quality corrections in v2.1

While migrating, we fixed pre-existing issues in v2.0:

- 60 SQL examples across `sql_batch_201/208/212/216/219/221.jsonl` (10 each) had `owasp_2021: "Unknown"` and `cwe: "CWE-000"`, corrected to `A03:2021-Injection` and `CWE-89`
- 10 `express_js-injection-*` examples had truncated `owasp_2021: "A03"` — corrected to full label
- 2 SSRF examples had inconsistent `(SSRF)` suffix — normalized
- 6 SSTI examples had truncated conversations in JSONL (parquet had full content) — JSONL restored from parquet
- 50 AI/ML examples in `data/` (not in any release split) moved to `data/_archived_duplicates/ai_ml_removed/` (out of scope for this web-security dataset; AI/ML security is covered separately by `scthornton/securecode-aiml`)
- ~30 minor type/format normalizations for schema strictness

All corrections are recorded in `metadata.provenance.owasp_data_corrections` per affected example.

### Documented coverage gap

OWASP Top 10:2025 introduced **A10:2025 "Mishandling of Exceptional Conditions"** as a brand-new category. The current dataset has **0 examples** mapped to A10:2025 — this is a known gap that future releases (v2.5+) will address.

### Loading the enriched data

```python
from datasets import load_dataset
ds = load_dataset("scthornton/securecode-web")

# Filter by exploitability — high EPSS + internet-facing + no auth required
high_risk = ds["train"].filter(lambda ex:
    (ex["metadata"]["epss_percentile"] or 0) > 0.9
    and ex["metadata"]["preconditions"]["network_position"] == "internet"
    and ex["metadata"]["preconditions"]["auth_required"] is False
)

# Filter by MITRE ATT&CK technique
sql_injection_examples = ds["train"].filter(lambda ex:
    "T1190" in (ex["metadata"]["attack_techniques"] or [])
)
```

---

## SecureCode Dataset Family

This dataset is the **web & application security** component of the SecureCode family:

| Dataset | Examples | Focus | Link |
|---------|----------|-------|------|
| **SecureCode** | 2,185 | Unified dataset (web + AI/ML) with HF configs | [scthornton/securecode](https://huggingface.co/datasets/scthornton/securecode) |
| **SecureCode Web** | 1,625 | Traditional web & application security (OWASP Top 10 2021) | This dataset |
| **SecureCode AI/ML** | 750 | AI/ML system security (OWASP LLM Top 10 2025) | [scthornton/securecode-aiml](https://huggingface.co/datasets/scthornton/securecode-aiml) |

For the combined dataset with both web and AI/ML security examples, use [`scthornton/securecode`](https://huggingface.co/datasets/scthornton/securecode).

---

## Overview

SecureCode Web is a rigorously validated dataset of **1,625 web security-focused coding examples** designed to train security-aware AI code generation models. Every example is grounded in real-world security incidents (CVEs, breach reports), provides both vulnerable and secure implementations, demonstrates concrete attacks, and includes defense-in-depth operational guidance.

The dataset focuses exclusively on **traditional web and application security** (OWASP Top 10 2021) and includes the original **1,159 baseline examples** covering 11 programming languages, plus **219 framework-specific additions**, a **70-example XSS expansion pack**, **125 v2.4 coverage examples** (CSRF/open-redirect/clickjacking, file-upload/path-traversal, Django), and **85 v2.5 currency examples** (supply-chain/CI-CD, OAuth/OIDC, 2025 framework CVEs).

### Why SecureCode Web?

**The Problem:** AI coding assistants produce vulnerable code in 45% of security-relevant scenarios (Veracode 2025), introducing security flaws at scale.

**The Solution:** SecureCode Web provides production-grade training data with:

- **100% Incident Grounding** -- Every example ties to documented CVEs or security incidents
- **4-Turn Conversational Structure** -- Mirrors real developer-AI workflows
- **Complete Operational Guidance** -- SIEM integration, logging, monitoring, detection
- **Full Language Fidelity** -- Language-specific syntax, idioms, and frameworks
- **Rigorous Validation** -- 100% compliance with structural and security standards

---

## Trained Models

We've fine-tuned **8 security-aware code models** (3B to 20B parameters) using this dataset, all available in the [SecureCode Model Collection](https://huggingface.co/collections/scthornton/securecode):

| Model | Parameters | Base Model | Training Time | Key Features |
|-------|-----------|------------|---------------|--------------|
| [Llama 3.2 3B SecureCode](https://huggingface.co/scthornton/llama-3.2-3b-securecode) | 3B | Meta Llama 3.2 | 1h 5min | Smallest model, ideal for edge deployment |
| [Qwen Coder 7B SecureCode](https://huggingface.co/scthornton/qwen-coder-7b-securecode) | 7B | Qwen 2.5 Coder | 1h 24min | Balanced speed & accuracy |
| [CodeGemma 7B SecureCode](https://huggingface.co/scthornton/codegemma-7b-securecode) | 7B | Google CodeGemma | 1h 27min | Google-backed, enterprise trust |
| [DeepSeek Coder 6.7B SecureCode](https://huggingface.co/scthornton/deepseek-coder-6.7b-securecode) | 6.7B | DeepSeek Coder | 1h 15min | Strong multilingual code understanding |
| [CodeLlama 13B SecureCode](https://huggingface.co/scthornton/codellama-13b-securecode) | 13B | Meta CodeLlama | 1h 32min | Production workhorse |
| [Qwen Coder 14B SecureCode](https://huggingface.co/scthornton/qwen2.5-coder-14b-securecode) | 14B | Qwen 2.5 Coder | 1h 19min | Production balance (128K context) |
| [StarCoder2 15B SecureCode](https://huggingface.co/scthornton/starcoder2-15b-securecode) | 15B | StarCoder2 | 1h 40min | Open-source flagship |
| [Granite 20B SecureCode](https://huggingface.co/scthornton/granite-20b-code-securecode) | 20B | IBM Granite Code | 1h 19min | Enterprise flagship (IBM-grade trust) |

**Training Infrastructure:**
- Google Cloud Platform (GCP) A100 instances (2x A100 40GB)
- LoRA fine-tuning with 4-bit quantization (QLoRA)
- ~1-2 hours training time per model
- Total training cost: ~$400 for all 8 models

**Note:** The published models were trained on the earlier v2.0 baseline. A retrain on the current corpus is planned for a future release.

**Read More:** [SecureCode Models: Training Security-Aware Code Generation](https://huggingface.co/blog/scthornton/securecode-models)

---

## Dataset Statistics

| Metric | Value |
|--------|-------|
| **Total Examples** | 1,625 |
| **Baseline (v2.0)** | 1,159 examples (11 languages, OWASP Top 10 2021) |
| **Framework Additions** | 219 examples (9 frameworks, framework-native security) |
| **XSS expansion pack (v2.3)** | 70 examples (server-rendered XSS across 7 languages) |
| **Coverage packs (v2.4)** | 125 examples (CSRF/redirect/clickjacking, file-upload/traversal, Django) |
| **Currency packs (v2.5)** | 85 examples (supply-chain/CI-CD, OAuth/OIDC, 2025 framework CVEs) |
| **Vulnerability Categories** | 10 (complete OWASP Top 10:2021) |
| **Programming Languages** | 13 (incl. YAML/Dockerfile/JSON config) |
| **Average Conversation Length** | 4 turns (user - assistant - user - assistant) |

### Vulnerability Coverage

Distribution across both OWASP taxonomies. Counts computed from the released parquet (1,625 examples).

| OWASP 2021 | OWASP 2025 (mapped) | Examples |
|---|---|---|
| A01:2021 — Broken Access Control | A01:2025 — Broken Access Control | 303 |
| A02:2021 — Cryptographic Failures | A04:2025 — Cryptographic Failures | 135 |
| A03:2021 — Injection | A05:2025 — Injection | 303 |
| A04:2021 — Insecure Design | A06:2025 — Insecure Design | 138 |
| A05:2021 — Security Misconfiguration | A02:2025 — Security Misconfiguration | 158 |
| A06:2021 — Vulnerable and Outdated Components | A03:2025 — Software Supply Chain Failures | 137 |
| A07:2021 — Identification and Authentication Failures | A07:2025 — Authentication Failures | 234 |
| A08:2021 — Software and Data Integrity Failures | A08:2025 — Software or Data Integrity Failures | 99 |
| A09:2021 — Security Logging and Monitoring Failures | A09:2025 — Security Logging and Alerting Failures | 66 |
| A10:2021 — Server-Side Request Forgery | (folded into A01:2025) | 52 |
| (none) | A10:2025 — Mishandling of Exceptional Conditions | 0 *(documented gap)* |
| **Total** | | **1,625** |

Aggregated by OWASP 2025 (after SSRF folds into Broken Access Control):

| OWASP 2025 Category | Examples |
|---|---|
| A01:2025 — Broken Access Control | 355 (303 + 52 SSRF) |
| A05:2025 — Injection | 303 |
| A07:2025 — Authentication Failures | 234 |
| A04:2025 — Cryptographic Failures | 135 |
| A02:2025 — Security Misconfiguration | 158 |
| A06:2025 — Insecure Design | 138 |
| A03:2025 — Software Supply Chain Failures | 137 |
| A08:2025 — Software or Data Integrity Failures | 99 |
| A09:2025 — Security Logging and Alerting Failures | 66 |
| A10:2025 — Mishandling of Exceptional Conditions | 0 |

### Programming Language Distribution

Counts computed from the released parquet (1,625 examples).

| Language | Examples | Frameworks/Tools |
|----------|----------|------------------|
| **JavaScript** | 342 | Express.js, React, Vue, GraphQL |
| **Python** | 341 | Flask, Django, FastAPI, SQLAlchemy, Jinja2 |
| **Java** | 248 | Spring Boot, JSP, Thymeleaf |
| **Go** | 173 | Gin, net/http, html/template |
| **TypeScript** | 128 | Next.js, NestJS, React Server Components |
| **PHP** | 123 | Laravel, Symfony, Blade, Twig |
| **C#** | 109 | ASP.NET Core, Razor |
| **Ruby** | 66 | Ruby on Rails, ERB |
| **YAML** | 41 | GitHub Actions, IaC / config (Docker, K8s) |
| **Rust** | 29 | Actix, Axum |
| **Kotlin** | 18 | Spring Boot, Ktor |
| **Dockerfile** | 4 | Container build hardening |
| **JSON** | 3 | package.json / npmrc supply-chain config |

### Framework-Specific Additions (219 Examples)

The framework additions provide deep, idiomatic security patterns for 9 popular web frameworks:

| Framework | Language | Examples | Focus Areas |
|-----------|----------|----------|-------------|
| **Express.js** | JavaScript | 69 | Middleware security, session handling, CORS, auth |
| **Spring Boot** | Java | 50 | Security filters, bean validation, JDBC, SpEL/deserialization |
| **React** | JavaScript/TypeScript | 18 | XSS sinks, dangerouslySetInnerHTML, SSR data handling |
| **Next.js** | TypeScript | 17 | Server-action authz, middleware auth, API routes |
| **FastAPI** | Python | 16 | Pydantic validation, OAuth2, dependency injection |
| **GraphQL** | JavaScript | 15 | Authz, introspection, query depth/complexity |
| **SQLAlchemy** | Python | 14 | ORM injection, raw/text() query safety |
| **Flask** | Python | 12 | Blueprint security, Werkzeug, Jinja2 |
| **Vue.js** | JavaScript | 8 | Template injection, v-html, client-side trust |

These framework-specific examples go beyond generic language patterns to demonstrate how each framework's built-in security features should be used correctly, covering framework-native authentication, ORM-specific injection patterns, template engine escaping, middleware security chains, and framework-idiomatic input validation.

### Severity Distribution

Counts from the released parquet (1,625 examples).

| Severity | Examples | Percentage |
|----------|----------|------------|
| **CRITICAL** | 1085 | 66.8% |
| **HIGH** | 516 | 31.8% |
| **MEDIUM** | 24 | 1.5% |

---

## What Makes This Different?

### 1. Incident Grounding

Every example references real security incidents:
- **Equifax breach (CVE-2017-5638)** - $425M cost from Apache Struts RCE
- **Capital One SSRF attack (2019)** - 100M customer records exposed
- **SolarWinds supply chain (CVE-2020-10148)** - Documented authentication bypasses

### 2. 4-Turn Conversational Structure

Unlike code-only datasets, each example follows realistic developer workflows:

**Turn 1:** Developer requests functionality ("build JWT authentication")
**Turn 2:** Assistant provides vulnerable + secure implementations with attack demos
**Turn 3:** Developer asks advanced questions ("how does this scale to 10K users?")
**Turn 4:** Assistant delivers defense-in-depth operational guidance

### 3. Comprehensive Operational Guidance

Every example includes:
- **SIEM Integration** - Splunk/Elasticsearch detection rules
- **Logging Strategies** - Security event capture patterns
- **Monitoring Recommendations** - Metrics and alerting
- **Infrastructure Hardening** - Docker, AppArmor, WAF configs
- **Testing Approaches** - Language-specific security testing

### 4. Rigorous Quality Validation

- **100% CVE Format Compliance** - All CVE references validated
- **100% Language Tag Validity** - Proper language assignments
- **100% Structural Compliance** - 4-turn conversation format
- **Expert Security Review** - Independent validation by security professionals
- **Zero Content Duplicates** - 1,203 duplicates removed from baseline

---

## Dataset Structure

**For almost all users, load the Parquet files** (via `load_dataset`, below). They hold the complete web dataset (baseline + framework additions) in train/validation/test splits of 1,249/186/190 = **1,625 examples**, and back the dataset viewer.

The `data/` directory also keeps the raw source files for humans to browse:
- **Baseline files** covering the 1,159 web security baseline examples
- **219 framework files** for the framework-specific additions

Note two things if you parse `data/` directly rather than the Parquet:
- The source files total **1,626 examples**, one more than the Parquet. The extra one is `sql-injection-000032`, a corrected example staged in `command_injection_batch_007.jsonl` for a future split rebuild; the other 1,625 match the release splits.
- Despite the `.jsonl` extension, many source files are **pretty-printed multi-line JSON** (one JSON object spanning multiple lines), not line-delimited JSON. A naive line-by-line `json.loads(line)` will fail on them; see the loader below.

> **`id` is not a unique key.** Example ids restart per batch file, so the same id (e.g. `authentication-000002`) appears on many distinct examples. There are only ~405 unique ids across the dataset. Deduplicate by row/content, never by `id`.

### Example Format

Each example is a 4-turn conversation in JSON format:

```json
{
  "id": "express_js-auth_failures-000001",
  "metadata": {
    "category": "Authentication Failures",
    "lang": "javascript",
    "owasp_2021": "A07",
    "severity": "CRITICAL",
    "cwe": "CWE-287"
  },
  "context": {
    "cve": "CVE-2022-23529",
    "real_world_incident": "JWT authentication bypass in production systems",
    "impact": "Complete authentication bypass"
  },
  "conversations": [
    {"turn": 1, "from": "human", "value": "How do I implement secure JWT authentication in Express.js?"},
    {"turn": 2, "from": "assistant", "value": "# Real-World Incident\nCVE-2022-23529..."},
    {"turn": 3, "from": "human", "value": "How does this scale to 10,000 concurrent users?"},
    {"turn": 4, "from": "assistant", "value": "# Production Scaling & Defense-in-Depth..."}
  ],
  "validation": {
    "syntax_check": "pass",
    "security_review": "pass"
  }
}
```

---

## Usage

### Load with Hugging Face Datasets

```python
from datasets import load_dataset

# Load the complete dataset (1,625 examples)
dataset = load_dataset("scthornton/securecode-web")

# Access splits
train_data = dataset["train"]
val_data = dataset["validation"]
test_data = dataset["test"]

# Inspect an example
print(train_data[0]["id"])
```

The Parquet splits already include the framework additions; `load_dataset` is all
most users need.

### Loading the raw source files in `data/`

Only needed if you want the 7 unreleased correction rows or prefer the raw files.
Many files are pretty-printed multi-line JSON despite the `.jsonl` extension, so
parse each file as a whole with a streaming decoder rather than line by line:

```python
import json
from pathlib import Path

def load_any(path):
    """Yield objects from a file that is either JSONL or pretty-printed JSON."""
    text = Path(path).read_text()
    # Fast path: line-delimited JSON
    try:
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    except json.JSONDecodeError:
        pass
    # Whole-file: a single object, an array, or concatenated pretty objects
    dec, idx, out, s = json.JSONDecoder(), 0, [], text.strip()
    while idx < len(s):
        obj, end = dec.raw_decode(s, idx)
        out.append(obj)
        idx = end
        while idx < len(s) and s[idx] in " \r\n\t":
            idx += 1
    return out

examples = []
for path in Path("data").glob("*.jsonl"):
    examples.extend(load_any(path))

print(f"Loaded {len(examples)} examples")  # 1,379
```

### Fine-Tuning Example

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments

model_name = "meta-llama/Llama-3.2-3B"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Prepare dataset for training.
# Conversations live under "conversations" as {turn, from, value} with
# from in {human, assistant}; convert to the {role, content} the chat template expects.
def format_conversation(example):
    messages = [
        {"role": "user" if turn["from"] == "human" else "assistant",
         "content": turn["value"]}
        for turn in example["conversations"]
    ]
    formatted = tokenizer.apply_chat_template(messages, tokenize=False)
    return {"text": formatted}

train_dataset = dataset["train"].map(format_conversation)

# Configure training
training_args = TrainingArguments(
    output_dir="./securecode-finetuned",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    learning_rate=2e-5,
    logging_steps=100,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
)

trainer.train()
```

---

## Citation

If you use SecureCode Web in your research, please cite:

```bibtex
@misc{thornton2025securecode,
  title={SecureCode v2.0: A Production-Grade Dataset for Training Security-Aware Code Generation Models},
  author={Thornton, Scott},
  year={2025},
  month={December},
  publisher={perfecXion.ai},
  url={https://perfecxion.ai/articles/securecode-v2-dataset-paper.html},
  note={Dataset: https://huggingface.co/datasets/scthornton/securecode-web}
}
```

---

## License

This dataset is released under the **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (CC BY-NC-SA 4.0)**.

---

## Links

- **Research Paper**: [https://huggingface.co/papers/2512.18542](https://huggingface.co/papers/2512.18542)
- **Model Collection**: [https://huggingface.co/collections/scthornton/securecode](https://huggingface.co/collections/scthornton/securecode) (8 trained models)
- **Blog Post**: [https://huggingface.co/blog/scthornton/securecode-models](https://huggingface.co/blog/scthornton/securecode-models)
- **GitHub Repository**: [https://github.com/scthornton/securecode-web](https://github.com/scthornton/securecode-web)
- **This Dataset**: [https://huggingface.co/datasets/scthornton/securecode-web](https://huggingface.co/datasets/scthornton/securecode-web) (1,625 web security examples)
- **Unified Dataset**: [https://huggingface.co/datasets/scthornton/securecode](https://huggingface.co/datasets/scthornton/securecode) (all 2,185 examples)
- **AI/ML Security**: [https://huggingface.co/datasets/scthornton/securecode-aiml](https://huggingface.co/datasets/scthornton/securecode-aiml) (750 AI/ML examples)

---

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Adding new vulnerability examples
- Improving existing content
- Validation and quality assurance
- Documentation improvements

---

## Acknowledgments

- Security research community for responsible disclosure practices
- Three anonymous security experts who provided independent validation
- OWASP Foundation for maintaining the Top 10 taxonomy
- MITRE Corporation for the CVE database

---

## Quality Metrics

| Metric | Result |
|--------|--------|
| CVE Format Compliance | 100% (all CVE values well-formed) |
| Language Tag Validity | 100% |
| Content Quality Standards | 100% |
| 4-Turn Structure Compliance | 99.9% (1,624 / 1,625; one 6-turn example) |
| Incident Grounding | 100% (every example has a real_world_incident; ~82% additionally carry a CVE) |
| Expert Security Review | Complete (3 independent validators for baseline) |
| Content Deduplication | 1,203 duplicates removed from baseline |
