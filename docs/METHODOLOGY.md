# Upgrading SecureCode Web: A Multi-Tier Generation Methodology

*Working draft — evolves into published update articles as phases ship.*
*Last updated: 2026-04-24 (post external-review revision).*

---

## The problem with popular datasets

SecureCode Web hit 1,378 examples and got popular. That's a good problem and a trap. Once a dataset has real users, every change risks breaking fine-tuning pipelines that reference the schema, the splits, the field names. The easy path is to stop shipping. The hard path is to keep shipping while maintaining backward compatibility, quality, and trust.

This article documents how we're upgrading SecureCode Web without breaking the users who already depend on it.

The short version: we built a multi-tier generation methodology. Frontier cloud models do safety-critical generation and adversarial review. A local 26B mixture-of-experts model on DGX Spark hardware handles validation, triage, and high-volume support tasks. Deterministic validators enforce structural rules. On top of that, the author personally adjudicates every safety-critical example using Claude Opus 4.7 as an interactive review tool — and an external security professional reviews a 10% random sample before each public release.

The result is a pipeline with multiple independent quality gates at modest cloud cost, with provenance and reject-reason logs that hold up to audit.

Here's how it works.

---

## The upgrade targets

Four releases ship in roughly seven to ten months. A fifth waits on evidence.

**v2.1 — metadata enrichment.** Users today filter by severity and OWASP category. That's coarse. We're adding EPSS scores (exploitability probability), MITRE ATT&CK technique mapping, CAPEC mapping, and explicit preconditions (authentication required, network position, user interaction) to every example. Every enriched field carries a confidence and source marker — `epss_source: "first.org_epss_api_v3"`, `attack_techniques_source: "derived_from_cwe_via_mitre_mapping"` — so users can distinguish measured fields from heuristic derivations.

The OWASP Top 10:2025 migration runs as part of this release. Critically, it's non-breaking. The old `owasp_2021` field gets preserved as `owasp_2021_legacy` so existing pipelines don't snap. Users opting into the new taxonomy do so explicitly.

**v2.2 — safe-but-suspicious negatives.** Every example today follows the same shape: vulnerable code, then the fix. A model trained on that pattern learns to flag anything that *looks* dangerous, even when it isn't. We're adding ~100 examples where the code looks wrong but is demonstrably safe — `dangerouslySetInnerHTML` on DOMPurify-sanitized content, weak hashes used unambiguously for non-security purposes, hardcoded constants whose names make their public nature legible.

The version we'll ship is meaningfully better than my original sketch, after multiple rounds of review. Three things changed.

First, picking the negative patterns by intuition risked generating examples that don't correspond to where deployed models actually over-flag. So Phase 2 begins by running our 8 existing fine-tuned models against ~500 random functions from real GitHub repos, cataloguing what they over-flag, and deriving the patterns from that data.

Second, claiming "30% reduction in false positives" is unfalsifiable without a defined eval. So the phase also curates a 200-safe-plus-200-vulnerable test set with baseline numbers measured before generation begins. The post-fine-tune delta gets published regardless of whether it hits the target. We measure both false-positive reduction *and* false-negative regression — making sure we don't teach the model to excuse real vulnerabilities while reducing false alarms.

Third, several pattern categories from the original list got dropped. Categories like "safe `eval` with allowlist" or "intentionally permissive CORS" depend on safety claims about the *environment* rather than safety enforced *in the code*. A model trained on those examples learns to rationalize bad patterns. The kept patterns all share a property: a reader looking only at the example can verify the safety claim from the code itself, not from prose explanations.

**`securecode-infra` v0.1 — Infrastructure & Supply Chain (new sibling dataset).** Originally scoped as "v2.3 IaC inside Web." Critical assessment changed it: IaC and supply chain belong in a separate sibling, not folded into Web. Two reasons. The audience is different (cloud security engineers, not app sec engineers). And the original scope of 80 examples missed where 2024–2025 breaches actually live — the XZ Utils backdoor, Polyfill.io supply chain compromise, GitHub Actions injection via `pull_request_target`, malicious npm postinstall scripts. None of that fits Terraform or Kubernetes manifests cleanly.

