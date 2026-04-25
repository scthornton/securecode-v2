#!/usr/bin/env python3
"""
SecureCode Web v2.1: Metadata Enrichment

Adds EPSS, CVSS v3/v4, ATT&CK, CAPEC, and explicit preconditions to every
example. Per ROADMAP §11.4, every derived field carries source + confidence
markers so downstream users can distinguish measured fields from heuristic
derivations.

Sources (all free, no commercial APIs):
  - EPSS:  api.first.org/data/v1/epss        (no key)
  - CVSS:  services.nvd.nist.gov              (NVD_API_KEY env var)
  - CAPEC: scripts/enrichment_data/cwe-2000.csv  (MITRE CWE catalog)
  - ATT&CK: small curated CWE→technique table (heuristic, confidence-tagged)

Two-pass design:
  1. CVE-backed examples (~75%): full automation. Output goes back to source JSONL.
  2. Composite/no-CVE examples (~25%): queued to enrichment_manual_queue.jsonl
     for Scott's manual triage. Partial enrichment applied where derivable
     from CWE alone (CAPEC, ATT&CK heuristic, preconditions estimated bucket).

Disk cache at scripts/cache/{epss,nvd}/<cve_id>.json with 14-day TTL.

Usage:
    python scripts/enrich_metadata.py --dry-run --limit 20    # tiny sample
    python scripts/enrich_metadata.py --dry-run                # all, no writes
    python scripts/enrich_metadata.py                          # live run
    python scripts/enrich_metadata.py --refresh-cache          # force re-fetch

Each enriched field has paired _source and _confidence markers:
    epss_score / epss_source / epss_confidence
    cvss_v3_vector / cvss_v3_source / cvss_v3_confidence
    capec_ids / capec_ids_source / capec_ids_confidence
    attack_techniques / attack_techniques_source / attack_techniques_confidence
    preconditions / preconditions_source / preconditions_confidence

Confidence enum: measured | heuristic | approximated | absent
"""

import argparse
import csv
import json
import os
import re
import sys
import time
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
SCRIPTS_DIR = REPO_ROOT / "scripts"
CACHE_DIR = SCRIPTS_DIR / "cache"
ENRICHMENT_DATA_DIR = SCRIPTS_DIR / "enrichment_data"
ARCHIVED_DIR_NAME = "_archived_duplicates"
MANUAL_QUEUE_PATH = REPO_ROOT / "enrichment_manual_queue.jsonl"

CACHE_TTL_DAYS = 14
NVD_API_KEY = os.environ.get("NVD_API_KEY")
NVD_RATE_LIMIT_SLEEP = 0.6 if NVD_API_KEY else 6.5  # 50/30s keyed; 5/30s unkeyed
EPSS_RATE_LIMIT_SLEEP = 0.05  # FIRST.org has generous limits

CVE_PATTERN = re.compile(r"^CVE-\d{4}-\d+$")
CWE_PATTERN = re.compile(r"^CWE-(\d+)$")

ENRICHMENT_DATE = datetime.now().strftime("%Y-%m-%d")
ENRICHMENT_VERSION = "v2.1.0"


# ---------------------------------------------------------------------------
# CWE → ATT&CK heuristic mapping (curated, marked as heuristic in output)
# ---------------------------------------------------------------------------
# NOTE: This is a deliberately small, conservative mapping. We mark every
# entry as `confidence: heuristic` so downstream users know it's derived
# from CWE category nature rather than authoritative.
# Empty list = "no known generic mapping; consult CVE-specific sources"

