#!/usr/bin/env python3
"""
SecureCode Web v2.1 — Composite Example Heuristic Enrichment (Pass 2)

For composite (no-CVE) examples that couldn't be measured via EPSS/NVD APIs,
apply transparent severity- and category-based heuristics. Every field added
here carries `*_confidence: "approximated"` and a `*_source` marker explaining
the derivation, so users can filter on or trust each field accordingly.

This pass intentionally skips full CVSS v3.1 vectors. CVSS without ground
truth is too lossy. We do derive `preconditions` (auth_required, network
position, user_interaction, prior_access) from the example's category +
severity + business_impact text, since those are the actually-useful filter
dimensions for downstream tools.

EPSS approximation (from severity bucket):
  CRITICAL → percentile 0.90, score 0.30  (top 10% — most exploitable)
  HIGH     → percentile 0.70, score 0.05
  MEDIUM   → percentile 0.40, score 0.005
  LOW      → percentile 0.10, score 0.001

These buckets approximate the FIRST.org EPSS distribution where the median
CVE has percentile ~0.5 and CRITICAL CVEs cluster in the top decile.

Preconditions: per-category defaults overridden by business_impact text:
  injection / ssrf / xxe / deserialization → pre-auth, internet-facing
  broken_access_control / privilege_escalation → post-auth
  xss → passive UI required, auth varies
  csrf → active UI required, victim must be authenticated
  vulnerable_components → varies; default conservative (auth required)
  cryptographic_failures → varies; default network-internet, no UI

Usage:
    python scripts/enrich_composites.py --dry-run     # preview
    python scripts/enrich_composites.py               # write
    python scripts/enrich_composites.py --sample 10   # show sample of decisions

Operates only on examples without context.cve. Examples with a CVE were
already enriched by enrich_metadata.py and are skipped here.
"""

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
ARCHIVED_DIR_NAME = "_archived_duplicates"

ENRICHMENT_DATE = datetime.now().strftime("%Y-%m-%d")
ENRICHMENT_VERSION = "v2.1.0-composite-heuristic"

# ---------------------------------------------------------------------------
# Heuristic tables
# ---------------------------------------------------------------------------

# Severity → EPSS approximation
SEVERITY_TO_EPSS = {
    "CRITICAL": {"score": 0.30, "percentile": 0.90},
    "HIGH":     {"score": 0.05, "percentile": 0.70},
    "MEDIUM":   {"score": 0.005, "percentile": 0.40},
    "LOW":      {"score": 0.001, "percentile": 0.10},
}

# Category → default preconditions
# Returns: (auth_required, network_position, user_interaction, prior_access)
CATEGORY_DEFAULTS = {
    "injection":               (False, "internet", "none", "none"),
    "broken_authentication":   (False, "internet", "none", "none"),
    "auth_failures":           (False, "internet", "none", "none"),
    "authentication_failures": (False, "internet", "none", "none"),
    "broken_access_control":   (True,  "internet", "none", "authenticated_user"),
    "ssrf":                    (False, "internet", "none", "none"),
    "cryptographic_failures":  (False, "internet", "none", "none"),
    "vulnerable_components":   (False, "internet", "none", "none"),
    "integrity_failures":      (True,  "internet", "passive", "authenticated_user"),
    "logging_failures":        (True,  "internet", "none", "privileged"),
    "security_misconfiguration": (False, "internet", "none", "none"),
    "insecure_design":         (False, "internet", "none", "none"),
    "xss":                     (False, "internet", "passive", "none"),
    "csrf":                    (True,  "internet", "active", "authenticated_user"),
    "xxe":                     (False, "internet", "none", "none"),
    "path_traversal":          (False, "internet", "none", "none"),
    "deserialization":         (False, "internet", "none", "none"),
    "command_injection":       (False, "internet", "none", "none"),
    "sql_injection":           (False, "internet", "none", "none"),
}

# Subcategory overrides (more specific than category)
SUBCATEGORY_DEFAULTS = {
    "idor":                  (True,  "internet", "none", "authenticated_user"),
    "privilege_escalation":  (True,  "internet", "none", "authenticated_user"),
    "csrf":                  (True,  "internet", "active", "authenticated_user"),
    "xss":                   (False, "internet", "passive", "none"),
    "stored_xss":            (False, "internet", "passive", "none"),
    "dom_xss":               (False, "internet", "passive", "none"),
    "reflected_xss":         (False, "internet", "active", "none"),
    "ssrf":                  (False, "internet", "none", "none"),
    "session_fixation":      (False, "internet", "active", "none"),
    "session_hijacking":     (False, "internet", "passive", "none"),
}