So Phase 3 ships a new sibling dataset `scthornton/securecode-infra` with 90 examples: 30 Terraform, 30 Kubernetes, and 30 covering GitHub Actions injection plus npm supply chain attacks. (GitLab CI, Jenkins, Cargo, and Go module supply chain defer to v0.2 — narrowing the v0.1 scope keeps it deliverable.) Detection-rule integration covers Checkov, tfsec, Falco, kube-bench, sigstore, OSV, and GitHub's secret scanning. The pattern matches the existing `scthornton/securecode-aiml` sibling.

**v2.4 — executable verification (pilot).** This is the dataset's actual differentiator. Every other "secure code" dataset claims rigorous validation; none ship reproducible proof. v2.4 makes "validated" mean *exploited and verified-fixed*, not *human read it*.

For 12 carefully-selected critical examples, we ship a Dockerfile plus exploit script plus verify harness. The harness builds a vulnerable container, runs the documented exploit, confirms it succeeds. Then builds a secure container, runs the same exploit, confirms it fails. CI runs the same on every pull request. Output: `validation.code_execution: passed` is no longer a human attestation. It's a CI-checked, anyone-can-reproduce claim.

The pilot is deliberately small. The original plan was 50 examples; external review correctly noted that was too aggressive as a first commitment. Some bug classes — Java/Spring deserialization, complex SSRF chains, auth-flow exploits — take half a day or more to verify properly. The pilot proves out the per-example template, Docker patterns, exploit-drift handling, and CI runtime budget across 12 examples spanning SQL injection, command injection, SSRF, stored XSS, and JWT auth bypass. A separate v2.5 release scales to ~50 once the pilot exposes the real per-example cost.

This was originally deferred to a future v4.0; the critical assessment moved it up. Even at 12 examples, it's the credibility multiplier that makes other releases trustworthy.

**v3.0 — agentic review loops (deferred 6 months).** The original plan committed 320 hours to a format nobody has yet proven helps fine-tuning. No major actor — Anthropic, OpenAI, Cursor, Cline, Aider, Copilot Workspace — has published "we trained on agentic-loop data and metrics improved." The format is also still settling. Building our own schema today might not match whatever standard emerges.

So v3.0 is deferred. Six months after v2.4 ships, decision point with explicit criteria: a major framework publishes positive fine-tuning results, *or* a canonical multi-agent schema emerges, *or* a peer-reviewed agentic eval benchmark appears. If none of those happen, we skip and reallocate the budget — likely to scaling executable verification or addressing OWASP API Top 10.

---

## The three-tier generation stack

Generating dataset examples at quality requires two things that pull in opposite directions: strong reasoning and high volume. Frontier cloud models have the reasoning but cost and rate-limit quickly. Local open-source models are fast and free but weaker on edge cases. Deterministic validators catch structural issues reliably but can't evaluate meaning.

The insight is that most of the work isn't generation. It's validation, triage, classification, first-pass drafting, and documentation — tasks that don't need frontier quality. Separate those out and run them locally, and the frontier budget goes much further.

Our stack:

**Tier 1 — frontier cloud.** Anthropic Claude Sonnet 4.6 and OpenAI GPT-5.4. Used for all safety-critical generation and adversarial review. Every safety-critical example is generated by one frontier provider and independently reviewed by the other. The cold reviewer doesn't see the generator's rationale — it only sees the code, with the question "is this code exploitable as written?" That breaks the anchoring effect where a reviewer reading a persuasive "this is safe because…" explanation tends to accept it.

When the two strong independent models agree the code is safe, it goes to the human adjudicator. When they disagree, it goes to full human review immediately.

**Tier 2 — local.** Gemma 4 26B-A4B on DGX Spark, Q8_0 quantized, running on `llama-server` with an OpenAI-compatible endpoint at `localhost:8080`. The mixture-of-experts architecture means roughly 4B active parameters at inference time — fast enough for real-time use in a validation pipeline. This tier handles schema conformance checks beyond regex, triage and classification of outputs into pattern categories, first-pass drafts of formulaic content, commit message drafting from diffs, progress log summarization, duplicate detection via embeddings, and prompt linting before cloud calls.