CWE_TO_ATTACK = {
    # Injection family
    "CWE-78": ["T1059", "T1190"],     # Command injection / OS command injection
    "CWE-77": ["T1059"],              # General command injection
    "CWE-89": ["T1190"],              # SQL injection (exploit public-facing app)
    "CWE-94": ["T1059", "T1190"],     # Code injection
    "CWE-79": ["T1059.007"],          # XSS (JavaScript)
    "CWE-91": ["T1190"],              # XML injection
    "CWE-917": ["T1190"],             # Expression Language injection
    "CWE-1336": ["T1190"],            # Template injection (general)
    "CWE-1426": ["T1190"],            # Server-side template injection

    # Path / file
    "CWE-22": ["T1083", "T1190"],     # Path traversal
    "CWE-23": ["T1083"],              # Relative path traversal
    "CWE-36": ["T1083"],              # Absolute path traversal
    "CWE-434": ["T1190", "T1505.003"],# Unrestricted file upload (web shell)

    # Auth / session
    "CWE-287": ["T1078"],             # Improper authentication
    "CWE-306": ["T1078"],             # Missing auth for critical function
    "CWE-307": ["T1110"],             # Improper restriction of brute-force
    "CWE-384": ["T1539"],             # Session fixation
    "CWE-521": ["T1110.001"],         # Weak password requirements
    "CWE-798": ["T1552.001"],         # Hardcoded credentials
    "CWE-916": ["T1110.002"],         # Weak password hashing → cred cracking

    # Access control
    "CWE-285": ["T1078"],             # Improper authorization
    "CWE-639": ["T1190"],             # IDOR
    "CWE-862": ["T1078"],             # Missing authorization
    "CWE-863": ["T1078"],             # Incorrect authorization
    "CWE-269": ["T1068"],             # Improper privilege management

    # Crypto / data
    "CWE-200": ["T1213"],             # Information exposure
    "CWE-201": ["T1213"],             # Sensitive info in returned data
    "CWE-209": ["T1213"],             # Info exposure through error message
    "CWE-311": ["T1040"],             # Missing encryption (network sniff)
    "CWE-312": ["T1552"],             # Cleartext storage
    "CWE-326": ["T1552"],             # Inadequate encryption strength
    "CWE-327": ["T1552"],             # Use of broken crypto
    "CWE-330": ["T1110"],             # Insufficient randomness
    "CWE-338": ["T1110"],             # Cryptographic PRNG predictable

    # Deserialization / config
    "CWE-502": ["T1190"],             # Insecure deserialization (RCE path)
    "CWE-611": ["T1083", "T1190"],    # XXE
    "CWE-1004": ["T1539"],            # Sensitive cookie without HttpOnly
    "CWE-352": ["T1185"],             # CSRF (browser session riding)

    # SSRF / request manipulation
    "CWE-918": ["T1090", "T1095"],    # SSRF (internal service abuse)

    # Resource / DoS
    "CWE-400": ["T1499"],             # Uncontrolled resource consumption
    "CWE-770": ["T1499"],             # Allocation without limits

    # Logging / monitoring
    "CWE-117": [],                    # Improper output neutralization for logs
    "CWE-223": [],                    # Omission of security-relevant info
    "CWE-693": [],                    # Protection mechanism failure (general)
    "CWE-778": [],                    # Insufficient logging

    # Supply chain
    "CWE-1104": ["T1195"],            # Use of unmaintained third-party
    "CWE-1357": ["T1195.002"],        # Reliance on insufficiently trustworthy component
}


# ---------------------------------------------------------------------------
# I/O — JSONL parsing (mirrors migrate_owasp_2025.py)
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
        if len(examples) != 1:
            raise ValueError(f"single_object expects 1 example, got {len(examples)}")
        path.write_text(json.dumps(examples[0], ensure_ascii=False, indent=2) + "\n")
    elif format == "line_per_example":
        with open(path, "w") as f:
            for ex in examples:
                f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    else:
        raise ValueError(f"Unknown format: {format}")


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
# Disk cache
# ---------------------------------------------------------------------------


