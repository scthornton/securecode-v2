#!/usr/bin/env python3
"""
SecureCode Web v2.1: OWASP Top 10:2021 → 2025 NON-BREAKING Migration

Adds metadata.owasp_2025 alongside the existing metadata.owasp_2021 field.
Existing consumers querying owasp_2021 keep working; new consumers can opt
into owasp_2025.

Also performs five pre-approved data corrections (Scott approved 2026-04-25):

1. AI/ML examples in data/ai_security_batch_103-107.jsonl have already been
   moved to data/_archived_duplicates/ai_ml_removed/ before this script runs.
   Script does NOT process the archived directory.
2. data/sql_advanced_batch_010.jsonl was empty and has been deleted.
3. 60 examples in sql_batch_201.jsonl with owasp_2021="Unknown" + cwe="CWE-000"
   are corrected: owasp_2021 → "A03:2021-Injection", cwe → "CWE-89" (SQL
   injection). These are SQL injection examples per category/subcategory.
4. 10 examples (express_js-injection-*) with truncated owasp_2021="A03"
   are corrected to owasp_2021 = "A03:2021-Injection".
5. 2 examples with owasp_2021="A10:2021-Server-Side Request Forgery (SSRF)"
   are normalized to "A10:2021-Server-Side Request Forgery" (canonical form
   matching the other 49 SSRF examples).

OWASP 2025 mapping uses FINAL labels verified from owasp.org/Top10/2025/
on 2026-04-25:

    A01:2021 Broken Access Control                    → A01:2025 Broken Access Control
    A02:2021 Cryptographic Failures                   → A04:2025 Cryptographic Failures
    A03:2021 Injection                                → A05:2025 Injection
    A04:2021 Insecure Design                          → A06:2025 Insecure Design
    A05:2021 Security Misconfiguration                → A02:2025 Security Misconfiguration
    A06:2021 Vulnerable and Outdated Components       → A03:2025 Software Supply Chain Failures
    A07:2021 Identification and Authentication Fail.  → A07:2025 Authentication Failures
    A08:2021 Software and Data Integrity Failures     → A08:2025 Software or Data Integrity Failures
    A09:2021 Security Logging and Monitoring Failures → A09:2025 Security Logging and Alerting Failures
    A10:2021 Server-Side Request Forgery              → A01:2025 Broken Access Control (SSRF folded)
    (none)                                            → A10:2025 Mishandling of Exceptional Conditions (NEW; 0 current examples)

Handles two JSONL physical formats per CLAUDE.md:
  - Baseline batches (*_batch_NNN.jsonl): one JSON object per line.
  - Framework files (<framework>-<subcat>-NNNNNN.jsonl): one pretty-printed
    JSON object spanning many lines. Entire file = one example.

Usage:
    python scripts/migrate_owasp_2025.py --dry-run    # validate, report changes
    python scripts/migrate_owasp_2025.py              # execute migration
    python scripts/migrate_owasp_2025.py --rollback   # restore from backup dir

Backups go to backups/pre-v2.1-owasp-migration/<timestamp>/.
"""

import argparse
import json
import shutil
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
BACKUP_BASE = REPO_ROOT / "backups" / "pre-v2.1-owasp-migration"
ARCHIVED_DIR_NAME = "_archived_duplicates"

# OWASP 2021 → 2025 mapping (FINAL labels, verified 2026-04-25 from official source)
OWASP_2021_TO_2025 = {
    "A01:2021-Broken Access Control":
        "A01:2025-Broken Access Control",
    "A02:2021-Cryptographic Failures":
        "A04:2025-Cryptographic Failures",
    "A03:2021-Injection":
        "A05:2025-Injection",
    "A04:2021-Insecure Design":
        "A06:2025-Insecure Design",
    "A05:2021-Security Misconfiguration":
        "A02:2025-Security Misconfiguration",
    "A06:2021-Vulnerable and Outdated Components":
        "A03:2025-Software Supply Chain Failures",
    "A07:2021-Identification and Authentication Failures":
        "A07:2025-Authentication Failures",
    "A08:2021-Software and Data Integrity Failures":
        "A08:2025-Software or Data Integrity Failures",
    "A09:2021-Security Logging and Monitoring Failures":
        "A09:2025-Security Logging and Alerting Failures",
    "A10:2021-Server-Side Request Forgery":
        "A01:2025-Broken Access Control",  # SSRF folded into A01:2025
}

# Data corrections applied during migration (Scott approved 2026-04-25)
SSRF_CANONICAL = "A10:2021-Server-Side Request Forgery"


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------


