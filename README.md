---
language:
- code
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
    num_examples: 1102
  - name: validation
    num_examples: 138
  - name: test
    num_examples: 138
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

![Version](https://img.shields.io/badge/version-2.1.0-blueviolet.svg)
![License](https://img.shields.io/badge/license-CC%20BY--NC--SA%204.0-blue.svg)
![Examples](https://img.shields.io/badge/examples-1,378-green.svg)
![Languages](https://img.shields.io/badge/languages-12-orange.svg)
![Quality](https://img.shields.io/badge/quality-100%25_validated-brightgreen.svg)
![CVE Grounding](https://img.shields.io/badge/CVE_grounding-100%25-blue.svg)
![EPSS](https://img.shields.io/badge/EPSS-97.7%25_coverage-blue.svg)
![OWASP](https://img.shields.io/badge/OWASP-2021%20%7C%202025-orange.svg)

**Production-grade web security vulnerability dataset with complete incident grounding, 4-turn conversational structure, and comprehensive operational guidance**

[Paper](https://huggingface.co/papers/2512.18542) | [GitHub](https://github.com/scthornton/securecode-web) | [Dataset](https://huggingface.co/datasets/scthornton/securecode-web) | [Model Collection](https://huggingface.co/collections/scthornton/securecode) | [Blog Post](https://huggingface.co/blog/scthornton/securecode-models)

</div>

---

## What's new in v2.1

v2.1 adds **deployment-grade exploitability metadata** to every example. Users can now filter by *what's actually exploitable in their environment*, not just by severity.

| Field | Coverage | Source |
|---|---|---|
| **EPSS** (exploit-probability score + percentile) | 97.7% (1,346 / 1,378) | FIRST.org EPSS API + severity-bucket approximation for composite examples |
| **CVSS v3.1 vector** | 77.4% (1,067 / 1,378) | NVD API |
| **CVSS v4.0 vector** | 2.0% (28 / 1,378) | NVD API where published; most CVEs not yet rated v4 |
| **Preconditions** (auth_required, network_position, user_interaction, prior_access) | 94.9% (1,308 / 1,378) | Parsed from CVSS or category-heuristic |
| **MITRE CAPEC IDs** | 71.0% (979 / 1,378) | Derived from CWE via MITRE catalog |
| **MITRE ATT&CK techniques** | 54.3% (748 / 1,378) | Heuristic mapping from CWE |
| **OWASP Top 10:2025 dual-field** | 100% (1,378 / 1,378) | Migrated from 2021 with non-breaking dual fields |

Every derived field carries paired `*_source` and `*_confidence` markers so you can distinguish measured from heuristic-derived values. Confidence enum: `measured` | `heuristic` | `approximated` | `absent`.

### Non-breaking migration

v2.1 is fully backward compatible. The existing `metadata.owasp_2021` field is preserved (and corrected — see below). New `metadata.owasp_2025` is added alongside. Existing pipelines querying `owasp_2021` keep working.

### Data-quality corrections in v2.1

While migrating, we fixed pre-existing issues in v2.0:

- 60 SQL examples in `sql_batch_201.jsonl` had `owasp_2021: "Unknown"` and `cwe: "CWE-000"` — corrected to `A03:2021-Injection` and `CWE-89`
- 10 `express_js-injection-*` examples had truncated `owasp_2021: "A03"` — corrected to full label
- 2 SSRF examples had inconsistent `(SSRF)` suffix — normalized
- 6 SSTI examples had truncated conversations in JSONL (parquet had full content) — JSONL restored from parquet
- 50 AI/ML examples in `data/` (not in any release split) moved to `data/_archived_duplicates/ai_ml_removed/` (they belong in `scthornton/securecode-aiml`)
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
| **SecureCode Web** | 1,378 | Traditional web & application security (OWASP Top 10 2021) | This dataset |
| **SecureCode AI/ML** | 750 | AI/ML system security (OWASP LLM Top 10 2025) | [scthornton/securecode-aiml](https://huggingface.co/datasets/scthornton/securecode-aiml) |

For the combined dataset with both web and AI/ML security examples, use [`scthornton/securecode`](https://huggingface.co/datasets/scthornton/securecode).

---

## Overview

SecureCode Web is a rigorously validated dataset of **1,378 web security-focused coding examples** designed to train security-aware AI code generation models. Every example is grounded in real-world security incidents (CVEs, breach reports), provides both vulnerable and secure implementations, demonstrates concrete attacks, and includes defense-in-depth operational guidance.

The dataset focuses exclusively on **traditional web and application security** (OWASP Top 10 2021) and includes the original **1,159 baseline examples** covering 11 programming languages, plus **219 framework-specific additions** targeting 9 popular web frameworks with deep, idiomatic security patterns.

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

**Note:** Models were trained on the v2.0 baseline (1,216 examples). Retraining with the full 1,435 examples is planned for a future release.

**Read More:** [SecureCode Models: Training Security-Aware Code Generation](https://huggingface.co/blog/scthornton/securecode-models)

---

## Dataset Statistics

| Metric | Value |
|--------|-------|
| **Total Examples** | 1,378 |
| **Baseline (v2.0)** | 1,159 examples (12 languages, OWASP Top 10 2021) |
| **Framework Additions** | 219 examples (9 frameworks, framework-native security) |
| **Vulnerability Categories** | 10 (complete OWASP Top 10:2021) |
| **Programming Languages** | 12 |
| **Average Conversation Length** | 4 turns (user - assistant - user - assistant) |

### Vulnerability Coverage

Distribution across both OWASP taxonomies. Counts computed from the released parquet (post-v2.1 corrections).

| OWASP 2021 | OWASP 2025 (mapped) | Examples |
|---|---|---|
| A01:2021 — Broken Access Control | A01:2025 — Broken Access Control | 211 |
| A02:2021 — Cryptographic Failures | A04:2025 — Cryptographic Failures | 179 |
| A03:2021 — Injection | A05:2025 — Injection | 218 |
| A04:2021 — Insecure Design | A06:2025 — Insecure Design | 108 |
| A05:2021 — Security Misconfiguration | A02:2025 — Security Misconfiguration | 151 |
| A06:2021 — Vulnerable and Outdated Components | A03:2025 — Software Supply Chain Failures | 100 |
| A07:2021 — Identification and Authentication Failures | A07:2025 — Authentication Failures | 207 |
| A08:2021 — Software and Data Integrity Failures | A08:2025 — Software or Data Integrity Failures | 87 |
| A09:2021 — Security Logging and Monitoring Failures | A09:2025 — Security Logging and Alerting Failures | 66 |
| A10:2021 — Server-Side Request Forgery | (folded into A01:2025) | 51 |
| (none) | A10:2025 — Mishandling of Exceptional Conditions | 0 *(documented gap)* |
| **Total** | | **1,378** |

Aggregated by OWASP 2025 (after SSRF folds into Broken Access Control):

| OWASP 2025 Category | Examples |
|---|---|
| A01:2025 — Broken Access Control | 262 (211 + 51 SSRF) |
| A05:2025 — Injection | 218 |
| A07:2025 — Authentication Failures | 207 |
| A04:2025 — Cryptographic Failures | 179 |
| A02:2025 — Security Misconfiguration | 151 |
| A06:2025 — Insecure Design | 108 |
| A03:2025 — Software Supply Chain Failures | 100 |
| A08:2025 — Software or Data Integrity Failures | 87 |
| A09:2025 — Security Logging and Alerting Failures | 66 |
| A10:2025 — Mishandling of Exceptional Conditions | 0 |

### Programming Language Distribution

| Language | Examples | Frameworks/Tools |
|----------|----------|------------------|
| **Python** | 255+ | Django, Flask, FastAPI |
| **JavaScript** | 245+ | Express.js, NestJS, React, Vue |
| **Java** | 189+ | Spring Boot |
| **Go** | 159+ | Gin framework |
| **PHP** | 123+ | Laravel, Symfony |
| **TypeScript** | 89+ | NestJS, Angular |
| **C#** | 78+ | ASP.NET Core |
| **Ruby** | 56+ | Ruby on Rails |
| **Rust** | 12+ | Actix, Rocket |
| **Kotlin** | 9+ | Spring Boot |
| **YAML** | IaC configurations | |
| **HCL** | Terraform configurations | |

### Framework-Specific Additions (219 Examples)

The framework additions provide deep, idiomatic security patterns for 9 popular web frameworks:

| Framework | Language | Examples | Focus Areas |
|-----------|----------|----------|-------------|
| **Express.js** | JavaScript | 25 | Middleware security, session handling, CORS |
| **Django** | Python | 25 | ORM injection, CSRF, template escaping |
| **Spring Boot** | Java | 25 | Security filters, bean validation, JDBC |
| **Flask** | Python | 25 | Blueprint security, Werkzeug, Jinja2 |
| **Ruby on Rails** | Ruby | 24 | Strong parameters, ActiveRecord, Devise |
| **Laravel** | PHP | 24 | Eloquent security, middleware, Blade |
| **ASP.NET Core** | C# | 24 | Identity framework, anti-forgery, LINQ |
| **FastAPI** | Python | 24 | Pydantic validation, OAuth2, dependencies |
| **NestJS** | TypeScript | 23 | Guards, pipes, interceptors, TypeORM |

These framework-specific examples go beyond generic language patterns to demonstrate how each framework's built-in security features should be used correctly, covering framework-native authentication, ORM-specific injection patterns, template engine escaping, middleware security chains, and framework-idiomatic input validation.

### Severity Distribution

| Severity | Examples | Percentage |
|----------|----------|------------|
| **CRITICAL** | ~930 | 64.8% |
| **HIGH** | ~460 | 32.1% |
| **MEDIUM** | ~45 | 3.1% |

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

The `data/` directory contains individual JSONL files:
- **Baseline JSONL files** (multi-line JSONL, 1,159 web security examples) - Original v2.0 web examples
- **219 framework files** (single-JSON JSONL, 219 examples) - Framework-specific additions

The Parquet files provide the complete web dataset (baseline + framework additions) in train/validation/test splits (1,102/138/138).

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

# Load the dataset (parquet splits - v2.0 baseline)
dataset = load_dataset("scthornton/securecode-web")

# Access splits
train_data = dataset["train"]
val_data = dataset["validation"]
test_data = dataset["test"]

# Inspect an example
print(train_data[0]["id"])
```

### Load All Examples (Including Framework Additions)

```python
import json
from pathlib import Path

# Clone the repo first, then load all JSONL files
examples = []
for path in Path("data").glob("*.jsonl"):
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                examples.append(json.loads(line))

print(f"Loaded {len(examples)} examples")  # 1,378
```

### Fine-Tuning Example

```python
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments

model_name = "meta-llama/Llama-3.2-3B"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Prepare dataset for training
def format_conversation(example):
    formatted = tokenizer.apply_chat_template(
        example["messages"],
        tokenize=False
    )
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
- **This Dataset**: [https://huggingface.co/datasets/scthornton/securecode-web](https://huggingface.co/datasets/scthornton/securecode-web) (1,378 web security examples)
- **Unified Dataset**: [https://huggingface.co/datasets/scthornton/securecode](https://huggingface.co/datasets/scthornton/securecode) (all 2,185 examples)
- **AI/ML Security**: [https://huggingface.co/datasets/scthornton/securecode-aiml](https://huggingface.co/datasets/scthornton/securecode-aiml) (750 AI/ML examples)
- **Original v2.0 Baseline**: [https://huggingface.co/datasets/scthornton/securecode-v2](https://huggingface.co/datasets/scthornton/securecode-v2) (1,209 baseline examples)

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
| CVE Format Compliance | 100% |
| Language Tag Validity | 100% |
| Content Quality Standards | 100% |
| 4-Turn Structure Compliance | 100% |
| Incident Grounding | 100% (all examples tied to real incidents) |
| Expert Security Review | Complete (3 independent validators for baseline) |
| Content Deduplication | 1,203 duplicates removed from baseline |
