# SecureCode Web — Upgrade Roadmap

Status: **draft for review**
Owner: Scott Thornton (@scthornton)
Last updated: 2026-04-24

This document specifies the next four releases of SecureCode Web. Each release is scoped independently and can be shipped on its own schedule. The goal is to move the dataset from "popular training corpus" to "reference benchmark with deployment-grade metadata and agentic relevance."

---

## 1. Goals and non-goals

### Goals

- Reduce false-positive rates in downstream-trained security models (negatives).
- Make examples filterable by exploitability, not just severity (metadata enrichment).
- Cover infrastructure-as-code with the same depth as application code (IaC).
- Stay relevant for agent-based coding workflows (agentic track).

### Non-goals

- Re-introducing AI/ML content — stays in `scthornton/securecode-aiml`.
- Rewriting existing 4-turn examples. All upgrades are additive or metadata-only.
- Changing the CC BY-NC-SA license in this roadmap (separate strategic decision).

### Guiding principles

1. **Additive, not breaking.** Every release must load cleanly with existing consumer code. Schema extensions require default values so old loaders see no change.
2. **Separate HF configs for new tracks.** Agentic content ships as its own config; the default config remains 4-turn web.
3. **Metadata before content.** v2.1 enriches what exists so downstream users feel the upgrade immediately, before waiting for new content.
4. **Multi-layer review on safety-critical changes.** Cross-model review (generator/reviewer split across OpenAI and Anthropic, with reviewer cold to generator's rationale) **plus** Scott + Opus 4.7 adjudication on every accepted example **plus** external security professional reviewing a 10% random sample before public release (§11). "Looks safe but isn't" is the failure mode we're defending against; multi-layer review addresses it where any single layer would not.

---

## 2. Release plan

Five phases. Phases 1, 2, 4 each ship a Web-dataset release. Phase 3 ships a **new sibling dataset** (`securecode-infra`). Phase 5 (agentic v3.0) is deferred 6 months pending ecosystem evidence.

| Phase | Release | Scope | Effort | API $ | Invocation |
|---|---|---|---|---|---|
| **Phase 1** | **v2.1** (Web) | OWASP 2021→2025 reconcile + metadata enrichment | ~50 hr | $0 | `execute phase 1` |
| **Phase 2** | **v2.2** (Web) | Generation harness (task 2.1) + evidence-based pattern selection (task 2.2) + FP-rate eval (task 2.3) + safe-but-suspicious negatives (task 2.4) | ~120 hr | ~$60 | `execute phase 2` |
| **Phase 3** | **`securecode-infra` v0.1** (NEW sibling) | Infrastructure & Supply Chain — 30 Terraform + 30 K8s + 30 CI/CD/supply-chain | ~80 hr | ~$30 | `execute phase 3` |
| **Phase 4** | **v2.4** (Web) | Executable verification — Docker harness + ~50 critical examples with verified exploit + verified fix | ~120 hr | ~$20 | `execute phase 4` |
| **Phase 5** | deferred | Agentic review loops (v3.0). Decision point in 6 months: ship only if at least one major actor (Anthropic, OpenAI, Cursor, Cline, Aider, Copilot Workspace) publishes fine-tuning results on agentic-loop data showing measurable improvement. | ~320 hr if pursued | ~$140 | `execute phase 5` (when criteria met) |

**Committed work (Phases 1–4 pilot):** ~405 hours, ~$100 cloud + ~$50 external reviewer + ~$145 Scott's Opus review = **~$295 total.** Part-time at 15 hr/week: ~7 months.

**Adding Phase 4.5 (v2.5 scale-up):** +~150 hr + ~$15 = **~$310 total** through v2.5. Part-time: ~10 months.

**If Phase 5 (agentic) is pursued after the 6-month decision point:** add ~360 hr + ~$140 cloud + ~$120 review = ~$260 more. Part-time: ~6 additional months.

**Total upside-bound (all five phases + v2.5 scale):** ~915 hours, ~$570 across all releases.

Key shifts from prior plan (post external review):
- **Effort estimates revised 30–50% upward** in several places (negatives review minutes, manual metadata, detection rules, exec verification per-example) — reviewer correctly noted my originals were optimistic.
- **Phase 4 reduced to 12-example pilot**, with v2.5 scale-up phase added separately. Quality over quantity for first executable-verification release.
- **Methodology architecture revised**: cross-model review + Scott/Opus adjudication (both layers, not single-pass + Opus alone). Adds ~$60 cloud and ~$50 external reviewer cost but quality bar is now defensible.
- **v2.2 negatives ship as opt-in `safe_controls` config only** (not default-mixed). Default `train` unchanged.
- **5 of 15 negative pattern categories dropped** because safety depended on environmental claims rather than machine-checkable code. Target now 100 examples not 150.
- **External reviewer added as Phase 2 requirement** — 10% sample of negatives reviewed by independent security professional before public release.
- **Phase 3 CI/CD subset narrowed** to GitHub Actions + npm supply chain only for v0.1; defer GitLab CI / Jenkins / Cargo / Go to v0.2.
- **Phase 1 OWASP migration is non-breaking** — dual fields (`owasp_2021_legacy` + `owasp_2025`), not rename-and-replace.

### 2.1 Phase-to-release mapping

**Effort estimates revised after external review** — original projections were 30–50% optimistic on several lines (manual metadata, pattern derivation, negatives review minutes/example, detection-rule authoring, exec verification per-example). Numbers below reflect realistic estimates.

| Phase | Release | Target repo | Effort | Cloud $ | Review $ | Activity breakdown |
|---|---|---|---|---|---|---|
| **Phase 1** | v2.1 | securecode-web | ~75 hr | $0 | ~$5 | OWASP reconcile (non-breaking dual-field): 10 · Enrichment script: 14 · Run: 4 · Manual queue (350 cases × 7 min avg): **40** · QA: 4 · Schema+README+parquet+handoff: 8 |
| **Phase 2** | v2.2 | securecode-web | ~145 hr | ~$60 | ~$110 | **Task 2.1** Generation harness: 25 · **Task 2.2** Evidence-based pattern selection: 20 · **Task 2.3** FP/FN-rate eval baseline: 12 · **Task 2.4** Cross-model gen + cold review + Scott/Opus adjudication: schema 4 · gen+review oversight 15 · adjudication (20 min × 100) **35** · external reviewer coord 10 · parquet 6 · post-fine-tune FP/FN delta 12 · taxonomy/template 6 |
| **Phase 3** | securecode-infra v0.1 | **NEW sibling repo** | ~100 hr | ~$30 | ~$25 | Sibling repo bootstrap: 8 · Incident library + taxonomy: 12 · Terraform 30 ex: 22 · K8s 30 ex: 22 · CI/CD-narrowed (GitHub Actions + npm only) 30 ex: 18 · Detection-rule authoring (real validation against 5 tools): **15** · README+parquet: 6 |
| **Phase 4** | v2.4 (pilot) | securecode-web | ~85 hr | ~$10 | ~$5 | Selection+planning: 8 · Docker template iteration: 16 · 12 verifications × 2 hr avg: 24 · CI integration: 12 · schema rollout: 4 · README+card+lessons: 12 · end-to-end test: 8 |
| **Phase 4.5** | v2.5 (scale) | securecode-web | placeholder ~150 hr | ~$5 | ~$10 | Set after pilot retrospective. Rough budget for 38 additional verifications. Re-baselined post-pilot. |
| **Phase 5** | v3.0 (if pursued) | securecode-web (agentic config) | ~360 hr | ~$140 | ~$120 | Schema+config 20 · voice bible 20 · harness ext 15 · gen+review oversight 180 · adjudication 60 · eval harness 50 · fine-tune+metrics 15 |

### 2.2 Cumulative checkpoints

| At end of | Cum hours | Cum $ | What's live on HF |
|---|---|---|---|
| **Phase 1 ships (v2.1)** | ~75 | ~$5 | securecode-web: 1,378 examples + enriched metadata (EPSS, ATT&CK, CAPEC, preconditions). Non-breaking dual-field OWASP migration. |
| **Phase 2 ships (v2.2)** | ~220 | ~$170 | securecode-web: opt-in `safe_controls` config with 100 examples (target). Default `train`/`val`/`test` unchanged. FP/FN baseline + post-fine-tune delta published. External reviewer's 10% sample documented. |
| **Phase 3 ships (`securecode-infra` v0.1)** | ~320 | ~$225 | NEW sibling: 90 examples (Terraform 30 + K8s 30 + GitHub Actions/npm 30); securecode-web unchanged |
| **Phase 4 ships (v2.4 pilot)** | ~405 | ~$240 | securecode-web: 12 examples have `validation.code_execution: passed` with Docker repro + CI verification. First dataset of its kind, even at pilot scale. Pilot lessons doc published. |
| **(v2.5 scale-up)** | ~555 | ~$255 | securecode-web: ~50 verified examples (including pilot) — full executable-verification subset |
| **(Phase 5 if pursued, v3.0)** | ~915 | ~$515 | securecode-web: agentic config (preview); default config unchanged |

### 2.3 Calendar at three paces

| Pace | Hours/week | v2.1 | v2.2 | infra v0.1 | v2.4 pilot | v2.5 scale | (v3.0 if pursued) |
|---|---|---|---|---|---|---|---|
| Weekend warrior | ~8 | Wk 10 | Wk 28 | Wk 40 | Wk 51 | Wk 70 | Wk 115 |
| **Part-time (default)** | ~15 | Wk 5 | Wk 15 | Wk 22 | Wk 27 | Wk 37 | Wk 61 |
| Focused sprint | ~30 | Wk 3 | Wk 8 | Wk 11 | Wk 14 | Wk 19 | Wk 31 |

Phases 1–4 take 6–7 months part-time. Phase 5 (agentic) decision point is at month 6 with explicit go/no-go criteria.

### 2.4 Dependency graph

```
Phase 1 (v2.1 metadata)
  ├── Task 1.1: OWASP reconcile ──┐
  └── Task 1.2: enrichment       ──┴──▶ [v2.1 ships to securecode-web]

Phase 2 (v2.2 negatives)
  ├── Task 2.1: generation harness  ──┐
  ├── Task 2.2: evidence-based       │
  │             pattern selection    │
  ├── Task 2.3: FP-rate eval         │
  │             baseline             │
  └── Task 2.4: negatives gen+review ┴──▶ [v2.2 ships to securecode-web]
                                          │
              ┌───────── parallelizable ─┼──▶ Phase 3 (infra v0.1) ──▶ [ships to NEW securecode-infra]
              │                          │
              │                          └──▶ Phase 4 (v2.4 exec verif) ──▶ [v2.4 ships to securecode-web]

[Decision point: 6 months after Phase 4 ships]
                                                 │
                                                 ├── if criteria met ──▶ Phase 5 (v3.0 agentic)
                                                 └── if not ──────────▶ skip; pursue executable verification expansion or other gaps
```

Phase 1 gates everything. Phase 2's harness (task 2.1) is reused by Phase 3 and Phase 5 (if pursued). Phase 4 (executable verification) is independent of Phase 2's harness — different infrastructure (Docker compose vs. cross-model API). Phases 3 and 4 can run in parallel after Phase 2 if reviewer bandwidth permits — but recommend sequential at part-time pace.

---

## 3. Spec: v2.1 — Metadata Enrichment

### Rationale

Users currently filter by `severity` (4 values) and `owasp_2021` (10 values). That's coarse. Adding EPSS (exploitability probability), MITRE ATT&CK mapping, CAPEC mapping, and explicit preconditions gives downstream users the ability to filter by "what can actually be exploited in my environment." Also makes the dataset legible to threat-intel tooling, not just training pipelines.

### Schema changes

Additions to `metadata` (all optional for backward compatibility):

```json
{
  "metadata": {
    "epss_score": 0.942,
    "epss_percentile": 0.993,
    "epss_date": "2026-04-24",
    "attack_techniques": ["T1190", "T1078.004"],
    "capec_ids": ["CAPEC-66", "CAPEC-115"],
    "cvss_v3_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
    "cvss_v4_vector": "CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N",
    "preconditions": {
      "auth_required": false,
      "network_position": "internet",
      "user_interaction": "none",
      "prior_access": "none"
    }
  }
}
```

Enum values for preconditions:
- `network_position`: `internet` | `adjacent` | `internal` | `local`
- `user_interaction`: `none` | `passive` | `active`
- `prior_access`: `none` | `authenticated_user` | `privileged` | `physical`

Also update `context.year` maximum in `schema.json` to 2026 (currently 2025 — already stale).

### Data sources

| Field | Source | Automation |
|---|---|---|
| `epss_*` | FIRST.org EPSS API (free) | Full |
| `attack_techniques` | MITRE CWE→ATT&CK mapping CSV | Full (derived from `metadata.cwe`) |
| `capec_ids` | MITRE CWE→CAPEC mapping CSV | Full (derived from `metadata.cwe`) |
| `cvss_v3_vector` | NVD API (free) | Full for real CVEs |
| `cvss_v4_vector` | NVD API where published | Full, ~25% coverage today |
| `preconditions` | Parsed from CVSS vector (AV/PR/UI) | Full for CVE-backed; manual for composites |

### Workflow

1. **Build enrichment script** (`scripts/enrich_metadata.py`, new) that:
   - Reads every `data/*.jsonl`
   - For CVE-backed examples: fetches EPSS, NVD CVSS, derives preconditions
   - For non-CVE examples: logs to `enrichment_manual_queue.json`
   - For all examples: derives ATT&CK and CAPEC from CWE
   - Writes enriched JSONL back, preserving original formatting (one-line vs pretty-printed — see `CLAUDE.md`)

2. **Run automation** across all 1,378 examples. Expect ~75% fully auto-enriched, ~25% queued for manual review.

3. **Manual review pass** for the queue (~350 composite-scenario examples). 2 min per example × 350 = ~12 hours.

4. **Validation pass**: 10% random sample, spot-check for correctness (~140 examples × 30 sec = 1.5 hr).

5. **Update schema.json** with new optional fields + year bump.

6. **Rebuild parquet splits** (1102/138/138 preserved).

7. **README update**: add "Metadata" section documenting new fields and sources.

### Acceptance criteria

- [ ] 100% of CVE-backed examples have EPSS score populated
- [ ] 100% of examples have ATT&CK + CAPEC populated (derived from CWE)
- [ ] 100% of examples have `preconditions` populated
- [ ] 90%+ have CVSS v3 vector; CVSS v4 where NVD provides it
- [ ] Schema extension validates against every example
- [ ] Existing loader code (README snippets) still works unchanged
- [ ] Parquet splits rebuilt and verified in train/val/test size match

### Effort

- Script development: 12–16 hours
- Automation run + debugging: 4 hours
- Manual enrichment queue: 12 hours
- Validation + QA: 4 hours
- Schema + README + parquet rebuild: 4 hours
- **Total: 36–40 hours**

### Risk

Low. All changes are additive. Worst case: EPSS/CVSS data is stale → ship a scheduled refresh (quarterly) as v2.1.x.

---

## 4. Spec: v2.2 — Safe-but-Suspicious Negatives

### Rationale

Every example currently shows "vulnerable → secure." A model trained on this learns to pattern-match on code that *looks* like common vuln shapes, without distinguishing whether context makes it safe. Result: high false-positive rate in production. Adding examples where code *looks* dangerous but is demonstrably safe trains the model to read context, not just surface patterns.

### Pre-generation tasks (new — added in critical assessment)

Two prerequisite tasks before any generation runs. These convert "we hope this reduces FP rates" into measurable claims.

**Task 2.2 — Evidence-based pattern selection (~10 hr).**

Don't pick the 15 negative-example patterns by author intuition. Derive them from data:

1. Source ~500 random functions from popular GitHub repos (no known CVEs, well-maintained projects: Django, Flask, FastAPI, Express, Spring Boot, Rails — match the dataset's framework coverage).
2. Run each function through your 8 existing fine-tuned SecureCode models (`llama-3.2-3b-securecode`, `qwen-coder-7b-securecode`, etc.).
3. Catalog every flag: which functions get marked vulnerable, what category, what model's output reasoning.
4. Cluster the false positives — code that no real reviewer would flag — into ~15 patterns by surface feature.
5. Use *those* 15 as the negative-example pattern taxonomy, not the heuristic list previously in this section.

**Output:** `docs/NEGATIVE_PATTERN_DERIVATION.md` documenting the data → pattern mapping. Becomes part of the v2.2 release notes — "we generated negatives for the patterns our models actually over-flagged, not patterns we guessed at."

**Task 2.3 — FP-rate eval baseline (~6 hr).**

Define the eval test set *before* Phase 2 generation begins. Without this, the "30% FP-rate reduction" target is unfalsifiable.

1. Curate 200 known-safe code examples — random sample from above 500-function pool that no model flagged plus 100 hand-picked tricky-but-safe samples (your spec for the patterns above).
2. Curate 200 known-vulnerable examples — held out from existing dataset's training data, ensuring no leakage from train splits.
3. Run all 400 through each existing fine-tuned model; record FP rate (% of safe code wrongly flagged) and FN rate (% of vulnerable code missed).
4. Save as `eval/v2-baseline-fp-fn.json` — the baseline to beat after v2.2 ships.
5. Acceptance for v2.2: re-run after fine-tuning with negatives folded in, report delta. Target ≥30% relative FP-rate reduction. Publish actual numbers regardless of result.

This is genuine science, not marketing. If the FP rate doesn't drop, that's a publishable negative result that informs the next iteration.

### Content design

**Target: 150 examples across 15 pattern categories (8–12 each).** Pattern categories now derived from Task 2.2's evidence rather than the original heuristic list.

The list below was the original heuristic taxonomy. **Treat as illustrative until Task 2.2 produces the data-derived list.** Expect 8–12 of these to survive plus 3–7 new ones we didn't anticipate.

**Pattern selection rule (added after external review):** safety must be *machine-checkable in the example's own code*, not asserted by environmental claims in prose. Drop categories where a model trained on the example would learn "this *looks* dangerous but a comment says it's fine, so it's fine." That trains models to rationalize bad patterns.

#### Acceptable patterns (safety enforced in code)

1. **`dangerouslySetInnerHTML` on DOMPurify-sanitized content** — Sanitization call is in the example.
2. **Weak hash used for non-security purposes** — Use site is unambiguously non-security (cache key derivation in the same file).
3. **Hardcoded "secrets" that are public constants** — Variable named `STRIPE_PUBLISHABLE_KEY`, OIDC `issuer` URL — type signature makes the intent legible.
4. **Permissive file upload with downstream sandboxing** — Sandbox boundary is in the example (e.g., separate worker process invocation visible).
5. **Reflective deserialization with type allowlist** — Allowlist is enforced in the deserialization call signature.
6. **Shell-out with strict argv separation** — `subprocess.run([...], shell=False)` form is unambiguous in code.
7. **Missing input length validation where platform enforces it** — Platform config (e.g., `nginx.conf` `client_max_body_size`) is shown alongside.
8. **Plaintext password handling in a password-change flow** — Plaintext is immediately hashed; control flow shows there's no persistence pre-hash.
9. **`innerHTML` from compile-time-trusted constant** — Source is a string literal in the same file, not a variable.
10. **Reflection-style API access with allowlist** — Allowlist defined as a constant in the same module.

#### Dropped patterns (safety depended on environmental claims)

These were in the original list but **removed after external review** because the safety claim depends on something *outside the code* and would train models to excuse bad patterns:

- ~~Safe `eval` / `exec` with allowlist~~ — Allowlist validation is just code; nothing in the eval signature itself enforces it. Too easy to silently break.
- ~~Raw SQL with upstream parameterization~~ — "Upstream" is invisible to the model reading this code; a model that learns "raw SQL is fine because someone said it's parameterized" is a vulnerability.
- ~~Intentionally open CORS on truly public API~~ — "Truly public" is an environmental claim; opens the door to models excusing CORS misconfig in non-public contexts.
- ~~Disabled CSRF on correctly-designed endpoints~~ — "Correctly designed" is the kind of vague justification we're trying to train *against*.
- ~~"Insecure" TLS config that's intentional~~ — Self-signed cert acceptance teaches "TLS bypass is sometimes fine"; too dangerous as a teaching signal.
- ~~Debug / admin endpoints gated by env + network~~ — Network gating isn't visible in app code; a model that learns to excuse exposed admin endpoints is a real vulnerability.

The 5 dropped patterns reflect a strict standard: **if the safety justification is "trust the environment," the example is rejected.** The remaining 10 patterns (and the 5–7 new ones derived from Task 2.2) all enforce safety in code that the model can see.

**Target reduced from 150 to 100 examples** as a result. 10 patterns × ~10 examples each = 100. Tighter, defensible.

### Example structure

Negatives follow the 4-turn structure but with a flipped Turn 2:

- **Turn 1** — Developer presents code or asks for review. Usually: "Is this safe?" or "I inherited this — what's wrong?"
- **Turn 2** — Assistant explains: (a) why this *looks* dangerous, (b) why it's actually safe, (c) **what would make it unsafe** (critical — this is the discriminator training signal).
- **Turn 3** — Developer asks a follow-up that probes the edge. Usually: "What if X changed?" where X is the precondition that keeps it safe.
- **Turn 4** — Assistant maps out when to refactor to a safer pattern anyway, monitoring hooks to detect if preconditions erode, and documentation practices.

### Schema changes

Add `metadata.example_type` (optional, default `"vulnerability"`):

```json
{
  "metadata": {
    "example_type": "safe_control"
  }
}
```

Enum: `"vulnerability"` | `"safe_control"`. Default = `"vulnerability"` for backward compat on all existing examples.

### ID scheme

`safe-<pattern>-<lang>-<NNNNNN>`

Examples: `safe-eval-allowlist-python-000001`, `safe-cors-wildcard-go-000003`.

Keep `metadata.category` and `metadata.owasp_2021` set to the category the negative is *about* (so filtering by injection returns both vulns and safe controls for injection patterns).

### HF config strategy

**Decision (revised after external review):** **Opt-in only for v2.2.** Ship as separate `safe_controls` HF config. **Do not** mix into default train/val/test splits. Users must explicitly request `load_dataset("scthornton/securecode-web", "safe_controls")` to get the negatives.

Rationale: a user who auto-loads `main` should not silently get a changed training objective for the highest-risk new content type. Default-mixing is a one-way door — once shipped, users training on `main` between v2.1 and v2.2 get inconsistent results depending on cache freshness.

**When default-mixing is reconsidered:** after v2.2 ships, fine-tune at least one existing SecureCode model with negatives folded in, run the FP/FN protocol from Task 2.3, and only propose default-mixing in a future release if results show:
- ≥30% relative FP-rate reduction
- ≤5% absolute FN-rate increase (no significant regression on detecting real vulnerabilities)
- External reviewer's 10% sample passed without revoked-acceptance findings

This becomes a *future v2.3 or v2.5 decision*, not a v2.2 commitment.

### Acceptance criteria

- [ ] 100 examples across ~10 pattern categories (target reduced from 150 after dropping environment-dependent patterns; final count after Task 2.2 derives data-driven taxonomy)
- [ ] Every pattern is **machine-checkable in the example's own code** — no examples where safety depends on environmental claims
- [ ] Cross-model review pipeline (§11): generator = one provider, cold reviewer = the other (does not see generator's rationale). Both must agree "code is actually safe" for acceptance.
- [ ] Scott + Opus final adjudication on every accepted example (15–30 min per example, not a 15% spot-check)
- [ ] Scott + Opus review on 100% of model disagreements, including reject reasoning
- [ ] **External reviewer**: at least one external security professional reviews a 10% random sample (~10 examples) before public release. If no external reviewer available, dataset card explicitly discloses single-author review
- [ ] Turn 2 of every example includes the "what would make this unsafe" section
- [ ] Per-pattern disagreement rate logged; any pattern >30% disagreement either escalated to full human re-review or dropped from release
- [ ] **FP-rate reduction**: ≥30% relative reduction on the Task 2.3 eval baseline after fine-tuning with negatives folded in (target — published actual numbers regardless)
- [ ] **FN-rate regression check**: absolute FN-rate increase ≤5% on the same eval. *No silent regression on detecting real vulnerabilities.*
- [ ] **HF strategy**: opt-in `safe_controls` config only. Default `train`/`validation`/`test` splits unchanged from v2.1.
- [ ] Reject-reason log published for every rejected candidate example (provenance system, see §11.2)

### Effort (revised after external review)

External reviewer noted prior estimates were 30–50% optimistic. Revised:

- **Task 2.1** Generation harness (shared infrastructure, see §11): 25 hours
- **Task 2.2** Evidence-based pattern selection (was 10 hr; revised): **20 hours** — sourcing 500 functions, scoring across 8 models, clustering, documenting
- **Task 2.3** FP/FN-rate eval baseline (was 6 hr; revised): **12 hours** — curating with leakage controls, repeatability protocol, baseline measurement
- **Task 2.4** Negatives generation + adjudication:
  - Pattern taxonomy + Turn 2 template (post-data): 6 hours
  - Schema extension (`metadata.example_type`): 4 hours
  - Cross-provider generation + cold-review runs: 15 hours human oversight
  - Scott + Opus final adjudication (~20 min × 100 examples; revised from 5 min × 150): **35 hours**
  - External reviewer coordination + sample review: 10 hours
  - Apply corrections + parquet rebuild: 6 hours
- Post-fine-tune FP/FN measurement + delta publication: 12 hours
- **Total: ~145 hours** (up from 120)

### Risk

**Still the highest-risk upgrade.** A negative example that ships a real vulnerability poisons downstream models into thinking the bug is safe.

Mitigations now in place:
1. **Machine-checkable safety only** — no patterns where safety depends on environmental claims
2. **Cold cross-model review** — reviewer doesn't see generator's rationale, breaks anchoring
3. **Scott + Opus full adjudication** — every example, not spot-check
4. **External reviewer 10% sample** — third-party validation
5. **FN-regression measurement** — explicit guard against teaching the model to excuse vulnerabilities
6. **Opt-in only** — users on `main` see no change; only users who opt in get negatives
7. **Reject-reason log** — transparent record of what was rejected and why
8. **Pattern-level kill switch** — if a pattern can't be made safe without environmental assumptions, drop the pattern (already applied to 5 of original 15)

---

## 5. Spec: Phase 3 — `securecode-infra` v0.1 (NEW SIBLING DATASET)

### Rationale

Critical assessment finding: scoping Phase 3 as "v2.3 IaC inside Web" was wrong. Two reasons.

First, IaC and CI/CD security are qualitatively different from web/application security. Different audiences (cloud security engineers vs. app sec engineers), different tooling (Checkov/tfsec/Falco vs. SAST/DAST), different threat models. Folding them into Web muddies the dataset's identity and makes both audiences' filtering harder.

Second, the original 80-example scope (40 Terraform + 40 Kubernetes) missed where 2024–2025 breaches actually live: **CI/CD pipelines and supply chain.** XZ Utils backdoor (CVE-2024-3094), Polyfill.io supply chain compromise, GitHub Actions runner attacks via `pull_request_target`, malicious npm packages, dependency confusion, lockfile tampering. None of that fits Terraform or K8s manifests.

**Decision:** ship as a new sibling dataset `scthornton/securecode-infra`, expanding scope to 90 examples covering Terraform, Kubernetes, *and* CI/CD + supply chain. Pattern matches the existing sibling structure (`securecode-web`, `securecode-aiml`, and now `securecode-infra`).

### Content design

**Target: 90 examples across three categories (30 each).**

#### Terraform (30 examples)

Coverage roughly across AWS (15), GCP (8), Azure (7):

- S3 / GCS / Blob Storage public exposure + encryption misconfig
- Overly-permissive IAM policies (`*` actions, cross-account trust, wildcard principals)
- Security groups / firewall rules open to internet on sensitive ports
- Missing encryption at rest (RDS, EBS, EFS, managed databases)
- Hardcoded secrets in `*.tf` variables or `*.tfstate` files
- Unrestricted egress in private subnets
- Missing logging (CloudTrail, flow logs, audit logs)
- KMS key policies with overly broad principals
- Public subnets for databases
- Default VPC / default security group usage
- Cross-account role assumption with overly broad trust policy

#### Kubernetes (30 examples)

- Privileged containers / `hostNetwork` / `hostPID`
- Missing NetworkPolicies (default allow-all)
- Over-permissive RBAC (ClusterRoleBinding to default ServiceAccount)
- Secret mounting patterns (env var leakage vs. projected volumes)
- Exposed kubelet / metrics / debug endpoints
- Missing PodSecurityStandards / PSA enforcement
- Insecure ingress TLS termination
- Image pull from public registries without signature verification (cosign / sigstore)
- Missing resource limits (DoS enabler via OOM cascade)
- ServiceAccount token auto-mounting
- `imagePullPolicy: Always` for security-critical images
- Helm chart templating injection

#### CI/CD + npm supply chain (30 examples) — *narrowed for v0.1 after external review*

Original scope was "all CI/CD platforms + all package ecosystems." External reviewer correctly flagged this as too broad for 90 examples total. **v0.1 narrows to GitHub Actions + npm only** — these are the highest-volume targets and where 2024–2025 attacks concentrated. GitLab CI, Jenkins, Cargo, Go modules defer to v0.2.

**GitHub Actions (~18 examples):**
- Injection via untrusted PR titles / branch names interpolated into shell
- `pull_request_target` token exposure on fork PRs
- Secret exfiltration via fork PRs
- `permissions: write-all` and missing `permissions:` blocks
- Unpinned action versions (`actions/checkout@main`)
- Self-hosted runner abuse — runners reused across untrusted PRs
- Workflow command injection via `::set-output::`
- Reusable workflow privilege issues
- Container registry credential exposure in workflows

**npm supply chain (~12 examples):**
- Dependency confusion — internal package names on public registry
- Malicious `postinstall` scripts that exfiltrate
- Typosquatting attacks (`expresss`, `loadash`, etc.)
- Lockfile tampering — modified `package-lock.json` introducing transitive deps
- Unverified `curl | sh` install steps
- Missing `npm audit` enforcement / outdated `--audit-level` thresholds
- Compromised maintainer accounts (event-stream-style hijacks)
- Pre-commit hook attacks via shared `husky` configs
- Lack of SLSA provenance verification on dependencies

**Deferred to v0.2** (acknowledged but not in v0.1):
- GitLab CI pipeline-as-code injection
- Jenkins script approval bypass
- Cargo (Rust) supply chain — proc-macros, build.rs
- Go modules supply chain
- Container registry attacks (tag mutability, registry credential reuse) beyond what npm covers
- Build-system supply chain (XZ Utils style — compromised compiler tooling)

The narrowing keeps v0.1 deliverable on the 30-example budget without sacrificing relevance. v0.2 can add the deferred set once v0.1 proves the methodology.

### Example structure

Same 4-turn structure. Turn 1 presents the config or pipeline, Turn 2 shows vulnerable and secure variants, Turn 3 asks about scale/production hardening, Turn 4 covers detection (cloud-native tools + supply-chain tools: AWS Config, GCP SCC, Falco, kube-bench, Checkov, tfsec, sigstore/cosign, OSV, Dependabot, GitHub `secret_scanning`, GitGuardian).

### Repository structure (new sibling)

```
github.com/scthornton/securecode-infra/      ◀── new GitHub repo
huggingface.co/datasets/scthornton/securecode-infra  ◀── new HF dataset

securecode-infra/
├── README.md           (dataset card following Web's structure)
├── CONTRIBUTING.md     (mirrors Web's; updated for IaC tone)
├── schema.json         (extends Web's with IaC-specific fields)
├── taxonomy.yaml       (sibling-specific taxonomy)
├── scripts/
│   ├── enrich_metadata.py     (forked from Web Phase 1)
│   ├── generate.py            (forked from Web Phase 2 harness)
│   └── validate_compliance.py (adapted from Web)
├── data/
│   ├── terraform-*.jsonl
│   ├── kubernetes-*.jsonl
│   ├── cicd-*.jsonl
│   ├── supply_chain-*.jsonl
│   └── *.parquet
└── docs/
    ├── DETECTION_RULES.md
    └── INCIDENT_LIBRARY.md
```

### Schema changes

Sibling extends Web's schema with `metadata.platform` (`terraform-aws`, `kubernetes`, `github-actions`, `gitlab-ci`, etc.) and `metadata.detection_tool_id` (`checkov:CKV_AWS_20`, `falco:rule_name`, etc.). Reuses Web's `metadata.example_type` field.

### HF strategy

Standalone HF dataset with own train/val/test splits. Suggested initial split: 72/9/9.

The unified `scthornton/securecode` dataset (currently 2,185 examples = web + aiml) gets a config update to optionally include `securecode-infra` content, but that lands in a separate housekeeping release.

### Acceptance criteria

- [ ] 30 Terraform + 30 Kubernetes + 30 CI/CD examples (90 total)
- [ ] Each example references a real incident or CVE
- [ ] Each example includes a corresponding detection-rule reference
- [ ] At least 8 examples cite 2024–2025 vintage incidents (XZ, Polyfill, regreSSHion, Ivanti, Palo Alto GlobalProtect, etc.)
- [ ] Single Scott-Opus review pass per example (lower bar than negatives — these are mechanical patterns)
- [ ] Sibling repo published on both GitHub and HF
- [ ] README cross-references between Web and Infra siblings

### Effort

- Sibling repo bootstrap (fork tooling from Web): 8 hours
- Incident library + taxonomy: 8 hours
- Terraform generation + review: 18 hours
- Kubernetes generation + review: 18 hours
- CI/CD + supply chain generation + review: 18 hours
- Detection-rule authoring across all 90: 6 hours
- README + parquet build: 4 hours
- **Total: ~80 hours**

### Risk

Low-to-medium. Config patterns age (cloud APIs change) — mitigate with `metadata.created` per example and annual refresh commits. CI/CD patterns may age fastest as platforms evolve — accept this and version the dataset accordingly. The supply-chain section is genuinely new content that doesn't exist anywhere else; that's where the credibility win comes from.

---

## 6. Spec: v2.4 — Executable Verification PILOT (Phase 4)

### Rationale

This is the dataset's actual differentiator vs. competitors. Every other "secure code" dataset claims rigorous validation; none ship reproducible proof. v2.4 makes "validated" mean *exploited and verified-fixed*, not *human read it*.

The mechanism: ship a Dockerfile + exploit script + verification harness for selected critical examples. The harness:
1. Builds a container with the *vulnerable* code from the example
2. Runs the documented exploit; verifies it succeeds (e.g., extracts a flag, returns sensitive data, gains shell)
3. Builds a second container with the *secure* code from the example
4. Runs the same exploit; verifies it fails

Output: `validation.code_execution: passed` is no longer a human attestation — it's a CI-checked, reproducible-by-anyone claim. Anyone can `git clone && docker compose up && ./run-verification.sh` and confirm.

### Why a pilot (revised after external review)

Original plan: 50 examples in Phase 4. External reviewer correctly noted this was too aggressive as a first commitment. Many bug classes (Java/Spring deserialization, complex SSRF chains, auth-flow exploits) take half a day or more to verify properly — not the 80 minutes I'd estimated for the average case. CI runtime for 50 verifications under 15 minutes is also aggressive.

**Revised scope: 10–15 example pilot in Phase 4.** Pilot proves out the per-example template, Docker boundary patterns, exploit-drift handling, and CI runtime budget. Phase 4.5 (v2.5) scales to 50 once the pilot exposes the real per-example cost.

**This is also better strategy.** A 10-example "Reproducibly Verified Subset" is more compelling than 50 hastily-built ones. Quality over quantity for the pilot release.

### Content design

**Target: 12 examples (3 per major bug class) for the pilot.** All CRITICAL severity, all CVE-backed, all locally exploitable.

Pilot distribution:
- **SQL Injection** (3 examples — easy bug class to verify; calibration anchor): one Python/Flask, one Node/Express, one Java/Spring
- **Command Injection** (3 examples): cross same three stacks
- **SSRF** (2 examples): Python and Node
- **XSS — stored** (2 examples): React + Django
- **JWT auth bypass** (2 examples): Express + FastAPI

Why this distribution:
- 3 SQLi serves as cross-language calibration — same bug class, three stacks; surfaces stack-specific Docker challenges early
- Command injection is reliably local (no external services needed)
- SSRF stretches to test network-isolation patterns (need a fake "internal" service in compose)
- Stored XSS exercises persistence — the verification needs to write+read state
- JWT auth bypass exercises auth-flow verification — non-trivial, calibrates whether we can handle auth examples at all

Hard exclusions for the pilot:
- No Java deserialization (high effort, defer to v2.5)
- No XXE (XML parser config drift makes long-term repro fragile)
- No race conditions / TOCTOU (timing-based exploits are unreliable in CI)

These re-enter scope in v2.5 with lessons learned from the pilot.

### Per-example structure

Each verified example gets a `verification/` subdirectory:

```
verification/
└── express_js-injection-sql-000001/
    ├── README.md              (what this verifies, how to run)
    ├── docker-compose.yml     (vulnerable + secure services)
    ├── vulnerable/
    │   ├── Dockerfile
    │   ├── app.js             (extracted from example's Turn 2 vulnerable code)
    │   └── ...
    ├── secure/
    │   ├── Dockerfile
    │   ├── app.js             (extracted from example's Turn 2 secure code)
    │   └── ...
    ├── exploit.sh             (the attack — must succeed against vulnerable, fail against secure)
    └── verify.sh              (runs both; exits 0 on correct outcome, 1 on regression)
```

`verify.sh` is the contract. CI on every PR runs `verify.sh` for every verified example. A regression (exploit no longer works against vulnerable code, OR exploit succeeds against secure code) blocks merge.

### Schema changes

Add `validation.execution_proof` to extend the existing `validation` block:

```json
{
  "validation": {
    "code_execution": "passed",
    "execution_proof": {
      "verification_path": "verification/express_js-injection-sql-000001/",
      "vulnerable_exploit_succeeded": true,
      "secure_exploit_failed": true,
      "ci_run_id": "github-actions-run-12345",
      "verified_date": "2026-09-15"
    }
  }
}
```

### Workflow (pilot)

1. **Pick the 12 examples** (1 day with Scott)
2. **Per-example template authoring** (~30 min): vulnerable Dockerfile, secure Dockerfile, common docker-compose. Some pilot examples will need iteration on the template — budget for it.
3. **Per-example verification authoring** (~2 hr average for the pilot): write the exploit script, write the verify.sh, test locally. Some examples (JWT auth bypass, SSRF with fake internal service) will take 4+ hours; SQLi will take ~1 hour. Budgeting **2 hr average** for the 12, not the 80 min that overestimated for the original 50.
4. **CI integration**: GitHub Actions workflow that runs `verify.sh` on every PR affecting `verification/`. Aggressive layer caching. Run all 12 in parallel matrix.
5. **Pilot retrospective** (~6 hr): document what took longer than expected, where Docker patterns broke down, exploit-drift catches over the 8-week pilot run. Output: `docs/EXEC_VERIFICATION_PILOT_LESSONS.md`. This is what Phase 4.5 (v2.5) scales from.
6. **README integration**: list verified examples prominently with a badge. Be explicit that "verified" means "documented exploit works against vulnerable, fails against secure" — *not* "secure code has no bugs."

### Acceptance criteria

- [ ] 12 examples have full `verification/` subdirectories
- [ ] All 12 pass `verify.sh` locally and in CI
- [ ] CI workflow runs all 12 in <8 minutes (pilot scope; full 50 would target <20 min after lessons)
- [ ] Exploit scripts use minimal dependencies
- [ ] At least one external user has reproduced verification on their own machine
- [ ] README "Verified Examples" section + dataset-card prominent placement
- [ ] **Explicit disclaimer**: "verified" means "documented exploit works against vulnerable code, fails against secure code." It does NOT mean the secure code is bug-free.
- [ ] **Pilot lessons doc** published — what surprised us, where the template broke, which patterns we'd change for v2.5

### Effort (revised after external review)

- Selection + planning: 8 hours (with Scott)
- Docker harness template + docker-compose pattern: 16 hours (more iteration than originally budgeted)
- Per-example verification (12 × 2 hr average): 24 hours
- CI integration (GitHub Actions, layer caching, parallelization): 12 hours
- `validation.execution_proof` schema rollout: 4 hours (smaller surface for pilot)
- README + release notes + dataset card update: 6 hours
- Pilot lessons documentation: 6 hours
- End-to-end pipeline test: 8 hours
- **Total pilot: ~85 hours** (down from 120 — and the count is honest now)

**Phase 4.5 (v2.5) scaling estimate** based on pilot averages will be set after the pilot retrospective. Rough placeholder: ~150 hours to scale from 12 → 50 examples, but this is a *projection* and will be re-baselined post-pilot.

### Risk

- **Exploit drift** (unchanged): pin image base versions; CI regularly re-runs; quarterly review.
- **Misleading "verified" implication**: addressed via explicit disclaimer (see acceptance).
- **CI cost / time**: pilot scope of 12 keeps CI minutes manageable. Scaling decisions deferred to v2.5.
- **Pilot fails to scale**: if the pilot reveals per-example effort is way higher than projected (e.g., averaging 6+ hr instead of 2 hr), we may *cap v2.5 at 25 examples* rather than 50. Pilot lessons doc captures whether scaling is feasible.

### Why this earns the differentiator label

Run a search across HuggingFace for security-code datasets. None ship reproducible exploit + fix verification. The closest analog is academic CTF challenge sets, which are not training data. SecureCode v2.4 (pilot) would be the first production-grade fine-tuning dataset where "validated" means CI-reproducible — even at 12 examples.

That's a citation magnet. That's a paper. That's a methodology other datasets will copy.

---

## 7. Spec: Phase 5 (deferred) — v3.0 Agentic Review Loops

### Status: deferred 6 months from Phase 4 ship date — go/no-go decision required

**Critical assessment finding (incorporated 2026-04-24):** v3.0 is a 320-hour bet on a format nobody has yet proven helps fine-tuning. No major actor (Anthropic, OpenAI, Cursor, Cline, Aider, Copilot Workspace, Continue.dev) has published "we fine-tuned on agentic-loop data and observed measurable downstream improvement." Building a 200-example dataset for an unproven format risks shipping a configuration nobody adopts.

### Decision criteria (must be met before invoking `execute phase 5`)

At least **one** of the following:

1. A major coding-agent framework (Claude Code, Cursor, Cline, Aider, Copilot Workspace, Continue, etc.) publishes fine-tuning results showing measurable improvement from agentic-loop training data.
2. A peer-reviewed paper or industry-standard benchmark for "agentic code review quality" emerges that we'd want to evaluate against.
3. A canonical schema for multi-agent code review sequences becomes a de facto standard (e.g., LangGraph, OpenAI Assistants, Anthropic tool-use patterns) — meaning our schema would align with existing tooling rather than diverge.

If none of those happen by 6 months after Phase 4 ships, **skip Phase 5** and reallocate the budget to:
- Expanding executable verification (v2.5 = next 100 examples) — *proven differentiator, just scale it*
- Or other high-value gaps from §15 (API Top 10, mobile, cross-language attack chains)

### Rationale (if pursued)

Industry is shifting from single-turn code generation to agent-driven workflows: a writer agent produces code, a reviewer agent critiques it, the writer revises. Claude Code, Cursor agents, Copilot Workspace all fit this pattern. A dataset that only trains single-assistant Q&A is increasingly off-trend. Agentic track gives users training data for the review-loop pattern specifically.

### Content design

**Target: 200 examples as a v3.0 preview, with 500 as the eventual goal.**

Each example is a 6–10 turn sequence across 3–4 roles:

- `user` — human developer (1 turn at start, often 1 closing)
- `writer_agent` — produces code
- `reviewer_agent` — performs security review, flags issues
- `tester_agent` (optional) — writes exploit PoC, confirms fix blocks it

### Loop pattern taxonomy (15 patterns, 12–15 examples each)

**Catch-and-fix loops:**
1. Writer produces vuln → Reviewer flags → Writer fixes → Reviewer approves.
2. Writer produces vuln → Reviewer flags → Writer pushes back → Reviewer justifies with CVE reference → Writer fixes.
3. Writer produces vuln → Reviewer misses it → User catches in Turn N → Writer fixes. *(trains humility)*

**Refusal-and-escalation loops:**
4. Writer refuses unsafe request → Reviewer confirms refusal is correct → Writer offers safe alternative.
5. Writer produces code → Reviewer flags that the *request itself* is a security anti-pattern → Writer escalates to user for requirement change.

**Edge-case-probe loops:**
6. Writer produces code → Reviewer asks about specific preconditions → Writer confirms/denies → Reviewer approves or requires hardening.
7. Writer produces code → Tester produces exploit → Fix required → Tester re-tests.

**Architectural loops:**
8. Writer produces single-file solution → Reviewer notes missing defense-in-depth → Writer expands to multi-layer.
9. Writer produces code → Reviewer flags threat model mismatch → User clarifies threat model → Writer revises.

**Disagreement loops:**
10. Reviewer flags false positive → Writer pushes back with context → Reviewer retracts.
11. Writer produces code → Reviewer and Tester disagree on severity → User resolves.

**Multi-round loops:**
12. Writer → Reviewer → Writer → Reviewer (3+ iteration cycles with specific remaining issues each round).

**Meta loops:**
13. Writer writes the review criteria first, Reviewer validates criteria, then Writer writes code against validated criteria.
14. Reviewer catches the same bug class recurring across multiple writer outputs; recommends a code-generation-time guardrail.

**Safe-acceptance loops (pairs with v2.2):**
15. Writer produces code that *looks* unsafe → Reviewer confirms it's fine → Tester validates → all agree.

### Schema changes

Extend `from` enum in `conversations[].from`:

```json
{
  "from": {
    "type": "string",
    "enum": ["human", "assistant", "user", "writer_agent", "reviewer_agent", "tester_agent", "system"]
  }
}
```

`human` and `assistant` retained for 4-turn backward compat. `user` is the agentic-era equivalent. Add `metadata.format`:

```json
{
  "metadata": {
    "format": "classic_4turn"
  }
}
```

Enum: `"classic_4turn"` | `"agentic_loop"`. Default `"classic_4turn"` for all existing examples.

Add optional `agentic_metadata` sibling to `metadata`:

```json
{
  "agentic_metadata": {
    "loop_pattern": "catch_and_fix",
    "turn_count": 8,
    "agents_involved": ["writer_agent", "reviewer_agent"],
    "terminal_state": "approved"
  }
}
```

`terminal_state` enum: `approved` | `refused` | `escalated_to_user` | `unresolved_disagreement`.

### HF config strategy

Ship as **separate HF config**, not a new split in default:

```yaml
configs:
  - config_name: default
    data_files: [same as today]
  - config_name: agentic
    data_files:
      - split: train
        path: data/agentic-train-00000-of-00001.parquet
      - split: validation
        path: data/agentic-validation-00000-of-00001.parquet
      - split: test
        path: data/agentic-test-00000-of-00001.parquet
```

Users opt in with `load_dataset("scthornton/securecode-web", "agentic")`. Classic consumers see zero change.

Proposed split: 160/20/20 for the 200-example preview. Scale proportionally at 500.

### ID scheme

`agentic-<pattern>-<lang>-<NNNNNN>`

Examples: `agentic-catch_and_fix-python-000001`, `agentic-refusal_escalation-javascript-000017`.

### Example structure (illustrative)

```json
{
  "id": "agentic-catch_and_fix-python-000001",
  "metadata": {
    "format": "agentic_loop",
    "lang": "python",
    "category": "injection",
    "subcategory": "sql_injection",
    "example_type": "vulnerability",
    ...
  },
  "agentic_metadata": {
    "loop_pattern": "catch_and_fix",
    "turn_count": 7,
    "agents_involved": ["writer_agent", "reviewer_agent"],
    "terminal_state": "approved"
  },
  "conversations": [
    {"turn": 1, "from": "user", "value": "Build me a user search endpoint in Flask."},
    {"turn": 2, "from": "writer_agent", "value": "[produces code with f-string SQL]"},
    {"turn": 3, "from": "reviewer_agent", "value": "I see a SQL injection in line 12. The f-string builds the query from user input without parameterization. Reference: CWE-89. Please use parameterized queries."},
    {"turn": 4, "from": "writer_agent", "value": "[revised code with ? placeholders]"},
    {"turn": 5, "from": "reviewer_agent", "value": "Parameterization looks correct. One remaining issue: no length limit on the search term, enables DoS via large LIKE scans. Recommend cap at 100 chars and index the column."},
    {"turn": 6, "from": "writer_agent", "value": "[adds length validation + mentions index creation]"},
    {"turn": 7, "from": "reviewer_agent", "value": "Approved. Summary of what changed: parameterization (SQLi fix), input length cap (DoS mitigation), recommended index (performance)."}
  ]
}
```

### Acceptance criteria

- [ ] 200 examples across 15 loop patterns, minimum 10 per pattern
- [ ] Each example has `agentic_metadata` fully populated
- [ ] Terminal state is always one of the 4 enum values (no dangling loops)
- [ ] At least 30 examples reach `terminal_state: approved` via 3+ iteration rounds (multi-round evidence)
- [ ] At least 20 examples have `tester_agent` involvement with an exploit + verified fix
- [ ] HF `agentic` config loads cleanly and is separate from default config
- [ ] Existing `default` config users see zero change

### Effort

- Schema design + HF config + docs: 20 hours
- Pattern taxonomy + "voice bible" per agent role: 15 hours
- Harness extension for multi-role cross-provider routing (builds on shared harness from §11): 10 hours
- Generation (cross-model, writer on one provider / reviewer on the other): ~50 min × 200 = 167 hours author oversight
- Author review: ~15 min × 200 = 50 hours
- Agentic eval harness build (no existing harness — open question #3): 40 hours
- Fine-tune one existing model on agentic track + produce before/after metrics: 15 hours (compute cost not included)
- Parquet build for new config: 6 hours
- **Total: ~320 hours**

(Includes the eval harness build that was previously deferred. The eval is part of v3.0 acceptance — without it, "we shipped an agentic track" is a claim with no evidence of utility.)

### Risk

- **Format risk.** Industry agentic conventions are still settling in 2026. This schema might not match where the field lands. Mitigate by shipping as v3.0 *preview*, explicitly marked as a format that may evolve, with semver-style versioning on the agentic config.
- **Quality risk.** Long sequences amplify small voice inconsistencies. Mitigate with a "voice bible" doc per agent role that authors/LLM prompts reference.
- **Utility risk.** Nobody fine-tunes on this yet, so there's no proof training helps. Mitigate by fine-tuning one of your existing 8 models on the agentic track and publishing before/after on an agentic eval.

---

## 8. Risk register

| Risk | Severity | Likelihood | Mitigation |
|---|---|---|---|
| Negative example actually ships a real bug | Critical | Low (after multi-layer review) | Multi-layer review: cold cross-model review + Scott/Opus adjudication on every example + external reviewer 10% sample. Pattern-level kill switch: drop categories where safety isn't machine-checkable in code. Reject-reason log published. |
| Cross-model review collusion (both miss same bug) | High | Medium | Scott/Opus adjudication breaks the correlation; external reviewer is the third independent check. Per-pattern disagreement-rate tracking surfaces categories where models agree too easily. |
| Negatives default-mix surprises users mid-training | High | Eliminated | Negatives ship as opt-in `safe_controls` config only. Default `train`/`val`/`test` splits unchanged. |
| FN-rate regression — model trained on negatives starts excusing real vulns | High | Medium | Task 2.3 baseline measures FN rate before; post-fine-tune protocol measures after. Hard ≤5% increase tolerance. Don't ship if exceeded. |
| External reviewer unavailable for v2.2 | Medium | Medium | Dataset card explicitly discloses single-author review. Honest framing beats false claims. Reach out to candidates before Phase 2 starts. |
| EPSS/CVSS data goes stale between releases | Medium | High | Quarterly scheduled refresh (v2.1.x). Confidence/source markers make staleness visible to users. |
| Derived metadata (ATT&CK/CAPEC) treated as authoritative | Medium | Medium | `*_source` and `*_confidence` markers on every derived field. README explicitly documents heuristic vs measured distinction. |
| OWASP 2025 migration breaks downstream pipelines | High | Eliminated | Non-breaking dual-field migration. `owasp_2021` preserved as `owasp_2021_legacy`. |
| Phase 4 verification scaling fails | Medium | Medium | Pilot scope of 12 limits exposure. v2.5 scaling decision deferred to post-pilot retrospective. |
| Phase 4 exploit drift (works today, fails in 6 months) | Medium | High | Pin Docker image base versions. CI re-runs verifications regularly. Quarterly review. |
| Agentic schema diverges from industry convention | High | High | Decision deferred 6 months with explicit go/no-go criteria (§7). Skip if criteria not met. |
| Parquet rebuild drops or duplicates examples | High | Low | Reuse `deduplicate_and_resplit.py` + `split_leakage_check.py`; pre/post count assertions in rebuild. |
| OpenAI or Anthropic API outage during generation sprint | Low | Medium | Harness supports single-provider fallback mode; log degraded-mode examples for re-review. |
| License (CC BY-NC-SA) blocks downstream commercial adoption indefinitely | High | High until decided | §15 license strategy. Decision required before v2.4 ships. |
| Roadmap contradictions cause execution drift | Medium | Eliminated | This roadmap revision pass reconciled stale sections. METHODOLOGY.md aligned with current ROADMAP.md. |

---

## 9. Resolved decisions (was: open questions)

1. **Parquet rebuild automation — exists.** `deduplicate_and_resplit.py` on the GitHub repo handles content-hash dedup and CVE/incident grouping to prevent split leakage. `split_leakage_check.py` validates the output. Reuse these for v2.1+ rebuilds. No additional infra needed.
2. **Multi-layer review architecture (revised after external review):** cross-model review (Anthropic + OpenAI, with cold reviewer not seeing generator's rationale) PLUS Scott + Opus 4.7 adjudication on every accepted example PLUS external security professional reviewing 10% random sample before v2.2 public release. See §11 for the pipeline design. The external reviewer is a recruitment action item before Phase 2 starts; if no external reviewer is available, dataset card discloses single-author review.
3. **Agentic eval harness — does not exist.** Must be built as part of v3.0. **+40 hours added to v3.0 effort.**
4. **Versioning — semver.** Use `v2.1`, `v2.2`, `v2.3`, `v3.0`. Date-tagged versions (e.g. `2026.04`) are a secondary label in README release notes only.
5. **Negatives mix strategy — opt-in only (revised after external review).** Ship as separate `safe_controls` HF config. Default `train`/`val`/`test` unchanged. Default-mixing reconsidered only after measured FP-reduction + FN-non-regression on a fine-tuned model. (Originally was Option C: mix into default + expose as filter. Reversed because default-mixing silently changes training behavior for users who auto-load `main`.)

---

## 10. Prerequisite — reconcile OWASP 2021 vs 2025 drift

**Blocker for v2.1 and all subsequent work.** GitHub and Hugging Face are diverged:

| Surface | Baseline | Count | OWASP version |
|---|---|---|---|
| Hugging Face `scthornton/securecode-web` | 1,378 examples | 1,378 | 2021 (`owasp_2021` field) |
| GitHub `scthornton/securecode-web` | 1,215 examples | 1,215 | 2025 (migration scripts + `schema_v2.json`) |

GitHub has migration tooling (`scripts/migrate_owasp_2025.py`) that maps 2021 categories to 2025 (SSRF merged into Broken Access Control, Vulnerable Components renamed to Software Supply Chain Failures, etc.) but the migrated content has never been published to HF. HF still ships 2021 + 219 framework additions that GitHub lacks.

### Three reconciliation paths

**Path A — HF is canonical, roll back GitHub.** Treat the GitHub 2025 migration as a stale experiment. Delete `schema_v2.json` and the migration scripts, push HF's 1,378-example 2021 baseline to GitHub as source of truth. Lowest cost: ~4 hours. Risk: you lose the 2025 migration work.

**Path B — GitHub is canonical, re-migrate HF.** Run the OWASP 2025 migration on the full HF 1,378-example baseline (baseline + framework additions), push to HF as v2.1.0 (or v2.0.1), then build upgrades on top. Cost: ~12 hours including QA. Risk: breaking change for downstream users already on the `owasp_2021` field.

**Path C — Maintain both, ship 2025 as new config.** Keep default config on 2021 for backward compat; add an `owasp_2025` HF config that exposes the migrated view. Cost: ~8 hours. Risk: doubles maintenance surface going forward.

### Recommendation

**Path B, gated on OWASP 2025 Top 10 being officially published.** Verify the 2025 list is final (not draft) before migrating. If 2025 is still draft, go Path A and revisit when final. Either way, resolve this before v2.1 enrichment starts — you do not want to enrich metadata against a taxonomy that's about to change.

### Effort impact

- Path A: +4 hours before v2.1 starts
- Path B: +12 hours + ~1 week for downstream user communication
- Path C: +8 hours, ongoing +10% maintenance overhead

---

## 11. Generation pipeline (cross-model review + Scott/Opus adjudication)

**Architecture decision (2026-04-24, revised after external review 2026-04-24):** Both layers, not one or the other. Single-pass + Scott/Opus alone is too dependent on one author using one model-assisted workflow — vulnerable to anchoring, batch fatigue, shared blind spots, and template-replicated mistakes.

**Five roles in the pipeline:**

1. **Generator (automated)** — Provider A (Sonnet 4.6 or GPT-5.4, alternating per example) drafts the example.
2. **Cold reviewer (automated)** — Provider B (the *other* provider) independently evaluates the generated code. Sees only the code, not the generator's rationale. Job: try to exploit the code, document the exploit path if any.
3. **Local validation (automated)** — Gemma 4 26B-A4B + deterministic Python/regex validators check structure, schema conformance, and basic semantic sanity.
4. **Final adjudicator (Scott + Opus 4.7)** — Scott reads each batch in a Claude Code session with Opus 4.7 as his review assistant. Opus helps verify safety claims, identify subtle issues, suggest corrections, apply fixes. **Scott is the accountable reviewer; Opus is his tool.** Adjudicates accepted examples, all model disagreements, and all high-risk pattern categories.
5. **Deterministic gates (final)** — `validate_contributing_compliance_v2.py` and `split_leakage_check.py` enforce structural and split-integrity rules before parquet rebuild.

### Reviewer's recommended framing (adopted verbatim)

> Automated cross-model review is a triage and adversarial-review layer for safety-critical generated content. Scott performs final adjudication with Opus assistance for accepted safety-critical examples, all model disagreements, and all high-risk pattern categories. Deterministic validators and release evals remain required final gates.

### Why both layers (not one)

The failure modes Scott + Opus alone doesn't address:

- **Reviewer anchoring** — Opus seeing the generator's "this is safe because…" prose biases toward accepting it
- **Batch fatigue** — at 150 examples, attention degrades; cross-model adversarial pass catches what tired review misses
- **Shared blind spots** — Sonnet generator + Opus review (same model family) miss the same subtle bugs; GPT-5.4 cold reviewer breaks that correlation
- **Template-level mistakes** — a flawed prompt template produces 20 flawed examples; cold reviewer catches the systematic issue
- **"Safe because of precondition"** — adversarial reviewer specifically tests whether the precondition holds, not whether the prose explains it well
- **Generated prose laundering unsafe patterns** — review must read code, not explanations

### Acceptance pipeline for safety-critical content (v2.2 negatives)

```
1. Generator (Provider A) drafts example
2. Cold reviewer (Provider B) attempts exploit
3. Deterministic validators (schema, structure, CVE format)
4. Decision branch:
   - Both models agree "safe" + validators pass → queue for Scott/Opus final review
   - Reviewer finds exploit path → reject, log reason, return to generator
   - Models disagree → flag as disagreement, escalate to full Scott/Opus review
5. Scott/Opus final adjudication (all accepted + all disagreements + all high-risk-pattern examples)
6. Approved examples → fold into dataset
7. External reviewer sample (10% random) before public release
```

**Cold-reviewer prompt design.** Reviewer must not see the generator's Turn 2 explanation. Reviewer gets only: the code, the example's category claim, and the question "is this code exploitable as written? Provide concrete exploit if yes." This breaks the anchoring effect.

### Provider alternation purpose (revised)

Sonnet 4.6 and GPT-5.4 each generate ~50% of examples — for **both voice diversity and adversarial coverage.** Downstream models see two generation styles, *and* every example was independently exploit-tested by the opposite provider. Cost parity ($2.50–3 input, $15 output per 1M tokens for both) keeps routing simple.

### Cost impact of the revised architecture

Cross-model review adds back a reviewer-role API call per example. Updated projections:

| Phase | Pipeline cloud $ | External reviewer $ | Scott's Opus review $ | Total |
|---|---|---|---|---|
| v2.1 | $0 | $0 | ~$5 | ~$5 |
| v2.2 | ~$60 (gen + cold review, batched) | ~$50 (10% sample, paid 1 reviewer) | ~$60 (15-30 min × 150 with Opus) | ~$170 |
| infra v0.1 | ~$30 (gen + cold review on 20% sample) | $0 | ~$25 | ~$55 |
| v2.4 (10–15 pilot) | ~$5 | $0 | ~$5 | ~$10 |
| Total Phases 1–4 | ~$95 | ~$50 | ~$95 | **~$240** |
| (v3.0 if pursued) | ~$140 | ~$100 | ~$120 | ~$360 |

Up from ~$190 in the prior framing, but the quality bar is now defensible. This is the right trade.

### Roles per provider

Different releases use the split differently. What's consistent: **the generator and the reviewer are always different providers.**

#### v2.1 metadata enrichment
Pure automation — no LLM generation needed. APIs not used.

#### v2.2 safe-but-suspicious negatives

**Generator → Reviewer → Adjudicator** pipeline:

1. **Generator (Claude Opus or Sonnet)** drafts a candidate example: the "looks suspicious but is safe" code, the Turn 2 explanation including the "what would make this unsafe" section.
2. **Reviewer (GPT-4o or GPT-5)** independently evaluates: "Is this code actually safe? What's the exploit path if any?" Given only the code, not the generator's claim.
3. **Adjudicator logic (deterministic)**:
   - If Reviewer agrees the code is safe → accept, log agreement
   - If Reviewer finds a real exploit path → reject, feed back to Generator for revision
   - If Reviewer flags something debatable → queue for human spot-check
4. Author (Scott) spot-checks ~15% of accepted examples and 100% of disagreements.

Rationale: the failure mode for negatives is "ships a vuln labeled safe." A second model that didn't write the code has no stake in defending it.

#### v2.3 IaC deepening

Lower stakes than negatives — use split for cost balance and voice diversity:

- **~50% generated by Claude, ~50% by GPT.** Random assignment.
- **Cross-provider review on 20% random sample** (not all 80 — cost cap). The sample is primarily for voice-consistency QA, not safety (unlike negatives).

#### v3.0 agentic review loops

The pipeline itself benefits from provider diversity:

- **`writer_agent` role** → one provider (alternate per example: Claude half, GPT half)
- **`reviewer_agent` role** → the *other* provider for that example
- **`tester_agent` role** (where present) → either provider, randomly

This makes the dataset itself heterogeneous in a useful way: downstream models fine-tuned on it learn from two different "voices" of review, reducing overfit to a single model's review style. The 15-pattern taxonomy is enforced by the generation harness regardless of provider.

### Generation harness (new, to be built)

Deliverable: `scripts/generate.py` (new). Not currently in the repo.

Features:
- Provider abstraction (OpenAI SDK + Anthropic SDK behind a common interface)
- Role assignment per example (generator/reviewer/tester)
- Adjudication logic for negatives
- Token/cost tracking per provider per release
- Output validation (hits `validate_contributing_compliance_v2.py` before writing)
- Failure queueing for human review
- Deterministic seed + provider assignment logging for reproducibility

**Harness build effort: ~25 hours.** Shared across v2.2, v2.3, v3.0 (build once, reuse). Amortized: ~8 hours per release that uses it.

### Cost impact

Single-pass generation + Scott's Opus-assisted review eliminates reviewer-role calls and uses Batch API (50% off) for non-time-critical generation. Token caching on the system prompt amortizes ~10× across calls in a phase.

| Release | Pipeline cloud $ | Scott's Opus review tokens | Total |
|---|---|---|---|
| v2.1 | $0 (no generation) | ~$5 | ~$5 |
| v2.2 | ~$25 (batched) | ~$30 (150 examples × 5 min Opus review) | ~$55 |
| v2.3 | ~$12 (batched) | ~$15 (80 examples × 4 min) | ~$27 |
| v3.0 | ~$60 (batched, longer sequences) | ~$80 (200 × 10 min agentic review) | ~$140 |
| **Total** | **~$100** | **~$130** | **~$230** |

Down from $515 in the previous estimate. Cost is no longer the constraint — review time is. Phase 2 needs ~12 hours of focused Scott review; Phase 4 needs ~33 hours.

### Provider routing guidance

- **Claude (Opus/Sonnet)**: longer-form narrative, Turn 4 operational guidance, voice consistency across multi-turn sequences. Strongest where you want "explains its reasoning."
- **GPT (4o/5)**: structured output, JSON schema adherence, code correctness checks. Strongest where you want "finds the bug."

This is a generalization — the actual split is: *alternate assignments, don't pre-assume which model is better for which role.* The cross-model value comes from disagreement surfacing, and that only works if both are treated as equal-authority.

### Environment / secrets

Add to `.env.example` (new file):
```
OPENAI_API_KEY=sk-proj-...
ANTHROPIC_API_KEY=sk-ant-api-...
GEMMA_BASE_URL=http://localhost:8080/v1
GEMMA_MODEL=gemma-4-26B-A4B-it-Q8_0.gguf
SECURECODE_GENERATION_BUDGET_USD=50
SECURECODE_PROVIDER_SPLIT=0.5
```

Frontier keys already present in shell env (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`). Gemma 4 runs without auth on localhost. Budget guardrail halts cloud generation when exceeded; local tier has no cap.

### 11.1 Gemma 4 local tier — routing and integration

**Why add a local tier.** DGX Spark running Gemma 4 26B-A4B (MoE with ~4B active params) at Q8_0 quantization on `llama-server` provides an effectively-free, low-latency third tier. OpenAI-compatible API on `localhost:8080` means the existing `OpenAIProvider` class can target it with just a base-URL swap.

**What Gemma does:**

| Task | Rationale |
|---|---|
| Structural validation (4-turn ordering, required sections) | Pattern-matching; doesn't need frontier reasoning |
| Schema conformance checks beyond regex | Semantic "does this look right" pass |
| Triage: classifying outputs into pattern categories | Classification is Gemma's sweet spot |
| First-pass agentic-loop skeletons (Phase 4) | Structure is formulaic; frontier model refines |
| Commit message drafts from diffs | Low-stakes, high-volume |
| Progress log summarization | Daily rollups for `phase-N-progress.md` |
| Duplicate detection via embeddings | Free embedding source |
| Prompt linting (is the generator prompt complete?) | Structural check on prompts before calling cloud |

**What Gemma does NOT do:**

- Generator role for safety-critical content (negatives, agentic-loop security reviews)
- Reviewer role in cross-model review (breaks the "two independent frontier opinions" property)
- Final security judgment — Gemma flags suspicious, frontier decides

**Implementation.** Add `GemmaProvider(base_url="http://localhost:8080/v1", model="gemma-4-26B-A4B-it-Q8_0.gguf")` to `scripts/generate/providers.py`. Route via new `--validator-provider gemma` CLI flag (distinct from `--generator-provider` and `--reviewer-provider` which remain cloud-only).

**Critical Gemma 4 caveat.** Gemma 4 26B-A4B is a reasoning model. Every response includes a `reasoning_content` field with chain-of-thought alongside the normal `content` field. Even trivial prompts like "say hello" generate ~90 completion tokens (most in `reasoning_content`). Harness implications:
- Set `max_tokens` to at least 3× target output length to leave room for reasoning
- Parse `reasoning_content` separately from `content` (ignore for dataset purposes; optionally log for debug)
- For pure classification tasks, consider a "no think" system prompt to suppress reasoning if model supports it

**Cost impact.** Offloading validation + drafts + docs cuts cloud API spend by ~35% — new totals reflected in §2.1.

### 11.2 Reproducibility manifest

**Critical assessment finding (incorporated 2026-04-24):** every generated example must carry a provenance record. Without this, the dataset's audit trail is "Scott reviewed it on date X" with no way to investigate model drift, prompt regressions, or post-hoc concerns about specific generations.

Add a `metadata.provenance` block to every generated example (Phases 2–4):

```json
{
  "metadata": {
    "provenance": {
      "schema_version": "2.2",
      "generator_model": "claude-sonnet-4-6",
      "generator_model_snapshot": "claude-sonnet-4-6-20260101",
      "generator_provider": "anthropic",
      "generator_reasoning_effort": null,
      "generator_temperature": 0.7,
      "prompt_template_id": "negatives-v2",
      "prompt_template_hash": "sha256:abc123...",
      "validator_model": "gemma-4-26B-A4B-it-Q8_0.gguf",
      "validator_passed": true,
      "review_session_id": "review-2026-06-15-batch-03",
      "reviewed_by": "scthornton+claude-opus-4-7",
      "review_date": "2026-06-15",
      "corrections_applied": ["fixed_turn_2_safety_claim", "added_log_line"],
      "generation_date": "2026-06-14",
      "generation_run_id": "run-20260614-143022"
    }
  }
}
```

**Why this matters:**
- **Drift detection.** If 6 months from now we see the dataset's quality has drifted, we can correlate with model snapshot dates and prompt template versions.
- **Targeted recalls.** If a prompt template turns out to have a subtle bug, we can identify exactly which examples used that template and re-generate.
- **Reproducibility claims.** Anyone can verify: "this example was generated by Claude Sonnet 4.6 dated 2026-01-01 with prompt template `negatives-v2` (hash X) and reviewed in session `review-2026-06-15-batch-03`."
- **Audit defensibility.** "How did this example end up in the dataset?" has a single-record answer.

**Implementation in harness (~4 hr).** Add `provenance.py` module to `scripts/generate/`. Hooks into every generation call to capture model + snapshot + reasoning_effort + temperature. Hooks into prompt template loading to compute SHA-256 hash. Hooks into review pipeline to record session ID. Writes the block as part of every output JSON.

**Storage.** Provenance lives inside `metadata.provenance`. Schema extension is fully backward-compatible (optional field). Existing 1,378 examples get a stub provenance with `generator_model: "legacy_v2_pre_provenance"` so the field is universally present.

### 11.3 Reject-reason log (added after external review)

Every candidate example that *fails* an acceptance gate is logged separately in `data/rejects/phase-N-rejects.jsonl`. Each reject record includes:

```json
{
  "candidate_id": "tentative-safe-eval-allowlist-python-000003",
  "reject_stage": "cold_reviewer | scott_opus_adjudication | external_reviewer | fp_eval_regression",
  "reject_reason": "Reviewer Provider B identified exploit path: allowlist regex escapes via unicode normalization. Sample exploit: ...",
  "candidate_content": { /* the rejected example as it stood at reject time */ },
  "generator_provenance": { /* full provenance block as it would have been */ },
  "rejected_date": "2026-06-15"
}
```

**Why this matters:**
- **Transparency** — reviewers and users can audit not just what was accepted but what was tried and rejected. Several published "negative results" become more credible than only published successes.
- **Pattern detection** — clustering reject reasons surfaces systemic issues (e.g., "all rejects in pattern X are for the same exploit class — pattern X may need to be dropped").
- **Future regeneration** — when a prompt template improves, we can re-attempt the rejected cases rather than starting fresh.

**Publication.** Reject log ships as a separate artifact alongside each release: `huggingface.co/datasets/scthornton/securecode-web/blob/main/rejects/phase-2-rejects.jsonl` etc. Not loaded by `load_dataset` by default (use `data_files="rejects/*"` if a user wants them).

### 11.4 Confidence and source markers on derived metadata (added after external review)

External reviewer noted: CWE→ATT&CK and CWE→CAPEC mappings are *derived heuristics*, not authoritative claims. EPSS scores manually approximated for composite (no-CVE) examples are *estimates*, not measurements. Marking everything as factual creates false precision.

Add source/confidence markers:

```json
{
  "metadata": {
    "epss_score": 0.842,
    "epss_confidence": "measured",
    "epss_source": "first.org_epss_api_v3",
    "attack_techniques": ["T1190", "T1078.004"],
    "attack_techniques_source": "derived_from_cwe_via_mitre_mapping",
    "attack_techniques_confidence": "heuristic",
    "capec_ids": ["CAPEC-66"],
    "capec_source": "derived_from_cwe_via_mitre_mapping",
    "capec_confidence": "heuristic",
    "cvss_v3_vector": "CVSS:3.1/...",
    "cvss_v3_source": "nvd_api"
  }
}
```

**Confidence enum:**
- `measured` — direct API result (EPSS from FIRST.org, CVSS from NVD)
- `heuristic` — derived from a published mapping (CWE→ATT&CK, CWE→CAPEC)
- `approximated` — manually estimated for composite/no-CVE examples (e.g., EPSS percentile bucket from `business_impact` text)
- `legacy` — pre-v2.1 examples without source tracking

**Why:** users filtering by ATT&CK technique should know they're filtering on heuristic mappings, not authoritative claims. A user building a SOC detection pipeline based on this metadata deserves to know the confidence of each filter dimension.

This is also what makes the dataset *honest* about its enrichment quality. Overclaiming hurts trust more than admitting limitations.

---

## 12. Phase execution plans

Detailed per-phase write-ups. Each section is structured as: objective, prerequisites, week-by-week execution, deliverables (specific file paths), concrete examples, acceptance gate, rollback plan, and what's unblocked on completion.

---

### 12.1 Phase 1 — v2.1 metadata enrichment

(This phase has two tasks. Task 1.1 below handles OWASP reconciliation; task 1.2 handles enrichment. Both run inside Phase 1.)

#### Task 1.1 — OWASP 2021/2025 reconciliation

**Objective.** Resolve the taxonomy drift between GitHub (OWASP 2025 with 1,215 examples) and Hugging Face (OWASP 2021 with 1,378 examples) so that all subsequent work builds on a single source of truth.

**Prerequisites.**
- Confirmation that OWASP Top 10:2025 is officially published (not draft). Check `https://owasp.org/Top10/` for "released" status before proceeding.
- Decision on reconciliation path (A, B, or C — see §10).

**Week-by-week (Path B, the recommended path).**

*Week 1: Assessment and plan.*
- Day 1–2: Verify OWASP 2025 official status. Document the 2021→2025 category mapping (already in `scripts/migrate_owasp_2025.py` on GitHub).
- Day 3: Audit the 219 framework additions on HF that are missing from GitHub. Identify any that would re-categorize under 2025 (SSRF examples merge into Broken Access Control; Vulnerable Components becomes Software Supply Chain Failures).
- Day 4: Draft the migration PR plan. Backup current HF splits first.
- Day 5: Prepare downstream-user communication: a dataset-card notice announcing the taxonomy change with a 2-week advance window before the breaking change.

*Week 2: Execute migration.*
- Day 1: Clone HF's 1,378 examples locally. Run `deduplicate_and_resplit.py` to establish a clean baseline (expect ~0 duplicates removed — HF is already deduped, per commit `17acc7f`).
- Day 2: Run `scripts/migrate_owasp_2025.py` on the full baseline. This renames `metadata.owasp_2021` → `metadata.owasp_2025` and remaps values. Preserve the 2021 value in `metadata.owasp_2021_legacy` for reference.
- Day 3: Re-run `validate_contributing_compliance_v2.py` on migrated data. Expect a drop in some category counts (SSRF folds into Access Control) — capture the new distribution.
- Day 4: Update `schema.json` (or promote `schema_v2.json` to canonical). Rebuild parquet splits via `deduplicate_and_resplit.py` preserving 1102/138/138 sizes.
- Day 5: Update README YAML frontmatter + coverage tables to reflect 2025 taxonomy. Push to HF as `v2.1.0-pre` tag; hold for one week before making default.

**Deliverables.**
- `scripts/migrate_owasp_2025.py` — reused from GitHub
- `data/train-00000-of-00001.parquet` et al — rebuilt
- `schema.json` — updated to OWASP 2025 fields
- `README.md` — updated frontmatter, coverage tables, migration note in CHANGELOG
- `MIGRATION_LOG.json` (new) — audit trail of every example's 2021→2025 reclassification

**Concrete example — migration output.**

Before:
```json
{
  "metadata": {
    "owasp_2021": "A10:2021-Server-Side Request Forgery",
    "category": "ssrf"
  }
}
```

After:
```json
{
  "metadata": {
    "owasp_2025": "A01:2025-Broken Access Control",
    "owasp_2021_legacy": "A10:2021-Server-Side Request Forgery",
    "category": "broken_access_control",
    "subcategory": "ssrf"
  }
}
```

**Acceptance gate.**
- [ ] 100% of examples have `owasp_2025` populated
- [ ] 100% of previously-`owasp_2021` examples have `owasp_2021_legacy` set (non-lossy migration)
- [ ] `validate_contributing_compliance_v2.py` passes on all 1,378 examples
- [ ] `split_leakage_check.py` shows no cross-split contamination
- [ ] Parquet rebuild matches 1102/138/138 exactly
- [ ] README coverage tables sum to 1,378
- [ ] HF dataset card updated with migration notice + 2-week advance window before default flips

**Rollback plan.** `deduplicate_and_resplit.py` creates `.bak_YYYYMMDD_HHMMSS` files. Keep the pre-migration parquet splits under `backups/pre-2025-migration/` for 90 days. If issues surface post-release, revert the parquet files and push a patch release.

**What's unblocked.** Phase 1 (metadata enrichment) — no point enriching EPSS/ATT&CK/CAPEC against a taxonomy that's about to change.

---

#### Task 1.2 — metadata enrichment

**Objective.** Add exploitability and threat-intel metadata (EPSS, ATT&CK, CAPEC, CVSS v3/v4, preconditions) to all 1,378 examples so users can filter by what's actually exploitable in their environment, not just by severity.

**Prerequisites.**
- Phase 0 complete (OWASP 2025 baseline)
- FIRST.org EPSS API accessible (no key required)
- NVD API key obtained (free, increases rate limit from 5/30sec to 50/30sec) — https://nvd.nist.gov/developers/request-an-api-key
- MITRE CWE→ATT&CK and CWE→CAPEC mapping CSVs downloaded locally

**Week-by-week.**

*Week 1: Build enrichment script.*
- Day 1: Scaffold `scripts/enrich_metadata.py`. Provider abstraction for NVD, EPSS, MITRE mappings. Retry logic + caching (14-day TTL per CVE to avoid re-fetching).
- Day 2: Implement CVE-backed enrichment path. For each example with `context.cve`, fetch EPSS score/percentile, CVSS v3/v4 vectors from NVD, derive preconditions from CVSS AV/PR/UI fields.
- Day 3: Implement CWE-derived enrichment path. Join on `metadata.cwe` against MITRE mapping CSVs. Output `attack_techniques` and `capec_ids` arrays.
- Day 4: Implement composite-scenario queue. Examples with `context.cve: null` are written to `enrichment_manual_queue.jsonl` with partial enrichment (ATT&CK/CAPEC from CWE works, but EPSS/CVSS require manual approximation).
- Day 5: Unit tests + dry-run on a 20-example sample. Verify JSON output matches schema extension.

*Week 2: Run enrichment + manual queue.*
- Day 1: Run full automation across 1,378 examples. Log provider call counts, cache hit rate, failure list.
- Day 2: Debug failures (expect ~2–5% CVE lookup failures from retired/disputed CVEs). Retry with fallback sources.
- Day 3–4: Work the manual queue (~350 composite examples). For each, manually assign plausible EPSS percentile ranges (high/medium/low bucket → 0.9/0.5/0.1) and CVSS vectors based on business_impact text. Budget: 2 min × 350 = ~12 hours.
- Day 5: Validation pass — sample 10% (140 examples) for spot-check; verify auto-derived fields look right.

*Week 3: Schema, README, ship.*
- Day 1: Update `schema.json` with new optional fields. Bump `context.year.maximum` from 2025 to 2027 (prevents re-edit in a year).
- Day 2: Update README YAML frontmatter with new feature definitions. Add "Enriched Metadata" section to README body documenting each field and its source.
- Day 3: Rebuild parquet splits via `deduplicate_and_resplit.py`. Verify 1102/138/138 preserved.
- Day 4: Internal review, final QA sweep.
- Day 5: Push to HF as `v2.1.0`.

**Deliverables.**
- `scripts/enrich_metadata.py` (new, ~500 LOC)
- `scripts/data/cwe-attack-mapping.csv` (new, from MITRE)
- `scripts/data/cwe-capec-mapping.csv` (new, from MITRE)
- `scripts/cache/` — on-disk EPSS/NVD cache (gitignored)
- `enrichment_manual_queue.jsonl` (new, under `backups/` when complete)
- `schema.json` — extended with new optional fields
- All `data/*.jsonl` — enriched in place, preserving one-line vs pretty-printed formatting per existing convention
- `data/*.parquet` — rebuilt
- `README.md` — new metadata section, updated frontmatter

**Concrete example — enriched output.**

```json
{
  "id": "express_js-injection-000001",
  "metadata": {
    "owasp_2025": "A04:2025-Cryptographic Failures",
    "cwe": "CWE-916",
    "severity": "CRITICAL",
    "epss_score": 0.842,
    "epss_percentile": 0.981,
    "epss_date": "2026-04-24",
    "attack_techniques": ["T1552.001", "T1110.002"],
    "capec_ids": ["CAPEC-49", "CAPEC-55"],
    "cvss_v3_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N",
    "cvss_v4_vector": null,
    "preconditions": {
      "auth_required": false,
      "network_position": "internet",
      "user_interaction": "none",
      "prior_access": "none"
    }
  }
}
```

**Acceptance gate.** See §3 acceptance criteria plus:
- [ ] EPSS/CVSS cache TTL documented (14 days) and refresh script scheduled
- [ ] MITRE mapping CSVs dated and versioned in `scripts/data/`
- [ ] HF dataset page loads without errors on default config

**Rollback plan.** Pre-enrichment parquet backed up to `backups/pre-v2.1/`. If enrichment introduces consumer-breaking issues (unlikely — all fields are additive), revert parquet + push v2.0.2 patch.

**What's unblocked.** User-visible momentum on the dataset. Downstream tools can filter by EPSS for the first time. v2.2 negatives can inherit the same metadata schema.

---

### 12.2 Phase 2 — v2.2 negatives

(This phase has four tasks. Task 2.1 builds the shared generation harness reused by Phases 3 and 5. Tasks 2.2 and 2.3 are the new evidence-based prerequisites added in the critical assessment. Task 2.4 is the negatives generation itself.)

#### Task 2.1 — cross-model generation harness

**Objective.** Build `scripts/generate.py` — the shared generation infrastructure used by Phases 3, 4, and 5. Abstracts provider differences, routes generator/reviewer roles across OpenAI and Anthropic, enforces budgets, and runs validation on output before writing.

**Prerequisites.**
- `OPENAI_API_KEY` and `ANTHROPIC_API_KEY` available in `.env`
- `scripts/enrich_metadata.py` pattern established in Phase 1 (provider abstraction reused)
- `validate_contributing_compliance_v2.py` on hand for output validation

**Week-by-week (~1 week focused).**

*Day 1: Provider abstraction.*
- Implement `Provider` protocol with `generate(prompt, role, max_tokens) -> Response`
- Concrete `AnthropicProvider` wrapping the `anthropic` SDK — use **`claude-sonnet-4-6`** for both generator and reviewer roles (Sonnet 4.7 is not yet released; verified against `/v1/models` on 2026-04-24). Reserve `claude-opus-4-7` for flagged edge-case adjudication only (rough estimate: 5% of disagreements) since Opus is ~5× the cost.
- Concrete `OpenAIProvider` wrapping the `openai` SDK — use **`gpt-5.4`** ($2.50/$15 per 1M; cost parity with Sonnet 4.6 for clean 50/50 routing). GPT-5.5 ($5/$30) is 2× the cost with no proven quality delta on this workload, and was released 2026-04-23 — not running a 200-example sprint against a one-day-old model. Reserve `gpt-5.5` for adjudicator edge cases only.
- All GPT-5.x models are reasoning models. Must set `reasoning_effort` explicitly (`none`/`low`/`medium`/`high`/`xhigh` — *not* `minimal`). Default consumes the entire `max_completion_tokens` budget on internal reasoning. Routing:
  - Validation/classification: `reasoning_effort=none`
  - Generator role: `reasoning_effort=low`
  - Reviewer role: `reasoning_effort=medium`
  - Adjudicator edge cases (gpt-5.5): `reasoning_effort=high`
- **Cost optimizations**:
  - Use **Batch API** (50% discount on both providers) for any generation run that doesn't need real-time response. Phase 2 negatives, Phase 3 IaC, Phase 4 agentic generation all qualify.
  - Use **prompt caching** for system prompts. Anthropic and OpenAI both offer ~10× cached-input discount. Generation harness reuses the same multi-thousand-token system prompt across 100+ calls per phase.
- Unified response object with token counts, cost, provider name, latency

*Day 2: Role routing.*
- Three roles: `generator`, `reviewer`, `tester` (latter only for agentic)
- Per-example provider assignment strategy: deterministic alternation seeded by example ID (so reruns are reproducible)
- Constraint: generator and reviewer must be different providers
- Tester (when invoked) is random assignment

*Day 3: Adjudicator logic.*
- For negatives and safety-critical output: generator produces, reviewer independently evaluates without seeing generator's rationale
- Structured adjudicator compares: agree-safe / agree-unsafe / disagree
- Disagreements queued to `review_queue.jsonl` for human adjudication
- Agreement rate logged per run for §11 disagreement-tracking metric

*Day 4: Budget + logging.*
- Per-run budget cap (from `SECURECODE_GENERATION_BUDGET_USD` env var)
- Halt-on-exceed with partial-progress save
- Structured JSON log per generation: provider, role, tokens, cost, latency, validation pass/fail
- Run summary report at exit: total cost, agreement rate, validation pass rate

*Day 5: Validation integration + tests.*
- Wire `validate_contributing_compliance_v2.py` as post-generation gate
- Examples failing validation go to `generation_failures.jsonl` with error messages
- Unit tests with mocked providers
- Integration test: generate 5 example on each provider, verify end-to-end

**Deliverables.**
- `scripts/generate.py` (new, ~800 LOC across modules)
  - `scripts/generate/providers.py` — Anthropic and OpenAI wrappers
  - `scripts/generate/roles.py` — role routing
  - `scripts/generate/adjudicator.py` — agreement logic
  - `scripts/generate/budget.py` — cost tracking
  - `scripts/generate/validate.py` — compliance validator wrapper
- `scripts/generate/cli.py` — entry point
- `tests/test_generate.py` (new) — unit tests with mocks
- `.env.example` (new) — documented env vars
- `docs/GENERATION_HARNESS.md` (new) — usage docs, provider routing examples, cost estimation

**Concrete example — CLI usage for Phase 3.**

```bash
# v2.2 negatives generation run
python -m scripts.generate.cli \
  --task negatives \
  --pattern safe-eval-allowlist \
  --count 10 \
  --language python \
  --generator-provider anthropic \
  --reviewer-provider openai \
  --output data/safe-eval-allowlist-python.jsonl \
  --review-queue review_queue.jsonl \
  --budget 15.00
```

**Acceptance gate.**
- [ ] 5-example dry-run succeeds on both Anthropic and OpenAI providers
- [ ] Adjudicator correctly routes agreement, disagreement, and validation-fail cases
- [ ] Budget cap halts generation mid-run (tested with a $0.50 cap)
- [ ] Every generated example passes `validate_contributing_compliance_v2.py` before being written to output
- [ ] Cost log matches actual provider invoices (spot check after first real run)
- [ ] Unit tests cover all three roles × two providers = 6 routing permutations

**Rollback plan.** Harness is internal tooling with no dataset impact on its own. If bugs surface during Phase 3–5 runs, fix forward — no rollback needed.

**What's unblocked.** All content-generating phases (3, 4, 5). Without the harness, generation is manual and the cross-model adversarial-review layer that complements Scott + Opus adjudication has no machinery.

---

#### Task 2.2 — Evidence-based pattern selection

**Objective.** Replace the heuristic 15-pattern list with a data-derived list. Catalog what existing fine-tuned SecureCode models actually over-flag on real benign code, then build the negatives taxonomy from that distribution.

**Workflow (~10 hr).**

1. **Source benign code corpus** (2 hr): Collect ~500 random functions from popular GitHub repos with no known CVEs (Django, Flask, FastAPI, Express, Spring, Rails, etc. — match dataset's framework coverage). Save to `eval/benign-functions.jsonl`.
2. **Run all 8 fine-tuned models** (3 hr): Score each function: vulnerable / safe. Track which models flagged each function and what category they assigned.
3. **Cluster false positives** (3 hr): Functions that 2+ models flagged but no real reviewer would flag. Group by surface feature (e.g., "uses eval", "raw SQL string", "permissive CORS"). Output ~15 clusters.
4. **Document** (2 hr): `docs/NEGATIVE_PATTERN_DERIVATION.md` mapping data → patterns → counts. Becomes part of v2.2 release evidence.

**Deliverables.** `eval/benign-functions.jsonl`, `eval/baseline-flag-results.json`, `docs/NEGATIVE_PATTERN_DERIVATION.md`.

#### Task 2.3 — FP-rate eval baseline

**Objective.** Define the eval test set used to validate v2.2's claim. Without this baseline, "30% FP-rate reduction" is unfalsifiable marketing.

**Workflow (~6 hr).**

1. **Curate 200 known-safe** (2 hr): random sample from the Task 2.2 benign corpus that no model flagged + 100 hand-picked tricky-but-safe examples covering the patterns from §4 list.
2. **Curate 200 known-vulnerable** (1 hr): held out from existing dataset's training data; ensure no leakage from train/val/test splits already published.
3. **Run all 400 against all 8 models** (1 hr): record FP rate and FN rate per model.
4. **Save baseline** (1 hr): `eval/v2-baseline-fp-fn.json` with per-model numbers.
5. **Document protocol** (1 hr): `eval/PROTOCOL.md` describing how to re-run after fine-tuning so the comparison is apples-to-apples.

**Deliverables.** `eval/safe-200.jsonl`, `eval/vulnerable-200.jsonl`, `eval/v2-baseline-fp-fn.json`, `eval/PROTOCOL.md`.

**Acceptance for v2.2:** re-run protocol after fine-tuning with negatives folded in; publish actual numbers regardless of whether they hit the 30% target. Honest negative result is better than no result.

#### Task 2.4 — Negatives generation + author Opus review

**Objective.** Generate 150 examples where code looks dangerous but is demonstrably safe, covering 15 pattern categories (§4). Reduce false-positive rates in downstream-trained security models.

**Prerequisites.**
- Phase 2 harness complete and tested
- 15 pattern templates authored (§4 lists them)
- Author (Scott) available for 15% spot-check + 100% disagreement review

**Week-by-week (~6 weeks at part-time pace).**

*Week 1: Taxonomy + templates.*
- Day 1–2: Author "Turn 2 template" per pattern — structured prompt fragments for generator that force the "looks wrong / is fine / what would make it unsafe" structure.
- Day 3: Schema extension work — add `metadata.example_type` to `schema.json`.
- Day 4: Harness adjudicator extension — implement the negatives-specific logic (both models must agree "safe" for acceptance).
- Day 5: 10-example pilot run across 3 patterns. Review output manually. Tune prompts.

*Week 2–4: Generation sprints.*
- Run 5 pattern categories per week × 10 examples each = 50 examples/week. Each run:
  - Harness generates (alternating Anthropic/OpenAI as generator; the other as reviewer)
  - Agreement-rate logged; acceptance threshold is "both agree safe"
  - Disagreements → `review_queue.jsonl`
  - Validation-failures → `generation_failures.jsonl`; retry or discard
- Budget: target ~$40/week × 3 weeks = $120 total

*Week 5: Author review.*
- Day 1–2: Random 15% spot-check (~22 examples): re-read the code, confirm the "safe" claim holds, verify Turn 2's "what would make this unsafe" is correct
- Day 3–4: 100% review of model disagreements (expected ~30 examples based on negatives being harder than straight vulns)
- Day 5: Per-pattern disagreement-rate analysis. If any pattern hit >30% disagreement, flag for extra scrutiny before shipping

*Week 6: FP-rate eval + ship.*
- Day 1–2: Fine-tune one existing SecureCode model (e.g., `qwen-coder-7b-securecode`) with negatives folded in; compare FP rate on a held-out safe-code eval against the baseline model
- Day 3: Parquet rebuild with negatives folded into default train/val/test proportionally (≈120/15/15). Also build `safe_controls` HF config.
- Day 4: README + CHANGELOG updates. Release notes explicitly call out the cross-model review methodology replacing a human 2nd reviewer — transparency matters.
- Day 5: Push to HF as `v2.2.0`.

**Deliverables.**
- `data/safe-*.jsonl` × 15 pattern files, ~10 examples each (total 150)
- `schema.json` — extended with `metadata.example_type`
- Parquet splits rebuilt (1218/153/153 including negatives proportionally) plus `safe_controls` config parquet
- `README.md` — new "Safe Controls" section with methodology
- `CHANGELOG.md` — v2.2 entry
- `docs/NEGATIVES_METHODOLOGY.md` (new) — cross-model review protocol, disagreement-rate data, FP-eval results

**Concrete example — one negative example (abbreviated).**

```json
{
  "id": "safe-eval-allowlist-python-000001",
  "metadata": {
    "example_type": "safe_control",
    "owasp_2025": "A05:2025-Injection",
    "category": "injection",
    "subcategory": "code_injection"
  },
  "conversations": [
    {
      "turn": 1,
      "from": "human",
      "value": "I inherited this code that uses eval(). Is it vulnerable?"
    },
    {
      "turn": 2,
      "from": "assistant",
      "value": "This *looks* dangerous (raw eval on user input), but it's actually safe as implemented. Here's why:\n\n[code]\n\nThe pre-eval validation restricts input to a strict allowlist of ~40 numeric-expression tokens. Anything outside that set raises before eval runs.\n\n## What would make this unsafe\n\n- Adding any identifier to the allowlist (opens attribute access)\n- Widening to allow string literals (opens f-string abuse paths)\n- Removing the length cap (enables algorithmic DoS via deeply-nested expressions)\n- Running eval under a more-privileged context than the request thread\n\nAny of those changes turns a safe sandbox into a real injection surface."
    },
    { "turn": 3, "from": "human", "value": "What if the allowlist grows over time — how do I keep it safe?" },
    { "turn": 4, "from": "assistant", "value": "[Turn 4: monitoring strategy — linter rule to flag allowlist additions, canary tests that probe for escape, logging every eval call with input hash for post-hoc analysis, migration path to a real expression parser once allowlist exceeds 60 tokens...]" }
  ],
  "validation": { "security_review": "passed", "reviewed_by": "cross_model_anthropic+openai_agreement; author_spot_check_2026-06-15" }
}
```

**Acceptance gate.** §4 acceptance criteria plus:
- [ ] Measurable FP-rate reduction on held-out eval (target: ≥30% reduction; document actual result in release notes)
- [ ] Per-pattern disagreement rates logged in `docs/NEGATIVES_METHODOLOGY.md`; any pattern >30% disagreement either escalated to full human review or dropped from release
- [ ] Author spot-check sample was genuinely random (seeded shuffle, not hand-picked)

**Rollback plan.** If a post-release vulnerability is found in a negative (the nightmare scenario): issue an immediate `v2.2.1` that removes the affected example, publish a security advisory citing the example ID, review the entire pattern category it came from before reshipping. The cross-model-review methodology document is the audit trail.

**What's unblocked.** Demonstrates the cross-model review pipeline works end-to-end, de-risking its reuse in v2.3 and v3.0. First user-visible release since v2.0's framework additions.

---

### 12.3 Phase 3 — `securecode-infra` v0.1 (NEW SIBLING DATASET)

**Objective.** Add 80 examples covering Terraform (40) and Kubernetes (40) misconfigurations with real-incident grounding and detection-rule integration.

**Prerequisites.**
- Phase 2 harness complete
- Incident research: Capital One (IAM), Tesla K8s cryptomining, public bucket breaches, kubelet exposures — build a ~30-incident library before generation starts

**Week-by-week (~4 weeks at part-time pace).**

*Week 1: Research + pattern templates.*
- Day 1–2: Incident library — 30 documented incidents with CVE-or-equivalent, year, affected systems, root cause
- Day 3: Pattern templates for Terraform (10 categories) and K8s (10 categories) per §5
- Day 4: Detection-rule templates — Checkov, tfsec, Falco, kube-bench, AWS Config integration per example
- Day 5: 5-example pilot run to tune prompts

*Week 2–3: Generation.*
- Run 20 examples per week × 2 weeks = 40 examples/week for a week each of Terraform and K8s
- Provider routing: 50/50 random assignment; cross-review on 20% sample only (cost cap)
- Detection-rule authoring happens inline with generation — Turn 4 of every example must include a concrete detection snippet

*Week 4: Review + ship.*
- Day 1–2: Single-reviewer pass on all 80 examples (~30 min each = 40 hr; but reviewer is the author so pull forward from generation oversight time)
- Day 3: Parquet rebuild folding 80 examples into default splits (≈64/8/8 added)
- Day 4: README updates — IaC now first-class category in coverage tables
- Day 5: Push to HF as `v2.3.0`

**Deliverables.**
- `data/terraform-*.jsonl` × 10 subcategory files, 40 examples total
- `data/kubernetes-*.jsonl` × 10 subcategory files, 40 examples total
- `docs/IAC_DETECTION_RULES.md` (new) — catalog of Checkov/tfsec/Falco/kube-bench rules referenced per example
- README coverage tables — IaC as a first-class row
- Parquet rebuilt (1282/161/161)

**Concrete example — Turn 4 detection rule integration.**

```markdown
## Detection

**Checkov rule (CKV_AWS_20):**
```yaml
checks:
  - id: CKV_AWS_20
    description: S3 Bucket should not be publicly accessible
    enforce: true
```

**AWS Config rule (s3-bucket-public-read-prohibited):**
```json
{ "ComplianceResourceTypes": ["AWS::S3::Bucket"], "SourceIdentifier": "S3_BUCKET_PUBLIC_READ_PROHIBITED" }
```

**Runtime detection (CloudTrail + EventBridge):**
Trigger alert when `s3:PutBucketAcl` grants `AllUsers` or `AuthenticatedUsers` groups read/write permissions.
```

**Acceptance gate.** §5 acceptance criteria plus:
- [ ] Every Terraform example includes a `checkov_rule_id` or `tfsec_rule_id` in `metadata.tags`
- [ ] Every K8s example includes a `kube_bench_ref` or `falco_rule` in `metadata.tags`
- [ ] README IaC coverage section added with incident-to-example crosswalk

**Rollback plan.** Same as v2.1 — keep pre-v2.3 parquet under `backups/pre-v2.3/` for 90 days.

**What's unblocked.** Closes the biggest coverage gap. Makes the dataset relevant to cloud-security teams, not just app-sec teams.

---

### 12.4 Phase 4 — v2.4 executable verification

**Objective.** Add reproducible Docker-based exploit + fix verification to ~50 of the highest-severity examples in `securecode-web`. Convert `validation.code_execution: passed` from a human attestation into a CI-checked, anyone-can-reproduce claim. Establishes the methodology that future releases scale.

**Prerequisites.**
- Phases 1, 2, 3 complete (v2.1, v2.2, infra v0.1)
- Docker + Docker Compose available locally
- GitHub Actions CI integration permissions
- ~50 CRITICAL-severity CVE-backed examples selected from existing dataset

**Week-by-week (~12 weeks at part-time pace; longer than other phases due to per-example engineering).**

*Week 1: Selection + planning.*
- Day 1–2: Select the 50 examples per criteria in §6. Output: `verification/SELECTION.md` with the 50 IDs, why each was picked, and known exploit references.
- Day 3: Standardize the Dockerfile/docker-compose template. Decide on language-specific base images, network isolation patterns, port allocation.
- Day 4: Author the `verify.sh` template — the contract every example must satisfy.
- Day 5: Pilot 3 examples (one Python, one JavaScript, one Java) end-to-end. Iterate on template until pilots are clean.

*Weeks 2–10: Per-example verification.*
- ~5 examples per week × 9 weeks = 45 verifications. Plus 3 from week 1 + buffer = 50.
- Each example takes ~80 min: extract vulnerable code → write Dockerfile → extract secure code → write second Dockerfile → write exploit script → write verify.sh → test locally → commit.
- Author Opus review at the end of each week's batch (5 examples × ~10 min review = 50 min/week).

*Week 11: CI integration.*
- Day 1–2: GitHub Actions workflow that detects `verification/` changes and runs affected `verify.sh` scripts. Layer caching for build speedup.
- Day 3: Parallel job matrix to keep total CI time under 15 minutes.
- Day 4: Status badge in README per verified example. Aggregate "verified count" badge at top.
- Day 5: Test by intentionally breaking one verification — confirm CI catches it.

*Week 12: Schema rollout + ship.*
- Day 1: Add `validation.execution_proof` field to schema.
- Day 2: Apply field to the 50 verified examples; rebuild parquet for `securecode-web`.
- Day 3: README "Verified Examples" section + dataset card update on HF.
- Day 4: Methodology doc `docs/EXECUTABLE_VERIFICATION.md` explaining how to add verification to future examples.
- Day 5: Push to HF as `v2.4.0`.

**Deliverables.**
- `verification/<example-id>/` × 50 directories
- `.github/workflows/verify.yml` — CI workflow
- `verify-template/` — boilerplate authors can copy when adding new verifications
- `docs/EXECUTABLE_VERIFICATION.md` — methodology + how-to-contribute
- `verification/SELECTION.md` — criteria + the 50 IDs
- README hero section: "🔒 50 examples reproducibly verified — every claim CI-checked"
- Schema extension for `validation.execution_proof`

**Concrete example — verify.sh contract:**

```bash
#!/usr/bin/env bash
set -euo pipefail

# Build both containers
docker compose -f docker-compose.yml build vulnerable secure

# Start vulnerable container, run exploit, expect success
docker compose up -d vulnerable
sleep 2
if ! ./exploit.sh vulnerable; then
  echo "REGRESSION: exploit failed against vulnerable code"
  exit 1
fi
docker compose down vulnerable

# Start secure container, run same exploit, expect failure
docker compose up -d secure
sleep 2
if ./exploit.sh secure; then
  echo "REGRESSION: exploit succeeded against secure code"
  exit 1
fi
docker compose down secure

echo "VERIFIED: exploit works against vulnerable, fails against secure"
exit 0
```

**Acceptance gate.** §6 acceptance criteria plus:
- [ ] `verify.sh` for all 50 examples exits 0 locally
- [ ] CI passes all 50 in <15 minutes wall clock
- [ ] At least one external user has reproduced verification on their own machine (verify the methodology actually works for outsiders, not just our setup)
- [ ] Docker base image versions pinned in every Dockerfile (no `:latest` tags)

**Rollback plan.** Verification is additive — it adds a `verification/` directory and an `execution_proof` field. Existing examples without verification continue to work. If a verification breaks 6 months later due to environment drift, mark `validation.code_execution: drift_detected` and queue for re-verification rather than removing it.

**What's unblocked.** The differentiator that makes the dataset citable as a *reference*, not just a *training corpus*. Future releases (v2.5, v2.6) can scale to 100, 200, eventually most of the dataset.

---

### 12.5 Phase 5 — v3.0 agentic review loops (DEFERRED — see §7 decision criteria)

**Objective.** Ship a 200-example agentic track as a separate HF config. Includes a new eval harness for measuring review-loop quality in fine-tuned models.

**Prerequisites.**
- Phases 1–4 complete (v2.3 is last 4-turn release — v3.0 is the format break)
- Schema extension accepted
- Voice bibles authored per agent role (writer, reviewer, tester)

**Week-by-week (~12–16 weeks at part-time).**

*Weeks 1–2: Schema + config + docs.*
- Extend `schema.json` with new `from` enum values, `metadata.format`, `agentic_metadata` block
- HF config split: default config unchanged; new `agentic` config with own train/val/test
- Write voice bibles: 2-page doc per agent role describing tone, typical turn length, what to include/exclude. These become LLM prompts during generation.

*Weeks 3–4: Harness extension + pilot.*
- Extend Phase 2 harness with multi-role cross-provider routing (§11)
- 20-example pilot across 5 loop patterns (4 each). Manually review every pilot example for voice consistency and terminal-state correctness.
- Iterate prompts until pilot examples look publishable.

*Weeks 5–12: Generation sprints.*
- 15 loop patterns × ~14 examples/pattern = 210 target (overgenerate to allow rejection)
- ~25 examples/week sustainable at 15 hr/wk
- Budget: ~$40/week × 8 weeks = $320

*Week 13: Review + QA.*
- All 200 examples get author review (~15 min each = 50 hours — this is where the review time goes)
- Terminal-state audit: every example must end with one of the four enum values, no dangling loops

*Weeks 14–15: Eval harness.*
- Build `scripts/agentic_eval.py` (~40 hours):
  - Held-out agentic test set (the 20 validation examples)
  - Metrics: terminal-state-correctness, loop-coherence (does each turn address the prior?), review-finding-accuracy (does the reviewer catch real bugs?), iteration-efficiency (how many rounds to resolution?)
  - Fine-tune a SecureCode base model on the agentic train set; compare before/after on the eval
- Publish before/after metrics alongside v3.0 release

*Week 16: Ship.*
- Parquet for new config (160/20/20 split)
- README overhaul: "Agentic Track (Preview)" section with schema doc and example
- Push to HF as `v3.0.0`; classic consumers load `default` config unchanged

**Deliverables.**
- `data/agentic-*.jsonl` × 15 pattern files, 200 examples total
- `data/agentic-train-00000-of-00001.parquet`, `-validation-`, `-test-`
- `scripts/agentic_eval.py` (new, ~600 LOC)
- `docs/AGENTIC_FORMAT.md` (new) — schema spec, voice bibles, usage examples
- `docs/AGENTIC_EVAL_RESULTS.md` (new) — before/after fine-tuning metrics
- `schema.json` — extended with agentic fields
- `README.md` — new prominent "Agentic Track (Preview)" section
- `CHANGELOG.md` — v3.0 entry with clear note that default config is unchanged

**Concrete example — partial agentic sequence.**

```json
{
  "id": "agentic-catch_and_fix-python-000001",
  "metadata": {
    "format": "agentic_loop",
    "example_type": "vulnerability",
    "owasp_2025": "A05:2025-Injection",
    "lang": "python"
  },
  "agentic_metadata": {
    "loop_pattern": "catch_and_fix",
    "turn_count": 7,
    "agents_involved": ["user", "writer_agent", "reviewer_agent"],
    "terminal_state": "approved",
    "iteration_rounds": 2
  },
  "conversations": [
    { "turn": 1, "from": "user", "value": "Build me a user-search endpoint for my Flask app." },
    { "turn": 2, "from": "writer_agent", "value": "[produces endpoint with f-string SQL]" },
    { "turn": 3, "from": "reviewer_agent", "value": "SQL injection on line 12 — f-string interpolates user input directly. Reference CWE-89. Please parameterize." },
    { "turn": 4, "from": "writer_agent", "value": "[revised with ? placeholders]" },
    { "turn": 5, "from": "reviewer_agent", "value": "SQLi fixed. Remaining concern: no length cap on the search term enables LIKE-scan DoS. Recommend 100-char limit and a trigram index." },
    { "turn": 6, "from": "writer_agent", "value": "[adds length validation + suggests index DDL]" },
    { "turn": 7, "from": "reviewer_agent", "value": "Approved. Summary: parameterization (SQLi fix), input cap (DoS mitigation), suggested index (performance)." }
  ]
}
```

**Acceptance gate.** §6 acceptance criteria plus:
- [ ] Eval harness runs on a fine-tuned model and produces the four metrics
- [ ] Before/after comparison shows measurable improvement on at least one metric (terminal-state-correctness is the most likely — document actual results)
- [ ] Default HF config load behavior unchanged (no regressions for classic consumers)
- [ ] Classic consumers who run `load_dataset("scthornton/securecode-web")` get exactly the v2.3 baseline

**Rollback plan.** Agentic ships as a separate config — can be unpublished without touching the default config. If the eval reveals the agentic track doesn't improve fine-tuned models, delay the release and iterate on prompts rather than shipping a format nobody benefits from.

**What's unblocked.** Dataset becomes relevant for the 2026 agent fine-tuning wave. Establishes a pattern other OWASP-grounded datasets can adopt.

---

## 13. Execution protocol — Claude as quarterback

This section defines how phase execution actually runs. Scott invokes a phase with a short command; Claude orchestrates end-to-end with defined authorization boundaries, checkpoint gates, and state persistence across sessions.

### 13.1 Invocation

| Command | Behavior |
|---|---|
| `execute phase N` | Start Phase N from the beginning. Read the phase plan, create a branch, post a plan summary, begin task 1. |
| `resume phase N` | Read `docs/phase-N-progress.md`, report current state, resume from last checkpoint. |
| `pause phase N` | Commit work-in-progress, update progress doc, hand back with a resume-ready summary. |
| `status` | Report current phase, current task, % complete, budget consumed, last checkpoint. |
| `checkpoint` | Force a manual checkpoint: commit, update progress doc, summarize. |
| `rollback last step` | Revert the most recent commit (with confirmation). |
| `abort phase N` | Soft-abort: commit, update progress doc with abort reason, delete branch only on explicit confirmation. |

Phase execution spans multiple Claude sessions. State persists via git commits, progress docs (`docs/phase-N-progress.md`), and my memory system. Expect to invoke `resume phase N` many times before a phase completes.

### 13.2 Authorization matrix

What Claude does autonomously vs. what requires Scott's approval.

| Action | Authorization |
|---|---|
| Create/edit files in the repo | **Autonomous** |
| Run local scripts (validators, enrichment, harness) | **Autonomous** |
| Call Anthropic/OpenAI APIs within budget cap | **Autonomous** |
| Call local Gemma 4 (unlimited) | **Autonomous** |
| Deploy subagents (Agent tool) for parallelizable work | **Autonomous** |
| Create feature branches | **Autonomous** |
| Commit to feature branches | **Autonomous** |
| Merge feature branch to main | **Checkpoint — Scott approves** |
| Push to GitHub remote | **Checkpoint — Scott approves** |
| Push to Hugging Face (dataset release) | **Checkpoint — Scott approves** |
| Change schema in ways not in the plan | **Checkpoint** |
| Exceed 80% of run budget | **Checkpoint — pause and ask** |
| Exceed run budget | **Hard stop** |
| Change phase scope | **Checkpoint** |
| Change license | **Never (manual only)** |
| Delete existing data files | **Never without explicit confirm** |
| Force-push to any branch | **Never without explicit confirm** |
| Rebuild parquet for final release artifact | **Checkpoint before the build** |

Default stance: if uncertain, checkpoint. The cost of pausing to confirm is low; the cost of an unwanted irreversible action is high.

### 13.3 Checkpoint policy

**Mandatory checkpoints** (Claude pauses, posts status, waits for Scott):

1. **Phase kickoff** — after planning, before first code change. Scott reviews plan, confirms or redirects.
2. **Sub-task boundaries** — at the end of each numbered task (e.g. task 1.1 complete, before starting 1.2).
3. **Pre-generation runs** — before any cloud API run >$20 estimated.
4. **Post-generation runs** — after any generation run, before folding into the dataset.
5. **Schema changes** — before modifying `schema.json`.
6. **Pre-release** — before rebuilding final parquet, before pushing to HF.
7. **Disagreement spikes** — if cross-model review disagreement rate on any pattern exceeds 30%.
8. **Budget >80%** — pause and reassess.
9. **Unexpected findings** — if a subagent reports something meaningfully off-plan.
10. **Context budget pressure** — before hitting compaction, checkpoint so resume is clean.

At each checkpoint Claude posts a **status block** of the form:

```
[Checkpoint: phase N, task N.N]
Done: <bullets>
Next: <bullets>
Budget: $X of $Y used (Z%)
Risks/blockers: <or "none">
Waiting on: <Scott to review / confirm / redirect>
```

### 13.4 Subagent deployment strategy

Subagents parallelize independent work. Deploy only when the task is genuinely independent of the main thread and the result is self-contained enough to summarize back.

| Agent | Best for |
|---|---|
| `code-analysis-wizard` | Post-generation code review; vulnerability spot-check on "is this actually safe?" negatives |
| `ai-redteam-pentester` | Adversarial review of negatives — "can you exploit this?" as a human-like second opinion |
| `sentinel-agent` | Writing security-hardened harness code; scripts that handle API keys |
| `ai-security-researcher` | Incident library research (Phase 3 IaC — Capital One IAM, Tesla K8s, etc.) |
| `prompt-security-expert` | Voice-bible authoring for Phase 4 agent roles; prompt linting |
| `qa-testing-expert` | Test plans for the harness; validation matrix for acceptance gates |
| `ml-security-expert` | Eval harness design (Phase 4) |
| `ml-statistical-expert` | FP-rate eval methodology (Phase 2 acceptance), inter-rater agreement math |
| `writer-rewriter` | Polishing README/CHANGELOG/article drafts |
| `Explore` | Codebase questions during phase kickoff |
| `general-purpose` | Anything that doesn't fit above |

**Parallelism rule.** If two subagents have zero data dependency, launch in a single message with two tool calls. Don't chain serially unless one needs the other's output.

**Trust-but-verify.** A subagent's result is its report, not a guarantee. Spot-check any claim that affects the dataset directly (e.g., "I verified 50 examples are safe" → I re-read 5 of those 50 before accepting).

### 13.5 Generation run discipline

For every cloud API generation run:

1. **Pre-run check** — confirm budget, confirm env keys, confirm output path, dry-run on 3 examples first.
2. **Budget guardrail** — `SECURECODE_GENERATION_BUDGET_USD` env var; harness halts on exceed.
3. **Provider balance** — log tokens/$ per provider; alert if skew >60/40 on a run that should be 50/50.
4. **Failure queue** — schema-fail, validation-fail, and disagreement-fail each go to separate queues with structured error messages.
5. **Post-run report** — cost by provider, agreement rate, validation pass rate, failure reasons. Posted in the checkpoint block.

### 13.6 Git discipline

- **Branch per phase**: `phase-1-metadata`, `phase-2-negatives`, etc. Sub-tasks are commits on that branch, not sub-branches.
- **Commit often**: every meaningful unit of work. Easier to rollback.
- **Commit messages**: follow existing repo style (short summary; body explains *why*, not what).
- **Never push** without checkpoint approval. Claude commits locally only.
- **Never force-push** under any autonomous workflow. If rebase needed, propose it at a checkpoint.
- **Never skip hooks** (`--no-verify`, `--no-gpg-sign`). If a hook fails, fix the underlying issue.
- **Phase completion**: Scott merges feature branch to main manually after release acceptance. Claude prepares the merge but doesn't execute it.

### 13.7 Session persistence and handoff

Phase execution spans many sessions. The truth lives in:

1. **Git commits on the phase branch** — source of truth for code/data.
2. **`docs/phase-N-progress.md`** — human-readable state: tasks done, tasks next, blockers, decisions made, budget used. Updated at every checkpoint.
3. **Claude memory** — durable decisions and gotchas (e.g., "never re-introduce AI/ML content to web dataset" already lives there).
4. **Commit messages** — why, not just what.

**Progress doc structure** (per phase):

```markdown
# Phase N Progress

## Status
- Current task: X.Y
- % complete: Z%
- Budget: $A of $B used
- Branch: phase-N-description

## Completed
- Task X.1 — done <date> — commit <hash>
- Task X.2 — done <date> — commit <hash>

## In progress
- Task X.3 — started <date>, blocked on <reason>

## Upcoming
- Task X.4
- Task X.5

## Decisions made this phase
- <decision> — <date> — <rationale>

## Open questions / blockers
- <question>

## Next checkpoint target
- <description>
```

**Session handoff.** When context gets tight, Claude: (1) commits WIP, (2) updates progress doc, (3) writes a handoff message with the exact command Scott should use to resume (`resume phase N`), (4) stops. Fresh session + `resume phase N` picks up cleanly.

### 13.8 Communication cadence

**Verbose (at checkpoints):** full status block, all metrics, clear ask.
**Quiet (during work):** short update at direction changes or blockers only. No narration of internal steps.
**Silent (routine):** file edits, normal tool calls, expected validator passes.

Rule: Scott should be able to walk away for an hour and return to find either (a) a clear checkpoint asking for input, or (b) a clear completed state with commits to review — never a half-finished stream of thought.

### 13.9 Failure modes and recovery

| Failure | Response |
|---|---|
| API outage (Anthropic or OpenAI) | Harness falls back to single-provider mode with degraded-log tag; examples re-reviewed when outage ends |
| Budget exceeded | Hard stop; checkpoint with summary; Scott decides to raise or cut scope |
| Validation-fail rate >20% on a run | Stop run; debug prompt; resume with fixed prompt |
| Cross-model disagreement rate >30% on a pattern | Pause pattern; full human review of all examples in that pattern before resuming |
| Schema-breaking change needed mid-phase | Checkpoint; Scott decides to accept break or defer |
| Git operation fails (push rejected, merge conflict) | Stop; report; Scott resolves manually or directs |
| Subagent returns something unexpected | Surface as checkpoint finding, not a silent override |
| Context budget nearly exhausted | Commit, update progress doc, handoff |

### 13.10 Decisions confirmed (2026-04-24)

- [x] `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` set in shell env
- [x] Gemma 4 running on `localhost:8080` (llama-server pid 3485)
- [x] `docs/` directory exists
- [x] **OWASP 2025 migration path**: Path B confirmed — re-migrate HF to OWASP 2025 (not 2021). Target OWASP 2025 or newer if published by execution time.
- [x] **Phase 2 cloud budget cap**: $100 (with ~$20 headroom over estimated $80)
- [x] **GitHub push policy**: open a PR for each phase completion. Scott reviews and merges. Motivation: visible account activity matters.
- [x] **HF push policy**: final tested version only, never incremental. Two variants:
  - **v2.1, v2.3** — straight to `main` after GitHub PR merge (backward-compatible changes only)
  - **v2.2, v3.0** — RC flow: push as `v2.2.0-rc1` / `v3.0.0-rc1` tagged revision first with dataset-card note + 1–2 week feedback window, then promote to `main` as `v2.2.0` / `v3.0.0`
- [ ] Repo clean — verify `git status` at start of each phase
- [ ] `main` branch up to date with remote — verify at start of each phase

### 13.11 Release push workflow (per phase)

```
Phase N work
  ├── commits on feature branch: phase-N-description
  ├── checkpoint: content complete, parquet rebuilt, validators passing
  │
  ├── push feature branch to GitHub remote  ◀─── Scott approves
  ├── open PR: "Phase N: <description>"     ◀─── Claude drafts, Scott merges
  │
  ├── (for v2.2 / v3.0 only) push to HF as vN.N.0-rc1 tagged revision
  ├── (for v2.2 / v3.0 only) feedback window 1–2 weeks
  ├── (for v2.2 / v3.0 only) promote rc → main as vN.N.0
  │
  └── (for v2.1 / v2.3) push to HF main directly as vN.N.0  ◀─── Scott approves
```

---

## 14. Strategic considerations

Added 2026-04-24 from critical assessment.

### 14.1 Dataset family identity

Currently:
- `scthornton/securecode-web` — application security (this dataset)
- `scthornton/securecode-aiml` — AI/ML system security
- `scthornton/securecode` — combined web + aiml

Phase 3 ships **`scthornton/securecode-infra`** as a fourth sibling for infrastructure + supply chain. This keeps each dataset focused on a coherent audience and threat model:

| Dataset | Audience | Tooling | Examples (post-roadmap) |
|---|---|---|---|
| `securecode-web` | Application developers | SAST, DAST, framework linters | ~1,528 (after v2.2) |
| `securecode-aiml` | ML engineers, AI safety | adversarial robustness, red teaming | 750 |
| `securecode-infra` | Cloud / platform / DevSecOps | Checkov, tfsec, Falco, sigstore | 90 (Phase 3) |
| `securecode` (unified) | Researchers wanting everything | varies | ~2,368 (web + aiml + infra after Phase 3) |

After Phase 3 ships, update `securecode` (unified) to optionally include infra content as a new config — separate housekeeping release, not blocking.

### 14.2 External reviewer recruitment (Phase 2 prerequisite)

Critical assessment finding: even with Scott + Opus review, public release credibility benefits from at least one external security professional reviewing a 10% sample before v2.2 ships. Negatives are the highest-risk content in the roadmap — a single example that ships a real vulnerability poisons downstream models.

**Action item before Phase 2 starts:**
- Identify 1–2 external security professionals willing to review ~15 negative examples for credit in the dataset card
- Draft a one-page reviewer protocol (what to look for, how to log findings)
- Confirm availability matches Phase 2 timeline (week 5 ish of Phase 2 execution)

If no external reviewer is available, ship v2.2 anyway with explicit dataset-card disclosure: "Single-author review with Claude Opus 4.7. No external review." Honest framing beats false claims.

### 14.3 Next siblings on the roadmap (post-Phase-4)

These were originally listed as "out of scope." External review correctly noted that some are too strategically important to leave there. Promoted to **planned** status with rough sequencing:

**`securecode-api` v0.1 — OWASP API Top 10 sibling (next planned after Phase 4).**

External reviewer's framing: "more strategically relevant to modern web security than mobile or agentic loops." Real-world breaches in 2024–2025 were disproportionately API-specific (BOLA, broken object-property-level authorization, unsafe API consumption). The current Web dataset's Broken Access Control category covers some of this, but OWASP API Top 10 is its own taxonomy and audience.

Rough scope (placeholder, refine when planning starts):
- BOLA (Broken Object-Level Authorization) — ~20 examples
- Broken Authentication — ~15 examples
- BOPLA (Broken Object Property-Level Authorization) — ~12 examples
- Unrestricted Resource Consumption — ~10 examples
- Broken Function-Level Authorization — ~12 examples
- Server-Side Request Forgery (already in Web; cross-link here)
- Security Misconfiguration — ~10 examples
- Lack of Protection from Automated Threats — ~8 examples
- Improper Inventory Management — ~5 examples
- Unsafe API Consumption — ~10 examples

Total ~100 examples. Effort estimate: ~80 hr after this roadmap's harness is mature. Ships as `scthornton/securecode-api`.

**`securecode-web` v2.6 — severity rebalance (placeholder).**

External reviewer noted the dataset is heavily critical/high severity (~64% CRITICAL, 32% HIGH) which creates "an unrealistic security prior" — a model trained on this expects everything to be critical. v2.6 would add ~100 medium/low-severity examples plus some "ordinary safe code" baselines (functions that are simply correct, not tricky-but-safe like v2.2 negatives).

Effort: ~60 hr. Position as a quality-and-balance release.

### 14.4 Still acknowledged gaps (genuinely out of scope)

These remain out of scope:

| Gap | Why out of scope | Future home |
|---|---|---|
| **Mobile (Android/iOS)** | Domain shift; needs mobile-sec expertise. Doing it mediocre hurts more than skipping. | Indefinite — revisit if external mobile-sec reviewer joins |
| **Cross-language attack chains** | Real but rare class. | Future special-edition release if demand surfaces |
| **Compliance-driven examples** (PCI-DSS, HIPAA, SOC2) | Audience overlap with web/infra is partial. | Possibly future `securecode-compliance` sibling |
| **Localization** (non-English) | English-first is the norm. | Community-contributed translations after dataset stabilizes |
| **AI-assisted attack chains** | Bridges Web and AI/ML. | Joint expansion of Web + AI/ML datasets |

### 14.5 Upgrade contract for users

Versioning commitments downstream consumers can rely on:

- **Patch versions (v2.1.x)**: backward-compatible bug fixes. Safe to auto-update.
- **Minor versions (v2.x.0)**: backward-compatible feature additions (new metadata fields, new examples). Existing field semantics preserved. Safe to auto-update for most consumers; users with strict pipelines should pin.
- **Major versions (v3.0)**: breaking changes (schema reshape, format break). Pinned consumers stay on prior major version; new consumers opt in explicitly.
- **Pre-releases (vX.Y.Z-rcN)**: not for production. Tagged feedback windows.

The pinning convention: `load_dataset("scthornton/securecode-web", revision="v2.1.0")` is the recommended way to lock to a specific version. Default `main` follows latest stable.

Add this contract to the dataset card during Phase 1 ship. Establishes expectations early.

---

## 15. License strategy (added after external review)

### The problem

SecureCode Web ships under **CC BY-NC-SA 4.0**. The non-commercial clause blocks most enterprise fine-tuning, since training a commercial product on NC-licensed data is generally prohibited. External reviewer correctly flagged: *if the goal is reference-benchmark adoption, license strategy can't stay out of scope.*

The current license was a defensive choice (prevent freeloaders monetizing the work). It also caps adoption in exactly the population that would otherwise cite the dataset most: enterprise security teams, AI-coding-assistant vendors, fine-tuning infrastructure providers.

### Options to evaluate

Five paths, ordered roughly from most-conservative to most-permissive:

**1. Status quo — keep CC BY-NC-SA 4.0 across all releases.**
- Pro: simple, defensible, aligns with research-paper norms.
- Con: caps commercial adoption indefinitely. Most enterprise users won't engage.

**2. Dual licensing — CC BY-NC-SA + commercial license on request.**
- Pro: lets commercial users get permission while keeping NC default for casual users. Several major datasets do this (e.g., Llama license model).
- Con: requires you to operate a licensing process (email, contracts, payment). Real overhead.

**3. Permissive license for verified subset, NC for the rest.**
- Pro: the executable-verification subset (12 in pilot, scaling to ~50 in v2.5) becomes the "benchmark" portion under permissive license (CC BY 4.0 or Apache 2.0). Bulk training data stays NC.
- Pro: aligns with industry norms — benchmarks are usually permissive, training corpora often aren't.
- Con: more complex licensing surface. Users must understand which subset they're using.

**4. Migrate to CC BY 4.0 across the board.**
- Pro: maximum adoption, citation-friendly, simplest.
- Con: anyone can train commercial models on it without compensation. Loses the protection.

**5. Hybrid: CC BY 4.0 for new releases (v2.4+), preserve CC BY-NC-SA on legacy v2.0 baseline.**
- Pro: signals "we want adoption going forward" without retroactively changing what existing users licensed.
- Con: requires careful documentation of which examples have which license. Schema needs a `metadata.license` field.

### Recommendation

**Path 3 — permissive for verified subset, CC BY-NC-SA for the rest.** Specifically:

- v2.4 pilot ships the 12 verified examples under **CC BY 4.0** (or Apache 2.0)
- v2.5 scales the verified subset to ~50, all under the permissive license
- Bulk dataset (1,378 baseline + framework additions + future generated content) stays CC BY-NC-SA 4.0
- Add `metadata.license` field; existing examples default to `"CC-BY-NC-SA-4.0"`, verified subset gets `"CC-BY-4.0"`
- Dataset card prominently explains the dual-license structure

This path:
- Preserves the protection on bulk content (where freeloader risk is real)
- Releases the verified subset (where adoption value is highest) under terms commercial users can accept
- Aligns with industry: benchmarks are permissive, training corpora are restricted
- Doesn't retroactively change existing users' license rights

### Action items

- [ ] **Before v2.4 ships**: Scott decides path (1–5)
- [ ] If path 3: schema field added, license headers in `verification/` directories, dataset-card updated
- [ ] Public note at v2.4 release explaining the dual-license rationale
- [ ] Consider creating a `LICENSE-VERIFIED` file in the repo for the permissive-licensed subset

### What this is not

This roadmap **does not** commit to a license change unilaterally. It commits to *making the decision explicit and on-the-record* before v2.4 ships. The current default is path 1 (status quo); if that's the right call, fine — but it should be a deliberate decision, not an unexamined inheritance from v2.0.

---

## 16. Success metrics

### v2.1 metadata
- [ ] HF weekly downloads flat or up (no regression from added fields)
- [ ] At least 3 downstream tools/papers reference the new metadata fields within 6 months
- [ ] Zero reported "derived metadata was treated as authoritative when it shouldn't have been" complaints (confidence markers worked)

### v2.2 negatives
- [ ] Fine-tune one existing SecureCode model with negatives included; measure FP rate on the Task 2.3 held-out eval. **Target: ≥30% relative FP-rate reduction. Publish actual numbers regardless.**
- [ ] **FN-rate regression check**: ≤5% absolute increase. No silent regression on detecting real vulnerabilities.
- [ ] Zero reported "negative example was actually a vuln" incidents in first 180 days
- [ ] External reviewer's findings published (positive or negative) in dataset card

### `securecode-infra` v0.1
- [ ] Sibling dataset published with own citation surface
- [ ] At least one cloud-security-focused citation within 6 months
- [ ] CI/CD content (GitHub Actions + npm) referenced by at least one supply-chain-security tool/paper within 12 months

### v2.4 verification pilot
- [ ] All 12 verifications pass locally and in CI
- [ ] At least one external user reproduces verification on their own machine
- [ ] Pilot lessons doc published; v2.5 scaling decision made on its basis
- [ ] Methodology cited or copied by at least one other security dataset within 12 months

### Phase 5 v3.0 agentic (only if pursued)
- [ ] Decision criteria from §7 met before invocation
- [ ] Fine-tune on agentic track; publish before/after metrics
- [ ] HF `agentic` config downloads reach 10% of default-config downloads within 6 months