def detect_format_and_parse(path: Path):
    """Return (format, [examples]).

    format: "single_object" (framework files) or "line_per_example" (batches).
    """
    text = path.read_text()
    # Try whole-file JSON first
    try:
        obj = json.loads(text)
        if isinstance(obj, dict) and "id" in obj:
            return "single_object", [obj]
    except json.JSONDecodeError:
        pass

    # Fall back to JSONL line-by-line
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
    """Write examples back preserving the original physical format."""
    if format == "single_object":
        if len(examples) != 1:
            raise ValueError(
                f"single_object format expects 1 example, got {len(examples)} "
                f"for {path.name}"
            )
        path.write_text(json.dumps(examples[0], ensure_ascii=False, indent=2) + "\n")
    elif format == "line_per_example":
        with open(path, "w") as f:
            for ex in examples:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    else:
        raise ValueError(f"Unknown format: {format}")


def iter_data_files():
    """Yield JSONL files under data/, skipping archived/corrections/empty."""
    for path in sorted(DATA_DIR.rglob("*.jsonl")):
        # Skip archived directory entirely
        if ARCHIVED_DIR_NAME in path.parts:
            continue
        # Skip the one-off corrections record (not part of normal data flow)
        if path.name.lower() == "batch_007_corrections.jsonl":
            continue
        if path.stat().st_size == 0:
            continue
        yield path


# ---------------------------------------------------------------------------
# Migration
# ---------------------------------------------------------------------------


class MigrationStats:
    def __init__(self):
        self.examples_total = 0
        self.examples_migrated = 0
        self.files_processed = 0
        self.fixes_unknown_to_injection = 0
        self.fixes_truncated_a03 = 0
        self.fixes_ssrf_normalized = 0
        self.errors = []
        self.dist_2021_before = Counter()
        self.dist_2021_after = Counter()
        self.dist_2025_after = Counter()


def correct_owasp_2021(entry: dict, stats: MigrationStats) -> str:
    """Apply pre-approved data corrections to owasp_2021 in place.

    Returns the corrected owasp_2021 value.
    """
    metadata = entry.get("metadata", {})
    owasp = metadata.get("owasp_2021")

    # Fix 3: Unknown SQL injection examples in sql_batch_201.jsonl
    if owasp == "Unknown" and metadata.get("category") == "injection" and metadata.get("subcategory") == "sql":
        owasp = "A03:2021-Injection"
        metadata["owasp_2021"] = owasp
        if metadata.get("cwe") == "CWE-000":
            metadata["cwe"] = "CWE-89"
        stats.fixes_unknown_to_injection += 1

    # Fix 4: Truncated "A03" → full label
    elif owasp == "A03":
        owasp = "A03:2021-Injection"
        metadata["owasp_2021"] = owasp
        stats.fixes_truncated_a03 += 1

    # Fix 5: Normalize SSRF variant
    elif owasp == "A10:2021-Server-Side Request Forgery (SSRF)":
        owasp = SSRF_CANONICAL
        metadata["owasp_2021"] = owasp
        stats.fixes_ssrf_normalized += 1

    return owasp


def migrate_entry(entry: dict, stats: MigrationStats, migration_date: str) -> dict:
    """Add owasp_2025 alongside owasp_2021 (non-breaking) + apply corrections."""
    metadata = entry.setdefault("metadata", {})
    owasp_before = metadata.get("owasp_2021")
    stats.dist_2021_before[owasp_before or "MISSING"] += 1

    # Apply data corrections in place (updates owasp_2021)
    owasp_2021 = correct_owasp_2021(entry, stats)

    # Map to 2025
    owasp_2025 = OWASP_2021_TO_2025.get(owasp_2021)
    if owasp_2025 is None:
        # Unknown / unmappable — leave new field absent and log
        stats.errors.append(
            f"Entry {entry.get('id', '?')}: owasp_2021={owasp_2021!r} not in mapping; owasp_2025 left absent"
        )
    else:
        metadata["owasp_2025"] = owasp_2025

    # Provenance — record that this example went through the migration
    provenance = metadata.setdefault("provenance", {})
    provenance["owasp_migration_date"] = migration_date

    # Record what data corrections, if any, were applied to this example
    corrections = []
    if owasp_before == "Unknown" and owasp_2021 == "A03:2021-Injection":
        corrections.append("triaged_unknown_to_injection")
        corrections.append("fixed_cwe_000_to_cwe_89")
    elif owasp_before == "A03" and owasp_2021 == "A03:2021-Injection":
        corrections.append("fixed_truncated_owasp_2021")
    elif owasp_before == "A10:2021-Server-Side Request Forgery (SSRF)":
        corrections.append("normalized_ssrf_label")
    if corrections:
        provenance["owasp_data_corrections"] = corrections

    stats.examples_total += 1
    stats.examples_migrated += 1
    stats.dist_2021_after[owasp_2021 or "MISSING"] += 1
    stats.dist_2025_after[owasp_2025 or "MISSING"] += 1

    return entry