# Business-impact text overrides — applied AFTER category default
TEXT_OVERRIDES = [
    # auth_required overrides
    (re.compile(r"\b(unauthenticated|pre-?auth(ent\w*)?|no auth(?:ent\w*)? (?:required|needed))\b", re.I),
     "auth_required", False),
    (re.compile(r"\b(authenticated user|logged.in user|valid (?:session|credentials)|after login|requires login)\b", re.I),
     "auth_required", True),

    # network_position overrides
    (re.compile(r"\b(internal|intranet|VPN|behind firewall|air-gapped|trusted network)\b", re.I),
     "network_position", "internal"),
    (re.compile(r"\b(adjacent network|same subnet|local network)\b", re.I),
     "network_position", "adjacent"),
    (re.compile(r"\b(physical access|local-only|local file system)\b", re.I),
     "network_position", "local"),

    # user_interaction overrides
    (re.compile(r"\b(victim (?:clicks?|opens?)|social engineering|phishing|user must (?:click|visit|open))\b", re.I),
     "user_interaction", "active"),
    (re.compile(r"\b(victim (?:views?|loads?)|page load triggers|automatic on visit)\b", re.I),
     "user_interaction", "passive"),
]


# ---------------------------------------------------------------------------
# I/O helpers (mirror migrate_owasp_2025.py / enrich_metadata.py)
# ---------------------------------------------------------------------------


def detect_format_and_parse(path: Path):
    text = path.read_text()
    try:
        obj = json.loads(text)
        if isinstance(obj, dict) and "id" in obj:
            return "single_object", [obj]
    except json.JSONDecodeError:
        pass
    examples = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            if isinstance(obj, dict) and "id" in obj:
                examples.append(obj)
        except json.JSONDecodeError:
            pass
    if examples:
        return "line_per_example", examples
    return None, []


def write_examples(path: Path, examples, format: str) -> None:
    if format == "single_object":
        path.write_text(json.dumps(examples[0], ensure_ascii=False, indent=2) + "\n")
    elif format == "line_per_example":
        with open(path, "w") as f:
            for ex in examples:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")


def iter_data_files():
    for path in sorted(DATA_DIR.rglob("*.jsonl")):
        if ARCHIVED_DIR_NAME in path.parts:
            continue
        if path.name.lower() == "batch_007_corrections.jsonl":
            continue
        if path.stat().st_size == 0:
            continue
        yield path


# ---------------------------------------------------------------------------
# Heuristic application
# ---------------------------------------------------------------------------


def apply_heuristics(metadata: dict, context: dict) -> tuple:
    """Return (epss_dict, preconditions_dict, source_notes) or (None, None, [])."""
    severity = (metadata.get("severity") or "").upper()
    category = (metadata.get("category") or "").lower()
    subcategory = (metadata.get("subcategory") or "").lower()
    business_impact = (context.get("business_impact") or "")

    # EPSS bucket
    epss = SEVERITY_TO_EPSS.get(severity)

    # Preconditions: subcategory > category > generic default
    if subcategory in SUBCATEGORY_DEFAULTS:
        auth, net, ui, prior = SUBCATEGORY_DEFAULTS[subcategory]
        precondition_basis = f"subcategory_{subcategory}"
    elif category in CATEGORY_DEFAULTS:
        auth, net, ui, prior = CATEGORY_DEFAULTS[category]
        precondition_basis = f"category_{category}"
    else:
        # Generic fallback
        auth, net, ui, prior = (False, "internet", "none", "none")
        precondition_basis = "generic_fallback"

    # Apply text-based overrides
    overrides_applied = []
    for pattern, field, value in TEXT_OVERRIDES:
        if pattern.search(business_impact):
            if field == "auth_required":
                if auth != value:
                    auth = value
                    overrides_applied.append(field)
            elif field == "network_position":
                if net != value:
                    net = value
                    overrides_applied.append(field)
            elif field == "user_interaction":
                if ui != value:
                    ui = value
                    overrides_applied.append(field)

    preconditions = {
        "auth_required": auth,
        "network_position": net,
        "user_interaction": ui,
        "prior_access": prior,
    }

    return epss, preconditions, {"basis": precondition_basis, "text_overrides": overrides_applied}