class DiskCache:
    def __init__(self, namespace: str, ttl_days: int = CACHE_TTL_DAYS):
        self.dir = CACHE_DIR / namespace
        self.dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(days=ttl_days)

    def _path(self, key: str) -> Path:
        # Sanitize key to a safe filename
        safe = key.replace("/", "_").replace(":", "_")
        return self.dir / f"{safe}.json"

    def get(self, key: str):
        path = self._path(key)
        if not path.exists():
            return None
        if datetime.now() - datetime.fromtimestamp(path.stat().st_mtime) > self.ttl:
            return None
        try:
            return json.loads(path.read_text())
        except json.JSONDecodeError:
            return None

    def put(self, key: str, value) -> None:
        self._path(key).write_text(json.dumps(value))

    def has_fresh(self, key: str) -> bool:
        return self.get(key) is not None


# ---------------------------------------------------------------------------
# HTTP helper
# ---------------------------------------------------------------------------


def http_get_json(url: str, headers: dict = None, timeout: int = 30) -> Optional[dict]:
    req = Request(url, headers=headers or {})
    try:
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        if e.code == 404:
            return None
        sys.stderr.write(f"  HTTP {e.code} for {url}\n")
        return None
    except URLError as e:
        sys.stderr.write(f"  URL error for {url}: {e}\n")
        return None
    except Exception as e:
        sys.stderr.write(f"  Error fetching {url}: {e}\n")
        return None


# ---------------------------------------------------------------------------
# EPSS provider
# ---------------------------------------------------------------------------


class EPSSProvider:
    def __init__(self):
        self.cache = DiskCache("epss")
        self.calls = 0
        self.cache_hits = 0
        self.failures = 0

    def lookup(self, cve_id: str) -> Optional[dict]:
        cached = self.cache.get(cve_id)
        if cached is not None:
            self.cache_hits += 1
            return None if cached.get("_no_data") else cached
        url = f"https://api.first.org/data/v1/epss?cve={cve_id}"
        time.sleep(EPSS_RATE_LIMIT_SLEEP)
        self.calls += 1
        data = http_get_json(url)
        if not data or not data.get("data"):
            self.failures += 1
            self.cache.put(cve_id, {"_no_data": True})
            return None
        record = data["data"][0]
        # EPSS may return a record with no score for CVEs not yet scored
        if "epss" not in record or "percentile" not in record:
            self.failures += 1
            self.cache.put(cve_id, {"_no_data": True})
            return None
        result = {
            "score": float(record["epss"]),
            "percentile": float(record["percentile"]),
            "date": record.get("date", ""),
        }
        self.cache.put(cve_id, result)
        return result


# ---------------------------------------------------------------------------
# NVD provider — fetches CVSS vectors and weaknesses
# ---------------------------------------------------------------------------


class NVDProvider:
    def __init__(self):
        self.cache = DiskCache("nvd")
        self.calls = 0
        self.cache_hits = 0
        self.failures = 0
        self.last_call_time = 0.0

    def lookup(self, cve_id: str) -> Optional[dict]:
        cached = self.cache.get(cve_id)
        if cached is not None:
            self.cache_hits += 1
            return None if cached.get("_no_data") else cached
        url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={cve_id}"
        headers = {"apiKey": NVD_API_KEY} if NVD_API_KEY else {}
        # Rate limiting
        elapsed = time.time() - self.last_call_time
        if elapsed < NVD_RATE_LIMIT_SLEEP:
            time.sleep(NVD_RATE_LIMIT_SLEEP - elapsed)
        self.calls += 1
        self.last_call_time = time.time()
        data = http_get_json(url, headers=headers)
        if not data or not data.get("vulnerabilities"):
            self.failures += 1
            self.cache.put(cve_id, {"_no_data": True})
            return None
        cve = data["vulnerabilities"][0]["cve"]
        metrics = cve.get("metrics", {})
        result = {
            "cvss_v31_vector": None,
            "cvss_v40_vector": None,
            "weaknesses": [],
            "published": cve.get("published", "")[:10],
        }
        if "cvssMetricV31" in metrics and metrics["cvssMetricV31"]:
            result["cvss_v31_vector"] = metrics["cvssMetricV31"][0]["cvssData"]["vectorString"]
        if "cvssMetricV40" in metrics and metrics["cvssMetricV40"]:
            result["cvss_v40_vector"] = metrics["cvssMetricV40"][0]["cvssData"]["vectorString"]
        for w in cve.get("weaknesses", []):
            for d in w.get("description", []):
                v = d.get("value", "")
                if v.startswith("CWE-"):
                    result["weaknesses"].append(v)
        self.cache.put(cve_id, result)
        return result