**Tier 3 — deterministic.** Regex validators, JSON schema validators, Python scripts like `validate_contributing_compliance_v2.py`. These catch what they catch — structural issues, format violations, missing required fields — and never produce false negatives on the specific checks they implement.

The routing is explicit. Generator and reviewer roles always go to Tier 1, always different providers from each other. Validation tries Tier 3 first and falls back to Tier 2 for semantic checks. Tier 2 never replaces Tier 1 for safety-critical judgment, but it handles the high-volume support work that doesn't need frontier quality.

---

## The human adjudication layer

Cross-model review between Anthropic and OpenAI is strong, but it's not enough on its own. Two failure modes are well-documented in the literature: model collusion (both models making the same subtle mistake) and prompt-template artifacts (a flawed prompt produces 20 systematically flawed examples).

So there's a fourth layer above the three-tier generation stack: I (Scott) personally adjudicate every safety-critical example using Claude Opus 4.7 as an interactive review tool.

The pattern works like this. After a batch passes cross-model review and deterministic validators, the harness outputs a markdown bundle of the batch. I open it in Claude Code with Opus 4.7 and walk through example-by-example. Opus helps me try to exploit the "safe" code in negatives, verify the Turn 2 "what would make this unsafe" section is technically correct, catch voice or style inconsistencies, and suggest specific corrections with diffs. Approved corrections get applied back to the source files. Rejections go into a published reject-reason log alongside the dataset, so future readers can see what was tried and why it didn't pass.

This is not "Scott + Opus replaces human review." Scott is the accountable reviewer; Opus is the assistive tool. Earlier drafts of this methodology framed the layers as alternatives — automated cross-model review *or* Scott + Opus review. External review correctly pointed out that's a false choice. Both layers catch different things, and both are needed.

There's still one more gate before public release. An external security professional reviews a 10% random sample of safety-critical content before any v2.2-style release ships. This catches the failure modes the rest of the pipeline shares — author blind spots, batch fatigue effects, cumulative anchoring across a long review session. If no external reviewer is available for a release, the dataset card explicitly discloses single-author review. Honest framing beats false claims.

---

## Provenance and reject reasons

Every generated example carries a provenance record. Which model generated it, with what date snapshot. Which prompt template, with a SHA-256 hash of the template content. Which review session approved it. What corrections were applied. What schema version the example targets.

This solves three problems. Drift detection: if dataset quality declines six months from now, we can correlate with model snapshot dates or prompt template versions. Targeted recalls: if a prompt template turns out to have a subtle bug, we can identify exactly which examples used that template and re-generate them. Reproducibility claims: anyone can verify "this example was generated by Claude Sonnet 4.6 dated 2026-01-01 with prompt template `negatives-v2` (hash X) and reviewed in session `review-2026-06-15-batch-03`."

The reject-reason log is the asymmetric companion. Every candidate example that *fails* an acceptance gate is logged separately. Each reject record includes the candidate content, the stage it failed (cold reviewer, Scott/Opus adjudication, external reviewer, FP-eval regression), and the specific reason. Logs ship as separate artifacts alongside each release, not loaded by default.

This matters for transparency. A dataset that publishes only its accepted examples shows you successes. A dataset that publishes its accepted examples *plus* its rejection log shows you methodology. Reviewers can audit not just what got in but what tried and didn't, and clustering reject reasons surfaces systemic issues — "everything in this pattern category got rejected for the same exploit class, maybe the pattern category itself needs rethinking."

---

## The phase-based execution model

Upgrades at this scale don't fit in a single sprint. The total committed work across Phases 1–4 is roughly 405 hours, with another ~150 hours for v2.5 to scale executable verification, plus another ~360 hours if Phase 5 (agentic) is pursued at the decision point. Splitting into discrete phases with clear shipping milestones keeps momentum visible and lets users benefit from each release rather than waiting for a bundle.