# ---------------------------------------------------------------------------
# Backup / rollback
# ---------------------------------------------------------------------------


def create_backup(timestamp: str) -> Path:
    backup_dir = BACKUP_BASE / timestamp
    backup_dir.mkdir(parents=True, exist_ok=True)

    # Backup all data files (excluding archived dir which is meta-data anyway)
    for path in iter_data_files():
        rel = path.relative_to(DATA_DIR)
        dst = backup_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dst)

    # Also backup parquet files
    for parquet in DATA_DIR.glob("*.parquet"):
        shutil.copy2(parquet, backup_dir / parquet.name)

    return backup_dir


def rollback_from_backup(timestamp: str) -> None:
    backup_dir = BACKUP_BASE / timestamp
    if not backup_dir.exists():
        # Try latest
        candidates = sorted(BACKUP_BASE.glob("*"))
        if not candidates:
            print(f"✗ No backups under {BACKUP_BASE}")
            sys.exit(1)
        backup_dir = candidates[-1]
        print(f"Using latest backup: {backup_dir.name}")

    for path in backup_dir.rglob("*.jsonl"):
        rel = path.relative_to(backup_dir)
        dst = DATA_DIR / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dst)
    for parquet in backup_dir.glob("*.parquet"):
        shutil.copy2(parquet, DATA_DIR / parquet.name)
    print(f"✓ Restored from {backup_dir}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--dry-run", action="store_true",
                        help="Report changes without writing")
    parser.add_argument("--rollback", metavar="TIMESTAMP", nargs="?", const="latest",
                        help="Restore from backup (default: latest)")
    args = parser.parse_args()

    if args.rollback:
        rollback_from_backup(args.rollback if args.rollback != "latest" else "latest")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    migration_date = datetime.now().strftime("%Y-%m-%d")
    stats = MigrationStats()

    print("=" * 80)
    print("SecureCode Web v2.1 — OWASP 2021 → 2025 NON-BREAKING migration")
    print(f"Mode: {'DRY-RUN (no writes)' if args.dry_run else 'LIVE'}")
    print(f"Migration date: {migration_date}")
    print("=" * 80)

    if not args.dry_run:
        print(f"\n→ Creating backup: {BACKUP_BASE / timestamp}")
        backup_dir = create_backup(timestamp)
        print(f"  Backup complete: {sum(1 for _ in backup_dir.rglob('*.jsonl'))} JSONL + "
              f"{sum(1 for _ in backup_dir.glob('*.parquet'))} parquet files")

    # Process every data file
    for path in iter_data_files():
        format, examples = detect_format_and_parse(path)
        if not examples:
            stats.errors.append(f"{path.name}: failed to parse / empty")
            continue

        stats.files_processed += 1
        for ex in examples:
            migrate_entry(ex, stats, migration_date)

        if not args.dry_run:
            write_examples(path, examples, format)

    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    print(f"Files processed:                {stats.files_processed}")
    print(f"Examples migrated:              {stats.examples_migrated}")
    print(f"Data fixes — Unknown→Injection: {stats.fixes_unknown_to_injection}")
    print(f"Data fixes — truncated A03:     {stats.fixes_truncated_a03}")
    print(f"Data fixes — SSRF normalized:   {stats.fixes_ssrf_normalized}")
    print(f"Errors:                         {len(stats.errors)}")

    if stats.errors:
        print("\nERROR DETAILS (first 10):")
        for err in stats.errors[:10]:
            print(f"  - {err}")
        if len(stats.errors) > 10:
            print(f"  ... and {len(stats.errors) - 10} more")

    print("\nDistribution BEFORE (owasp_2021, including pre-fix values):")
    for k, v in sorted(stats.dist_2021_before.items(), key=lambda x: -x[1]):
        print(f"  {k:60s}  {v:4d}")

    print("\nDistribution AFTER (owasp_2021, post-fix):")
    for k, v in sorted(stats.dist_2021_after.items(), key=lambda x: -x[1]):
        print(f"  {k:60s}  {v:4d}")

    print("\nDistribution AFTER (owasp_2025):")
    for k, v in sorted(stats.dist_2025_after.items(), key=lambda x: -x[1]):
        print(f"  {k:60s}  {v:4d}")

    if not args.dry_run:
        print(f"\n✓ Migration complete. Backup at: {BACKUP_BASE / timestamp}")
        print(f"   Rollback with: python scripts/migrate_owasp_2025.py --rollback {timestamp}")
    else:
        print("\n✓ Dry-run complete. Re-run without --dry-run to apply.")


if __name__ == "__main__":
    main()