# ---------------------------------------------------------------------------
# CWE → CAPEC mapping (loaded from MITRE CSV)
# ---------------------------------------------------------------------------


class CWECAPECMapper:
    def __init__(self, csv_path: Path):
        self.cwe_to_capec = {}
        self.cwe_names = {}
        self._load(csv_path)

    def _load(self, csv_path: Path) -> None:
        if not csv_path.exists():
            sys.stderr.write(f"WARNING: {csv_path} not found; CAPEC mapping disabled\n")
            return
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cwe_id = f"CWE-{row['CWE-ID']}"
                self.cwe_names[cwe_id] = row["Name"]
                rap = row.get("Related Attack Patterns", "")
                # Format: "::108::109::110::"
                capec_ids = []
                for part in rap.split("::"):
                    part = part.strip()
                    if part.isdigit():
                        capec_ids.append(f"CAPEC-{part}")
                self.cwe_to_capec[cwe_id] = capec_ids

    def lookup(self, cwe_id: str) -> list:
        return self.cwe_to_capec.get(cwe_id, [])


# ---------------------------------------------------------------------------
# Preconditions derivation from CVSS vector
# ---------------------------------------------------------------------------


def parse_cvss_v31(vector: str) -> dict:
    """Parse CVSS:3.1 vector into a dict."""
    parts = {}
    if not vector:
        return parts
    for kv in vector.split("/"):
        if ":" in kv:
            k, v = kv.split(":", 1)
            parts[k] = v
    return parts


def derive_preconditions(cvss_vector: str) -> Optional[dict]:
    """Map CVSS AV/PR/UI to preconditions block.

    AV (Attack Vector):     N (Network) | A (Adjacent) | L (Local) | P (Physical)
    PR (Privileges Required): N (None) | L (Low) | H (High)
    UI (User Interaction):  N (None) | R (Required)
    """
    if not cvss_vector:
        return None
    parsed = parse_cvss_v31(cvss_vector)
    if not all(k in parsed for k in ("AV", "PR", "UI")):
        return None

    av_map = {"N": "internet", "A": "adjacent", "L": "internal", "P": "local"}
    pr_map = {"N": "none", "L": "authenticated_user", "H": "privileged"}
    ui_map = {"N": "none", "R": "active"}

    return {
        "auth_required": parsed["PR"] != "N",
        "network_position": av_map.get(parsed["AV"], "unknown"),
        "user_interaction": ui_map.get(parsed["UI"], "unknown"),
        "prior_access": pr_map.get(parsed["PR"], "unknown"),
    }


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------


class EnrichStats:
    def __init__(self):
        self.examples_total = 0
        self.cve_backed = 0
        self.composite = 0
        self.epss_filled = 0
        self.cvss_v31_filled = 0
        self.cvss_v40_filled = 0
        self.attack_filled = 0
        self.capec_filled = 0
        self.preconditions_filled = 0
        self.queued_manual = 0
        self.failures_per_cve = Counter()


# ---------------------------------------------------------------------------
# Per-example enrichment
# ---------------------------------------------------------------------------