def enrich_composite_in_place(entry: dict, stats: Counter, sample_log: list) -> bool:
    metadata = entry.setdefault("metadata", {})
    context = entry.get("context", {})

    # Skip if has CVE (already done by Pass 1)
    if context.get("cve"):
        return False

    # Skip if already approximated (idempotent)
    if metadata.get("epss_confidence") == "approximated":
        return False

    epss, preconditions, basis = apply_heuristics(metadata, context)
    any_added = False

    # EPSS approximation
    if epss and "epss_score" not in metadata:
        metadata["epss_score"] = epss["score"]
        metadata["epss_percentile"] = epss["percentile"]
        metadata["epss_date"] = ENRICHMENT_DATE
        metadata["epss_source"] = "derived_from_severity_bucket_v2.1"
        metadata["epss_confidence"] = "approximated"
        stats["epss_approximated"] += 1
        any_added = True

    # Preconditions
    if preconditions and "preconditions" not in metadata:
        metadata["preconditions"] = preconditions
        metadata["preconditions_source"] = (
            f"derived_from_{basis['basis']}_with_business_impact_text"
        )
        metadata["preconditions_confidence"] = "approximated"
        if basis["text_overrides"]:
            metadata["preconditions_text_overrides"] = basis["text_overrides"]
        stats["preconditions_approximated"] += 1
        any_added = True

    if any_added:
        provenance = metadata.setdefault("provenance", {})
        provenance["composite_heuristic_date"] = ENRICHMENT_DATE
        provenance["composite_heuristic_version"] = ENRICHMENT_VERSION

        # Sample log
        if len(sample_log) < 10:
            sample_log.append({
                "id": entry.get("id"),
                "severity": metadata.get("severity"),
                "category": metadata.get("category"),
                "subcategory": metadata.get("subcategory"),
                "business_impact_excerpt": (context.get("business_impact") or "")[:80],
                "epss_score": metadata.get("epss_score"),
                "epss_percentile": metadata.get("epss_percentile"),
                "preconditions": metadata.get("preconditions"),
                "preconditions_basis": basis["basis"],
                "text_overrides": basis["text_overrides"],
            })

    return any_added


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--dry-run", action="store_true", help="Preview, no writes")
    parser.add_argument("--sample", type=int, default=0,
                        help="Print N decisions before/after summary")
    args = parser.parse_args()

    print("=" * 80)
    print("SecureCode Web v2.1 — Composite Heuristic Enrichment (Pass 2)")
    print(f"Mode: {'DRY-RUN' if args.dry_run else 'LIVE'}")
    print("=" * 80)

    stats = Counter()
    sample_log = []
    files_modified = 0

    for path in iter_data_files():
        format, examples = detect_format_and_parse(path)
        if not examples:
            continue
        modified = False
        for ex in examples:
            stats["total_examples"] += 1
            if ex.get("context", {}).get("cve"):
                stats["skipped_has_cve"] += 1
                continue
            stats["composite_total"] += 1
            if enrich_composite_in_place(ex, stats, sample_log):
                modified = True
        if modified:
            files_modified += 1
            if not args.dry_run:
                write_examples(path, examples, format)

    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    print(f"Total examples scanned:         {stats['total_examples']}")
    print(f"  Skipped (had CVE):            {stats['skipped_has_cve']}")
    print(f"  Composite (target):           {stats['composite_total']}")
    print()
    print(f"Heuristic fields added:")
    print(f"  EPSS approximated:            {stats['epss_approximated']}")
    print(f"  Preconditions approximated:   {stats['preconditions_approximated']}")
    print(f"Files modified:                 {files_modified}")

    if args.sample or sample_log:
        print("\nSample decisions (first 10):")
        for entry in sample_log:
            print(f"\n  id: {entry['id']}")
            print(f"    severity={entry['severity']}, category={entry['category']}, subcategory={entry['subcategory']}")
            print(f"    business_impact: {entry['business_impact_excerpt']}...")
            print(f"    EPSS: score={entry['epss_score']} percentile={entry['epss_percentile']}")
            print(f"    Preconditions: {entry['preconditions']}")
            print(f"      (basis: {entry['preconditions_basis']}; text_overrides: {entry['text_overrides']})")

    if args.dry_run:
        print("\n✓ Dry-run complete.")
    else:
        print("\n✓ Composite enrichment complete.")


if __name__ == "__main__":
    main()