**Phase 1 ships v2.1.** First task is reconciling a taxonomy drift between our GitHub and Hugging Face repos — GitHub has been migrated to OWASP Top 10:2025, HF is still on 2021, and the two have never been synced. The migration is non-breaking: dual fields preserve `owasp_2021` for legacy consumers while adding `owasp_2025`. Second task is the enrichment itself: EPSS, ATT&CK, CAPEC, CVSS v3/v4, preconditions, all with confidence and source markers.

**Phase 2 ships v2.2.** First task is building the cross-model generation harness — the shared infrastructure used by Phases 2, 3, and 5. Provider abstraction over Anthropic, OpenAI, and Gemma 4. Cold-reviewer routing where the reviewing provider doesn't see the generator's rationale. Reject-reason logging. Budget tracking. Then come the two prerequisite tasks added after critical review: deriving the negative pattern taxonomy from data (running existing fine-tuned models against 500 GitHub functions, cataloguing what they over-flag) and curating the FP/FN-rate eval baseline (200 safe + 200 vulnerable test set, baseline measured before any negatives generation begins). Finally the negatives themselves — ~100 examples through the four-layer pipeline, shipping as an opt-in `safe_controls` config that does not modify the default train split.

**Phase 3 ships `securecode-infra` v0.1.** New sibling repository on both GitHub and HF. Reuses the harness from Phase 2 with looser review requirements (IaC examples are more mechanical). The differentiator is detection-rule integration — every Turn 4 includes a concrete Checkov, tfsec, Falco, kube-bench, sigstore, or GitHub Actions security rule that would catch the misconfiguration in production.

**Phase 4 ships v2.4 (pilot).** 12 verified examples spanning major bug classes. New `validation/` subdirectories with Dockerfile + exploit + verify harness per example. CI workflow that runs `verify.sh` on every PR. Pilot lessons document published — what surprised us, where the template broke, which patterns we'd change. The v2.5 scaling decision happens on the basis of the pilot retrospective, not before.

**Phase 5 is deferred.** Agentic review loops. Decision point six months after v2.4 ships, with three explicit criteria, any one of which unlocks invocation. If none are met, the budget reallocates.

---

## Claude as quarterback

The practical question: who runs all this? An ~400-hour committed roadmap is too much for an individual contributor in most time windows. We built an orchestration model where Claude runs phases autonomously within defined authorization boundaries, checkpoints at meaningful decision points, and persists state across sessions via git commits and progress documents.

The invocation is deliberately simple. `execute phase 1` starts Phase 1 from scratch. `resume phase 1` picks up from the last checkpoint. `status` reports where things are. `pause phase 1` commits work-in-progress and hands back. These commands work across many Claude sessions — a phase takes weeks, not hours, and the model's memory doesn't persist between sessions, but git history and progress documents do.

The authorization boundary is explicit. Claude can create files, run local scripts, call APIs within a budget cap, deploy subagents for parallel work, create feature branches, and commit to those branches — all autonomously. Claude cannot merge to main, push to GitHub, push to Hugging Face, change the license, delete existing data, exceed the budget, or change phase scope — all require Scott's approval at a checkpoint.

Checkpoints are mandatory at phase kickoff, at sub-task boundaries, before any cloud API run over $20 estimated, after any generation run before folding results into the dataset, before schema changes, before final release builds, on disagreement spikes above 30%, and when budget exceeds 80%. At each checkpoint Claude posts a structured status block — what's done, what's next, budget used, risks, what it's waiting on — and stops.

Subagents handle parallelizable work. A code-analysis-wizard reviewing generated negatives. An ai-redteam-pentester trying to exploit each candidate negative as an adversarial second opinion. An ai-security-researcher building the incident library for Phase 3. A qa-testing-expert writing the acceptance-test matrix. These run in parallel when independent, sequential when one needs the other's output.

The outcome is a pipeline I can invoke in small windows. Thirty minutes on a Tuesday to review a checkpoint and redirect. Two hours on a Saturday to approve a release push. The orchestration absorbs the hundreds of hours of execution around those decision points.

---

## Five things worth highlighting

A few methodological observations from designing this.