def enrich_example(
    entry: dict,
    epss: EPSSProvider,
    nvd: NVDProvider,
    cwe_capec: CWECAPECMapper,
    stats: EnrichStats,
    manual_queue,
) -> bool:
    """Enrich a single example in place. Returns True if any field added."""
    metadata = entry.setdefault("metadata", {})
    context = entry.get("context", {})

    cve_id = context.get("cve")
    cwe_id = metadata.get("cwe")

    cve_valid = isinstance(cve_id, str) and CVE_PATTERN.match(cve_id) is not None
    cwe_valid = isinstance(cwe_id, str) and CWE_PATTERN.match(cwe_id) is not None

    stats.examples_total += 1
    any_filled = False

    # ---- CVE-backed: full automation ----
    if cve_valid:
        stats.cve_backed += 1

        # EPSS
        epss_data = epss.lookup(cve_id)
        if epss_data:
            metadata["epss_score"] = epss_data["score"]
            metadata["epss_percentile"] = epss_data["percentile"]
            metadata["epss_date"] = epss_data["date"]
            metadata["epss_source"] = "first.org_epss_api_v1"
            metadata["epss_confidence"] = "measured"
            stats.epss_filled += 1
            any_filled = True

        # NVD CVSS + weaknesses
        nvd_data = nvd.lookup(cve_id)
        if nvd_data:
            if nvd_data.get("cvss_v31_vector"):
                metadata["cvss_v3_vector"] = nvd_data["cvss_v31_vector"]
                metadata["cvss_v3_source"] = "nvd_api_v2"
                metadata["cvss_v3_confidence"] = "measured"
                stats.cvss_v31_filled += 1
                any_filled = True
            if nvd_data.get("cvss_v40_vector"):
                metadata["cvss_v4_vector"] = nvd_data["cvss_v40_vector"]
                metadata["cvss_v4_source"] = "nvd_api_v2"
                metadata["cvss_v4_confidence"] = "measured"
                stats.cvss_v40_filled += 1
                any_filled = True
            # Preconditions from CVSS v3.1
            preconditions = derive_preconditions(nvd_data.get("cvss_v31_vector"))
            if preconditions:
                metadata["preconditions"] = preconditions
                metadata["preconditions_source"] = "derived_from_cvss_v31_vector"
                metadata["preconditions_confidence"] = "measured"
                stats.preconditions_filled += 1
                any_filled = True
        else:
            stats.failures_per_cve[cve_id] += 1

    # ---- CAPEC + ATT&CK derivation (CWE-based, works for both branches) ----
    if cwe_valid:
        capec_ids = cwe_capec.lookup(cwe_id)
        if capec_ids:
            metadata["capec_ids"] = capec_ids
            metadata["capec_ids_source"] = "derived_from_mitre_cwe_catalog_csv"
            metadata["capec_ids_confidence"] = "heuristic"
            stats.capec_filled += 1
            any_filled = True
        attack_ids = CWE_TO_ATTACK.get(cwe_id, [])
        if attack_ids:
            metadata["attack_techniques"] = attack_ids
            metadata["attack_techniques_source"] = "derived_from_curated_cwe_attack_table"
            metadata["attack_techniques_confidence"] = "heuristic"
            stats.attack_filled += 1
            any_filled = True

    # ---- Composite (no CVE): queue for manual review ----
    if not cve_valid:
        stats.composite += 1
        if manual_queue is not None:
            manual_queue.write(json.dumps({
                "id": entry.get("id"),
                "cwe": cwe_id,
                "category": metadata.get("category"),
                "subcategory": metadata.get("subcategory"),
                "severity": metadata.get("severity"),
                "business_impact": context.get("business_impact"),
                "year": context.get("year"),
                "real_world_incident": context.get("real_world_incident"),
                "needs": ["epss_score", "epss_percentile", "cvss_v3_vector", "preconditions"],
                "auto_enriched": [k for k in ("capec_ids", "attack_techniques") if k in metadata],
            }, ensure_ascii=False) + "\n")
            stats.queued_manual += 1

    # ---- Provenance ----
    if any_filled:
        provenance = metadata.setdefault("provenance", {})
        provenance["enrichment_date"] = ENRICHMENT_DATE
        provenance["enrichment_version"] = ENRICHMENT_VERSION

    return any_filled


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    parser.add_argument("--dry-run", action="store_true",
                        help="Don't write changes back to data files")
    parser.add_argument("--limit", type=int, default=None,
                        help="Process at most N examples (for sampling)")
    parser.add_argument("--refresh-cache", action="store_true",
                        help="Bypass cache, force re-fetch from APIs")
    args = parser.parse_args()

    if args.refresh_cache and CACHE_DIR.exists():
        import shutil
        shutil.rmtree(CACHE_DIR)
        print(f"Cache cleared: {CACHE_DIR}")

    print("=" * 80)
    print("SecureCode Web v2.1 — Metadata Enrichment")
    print(f"NVD API key: {'present' if NVD_API_KEY else 'NOT SET (using unkeyed rate limit)'}")
    print(f"Mode: {'DRY-RUN (no writes)' if args.dry_run else 'LIVE'}")
    if args.limit:
        print(f"Limit: {args.limit} examples")
    print("=" * 80)

    epss = EPSSProvider()
    nvd = NVDProvider()
    cwe_capec = CWECAPECMapper(ENRICHMENT_DATA_DIR / "cwe-2000.csv")
    print(f"Loaded CWE→CAPEC mapping for {len(cwe_capec.cwe_to_capec)} CWEs")
    stats = EnrichStats()

    manual_queue_file = None
    if not args.dry_run:
        manual_queue_file = open(MANUAL_QUEUE_PATH, "w")

    try:
        for path in iter_data_files():
            if args.limit and stats.examples_total >= args.limit:
                break
            format, examples = detect_format_and_parse(path)
            if not examples:
                continue

            modified = False
            for ex in examples:
                if args.limit and stats.examples_total >= args.limit:
                    break
                if enrich_example(ex, epss, nvd, cwe_capec, stats, manual_queue_file):
                    modified = True

            if modified and not args.dry_run:
                write_examples(path, examples, format)

            # Progress every 100 examples
            if stats.examples_total > 0 and stats.examples_total % 100 == 0:
                print(f"  ... {stats.examples_total} processed "
                      f"(EPSS hits {stats.epss_filled}, CVSS hits {stats.cvss_v31_filled}, "
                      f"NVD calls {nvd.calls} cache hits {nvd.cache_hits})")
    finally:
        if manual_queue_file:
            manual_queue_file.close()

    # ---- Summary ----
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    print(f"Total examples processed:       {stats.examples_total}")
    print(f"  CVE-backed:                   {stats.cve_backed}")
    print(f"  Composite (queued manual):    {stats.composite}")
    print()
    print(f"Fields filled:")
    print(f"  EPSS score+percentile:        {stats.epss_filled}")
    print(f"  CVSS v3.1 vector:             {stats.cvss_v31_filled}")
    print(f"  CVSS v4.0 vector:             {stats.cvss_v40_filled}")
    print(f"  Preconditions (from CVSS):    {stats.preconditions_filled}")
    print(f"  CAPEC IDs (from CWE):         {stats.capec_filled}")
    print(f"  ATT&CK techniques (heur):     {stats.attack_filled}")
    print()
    print(f"API call summary:")
    print(f"  EPSS:  {epss.calls} calls, {epss.cache_hits} cache hits, {epss.failures} failures")
    print(f"  NVD:   {nvd.calls} calls, {nvd.cache_hits} cache hits, {nvd.failures} failures")
    print()
    print(f"Manual queue: {MANUAL_QUEUE_PATH if not args.dry_run else '(dry-run; would queue ' + str(stats.queued_manual) + ')'}")
    if stats.failures_per_cve:
        print(f"\nNVD failures per CVE (top 5):")
        for cve, n in stats.failures_per_cve.most_common(5):
            print(f"  {cve}: {n}")

    if args.dry_run:
        print("\n✓ Dry-run complete.")
    else:
        print("\n✓ Enrichment complete.")


if __name__ == "__main__":
    main()