**Cost isn't the constraint you'd expect.** Total cloud API spend across Phases 1–4 comes to roughly $100, with another $50 in external reviewer fees and $145 in Scott's Opus review session tokens. Under $300 total. The constraints that actually matter are reviewer attention, quality of the pattern taxonomies, and schema design.

**Local compute changes the calculus.** Having Gemma 4 on DGX Spark wasn't just a cost optimization. It unlocks patterns that would be prohibitively slow or expensive over the wire: embedding-based dedup on every new example, validation on every generator output before it's ever sent to a reviewer, progress documents auto-summarized nightly. These compound.

**The negatives are the hardest release, not the biggest.** v2.2 is small (~100 examples, 145 hours) but has the highest failure cost. Shipping a "safe" example that's actually exploitable would poison downstream models. Most of Phase 2's hours go to four review layers — cold cross-model, deterministic, Scott + Opus adjudication, and external reviewer sample. The harness builds itself in a week; the validation takes most of the phase.

**External review unblocks credibility.** The single most important change after critical review wasn't technical — it was committing to recruit at least one external security professional to review a 10% sample of v2.2 negatives before public release. A dataset with author-only validation can be trusted up to a point. A dataset with author validation plus published external review of a random sample is materially more defensible.

**The agentic deferral is the right call.** Resisting the urge to ship a 320-hour bet on an unproven format saves the budget for executable verification expansion. Six months from now we'll have evidence about whether the agentic ecosystem has converged on a schema, whether anyone has shown fine-tuning improvements, and whether the format is worth committing to. If it is, the harness we built for v2.2 carries over. If not, the budget redirects to gaps that have proven value.

---

## License: an explicit decision, not an inheritance

A note on something the original plan didn't address.

SecureCode Web ships under CC BY-NC-SA 4.0. The non-commercial clause was a defensive choice — prevent freeloaders monetizing the work without attribution or compensation. It also caps adoption in exactly the population that would otherwise cite the dataset most: enterprise security teams, AI-coding-assistant vendors, fine-tuning infrastructure providers.

Before v2.4 ships, we'll make the license decision explicit and on-the-record. The current default is to keep CC BY-NC-SA. The current recommendation in the roadmap is to release the executable-verification subset under a more permissive license (CC BY 4.0 or Apache 2.0) while keeping the bulk dataset under the existing license — aligning with industry norms where benchmarks are permissive and training corpora aren't.

Whichever path we pick, the point is to pick deliberately rather than inherit a 2024 decision into 2027 by default.

---

## Article variants

This methodology document evolves into published updates as phases ship:

- **Pre-launch:** "Upgrading a Popular Security Dataset: A Multi-Tier Methodology" (perfecXion.ai) — the forward-looking plan, including the multi-layer review architecture and the deliberate scope reductions after external review.
- **Post-v2.1:** "Enriching 1,378 Security Examples with EPSS, MITRE ATT&CK, and Confidence Markers" (HuggingFace blog) — the metadata enrichment story, with the fully-automated pipeline walkthrough and the case for confidence/source markers on derived metadata.
- **Post-v2.2:** "Cross-Model Adversarial Review Plus Author Adjudication: Catching What a Single Reviewer Misses" (perfecXion.ai) — the headline methodology piece. Disagreement rates, false-positive reductions measured against published baseline, the dropped pattern categories and why.
- **Post-`securecode-infra` v0.1:** "Detection-Rule-Integrated Infrastructure & Supply Chain Training Data" (HuggingFace blog) — the differentiator for the cloud-security audience.
- **Post-v2.4:** "Reproducibly Verified Security Examples: A Pilot Methodology" (perfecXion.ai) — the executable-verification pilot, with lessons learned and the v2.5 scaling decision.
- **Post-v3.0 (if pursued):** "An Agentic-Review-Loop Dataset for the Agent Fine-Tuning Era" (perfecXion.ai) — the format story, plus eval results on a fine-tuned model.

Each variant inherits this document's core — multi-tier stack, layered review, phase-based execution — and layers release-specific narrative, metrics, and lessons on top.

---

*This document is the source-of-truth methodology narrative; release-specific articles are derivations. Versioned alongside ROADMAP.md.*
