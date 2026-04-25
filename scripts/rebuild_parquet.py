#!/usr/bin/env python3
"""
SecureCode Web v2.1 — parquet rebuild with explicit HF Features schema.

This dataset's `id` field is NOT unique — `authentication-000001` appears 20+
times. Identity matching uses the conversations content hash.

Strategy:
  1. Read v2.0 parquet to determine split membership (by content hash).
  2. Match each parquet row to its enriched JSONL counterpart (by hash).
  3. Project every example to the v2.1 Features schema (v2.0 schema +
     enrichment fields). Drops any stray top-level or nested fields not in
     the schema. Forces consistent types.
  4. Write each split with the explicit schema.

Quality requirements (per Scott 2026-04-25, "must-have-upgrade" guideline):
  - Zero loss of v2.0 metadata fields
  - Full queryability of all enrichment fields in HF UI
  - Strict type discipline (no JSON-string fallbacks)
  - 1378 rows preserved across 1102/138/138 splits
"""

import hashlib
import json
import shutil
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import pyarrow.parquet as pq
from datasets import Dataset, Features, Value, Sequence

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
ARCHIVED = "_archived_duplicates"


# ---------------------------------------------------------------------------
# v2.1 Features schema = v2.0 schema + enrichment fields
# ---------------------------------------------------------------------------

V21_FEATURES = Features({
    "id": Value("string"),
    "metadata": {
        # ----- v2.0 fields (preserved) -----
        "category": Value("string"),
        "complexity": Value("string"),
        "created": Value("string"),
        "cwe": Value("string"),
        "lang": Value("string"),
        "owasp_2021": Value("string"),
        "severity": Value("string"),
        "subcategory": Value("string"),
        "tags": Sequence(Value("string")),
        "technique": Value("string"),
        "template_engine": Value("string"),
        "validated": Value("bool"),

        # ----- v2.1 OWASP 2025 dual-field (non-breaking) -----
        "owasp_2025": Value("string"),

        # ----- v2.1 EPSS (FIRST.org or severity-bucket-derived) -----
        "epss_score": Value("float64"),
        "epss_percentile": Value("float64"),
        "epss_date": Value("string"),
        "epss_source": Value("string"),
        "epss_confidence": Value("string"),

        # ----- v2.1 CVSS v3.1 (NVD) -----
        "cvss_v3_vector": Value("string"),
        "cvss_v3_source": Value("string"),
        "cvss_v3_confidence": Value("string"),

        # ----- v2.1 CVSS v4.0 (NVD where published) -----
        "cvss_v4_vector": Value("string"),
        "cvss_v4_source": Value("string"),
        "cvss_v4_confidence": Value("string"),

        # ----- v2.1 MITRE ATT&CK (heuristic from CWE) -----
        "attack_techniques": Sequence(Value("string")),
        "attack_techniques_source": Value("string"),
        "attack_techniques_confidence": Value("string"),

        # ----- v2.1 MITRE CAPEC (derived from CWE catalog) -----
        "capec_ids": Sequence(Value("string")),
        "capec_ids_source": Value("string"),
        "capec_ids_confidence": Value("string"),

        # ----- v2.1 Preconditions (parsed from CVSS or category-heuristic) -----
        "preconditions": {
            "auth_required": Value("bool"),
            "network_position": Value("string"),
            "user_interaction": Value("string"),
            "prior_access": Value("string"),
        },
        "preconditions_source": Value("string"),
        "preconditions_confidence": Value("string"),
        "preconditions_text_overrides": Sequence(Value("string")),

        # ----- v2.1 Provenance (audit trail) -----
        "provenance": {
            "owasp_migration_date": Value("string"),
            "owasp_data_corrections": Sequence(Value("string")),
            "enrichment_date": Value("string"),
            "enrichment_version": Value("string"),
            "composite_heuristic_date": Value("string"),
            "composite_heuristic_version": Value("string"),
            "v21_conversations_restored_from_v20_parquet": Value("bool"),
        },
    },
    "context": {
        # ----- v2.0 fields (preserved) -----
        "affected_systems": Value("string"),
        "attack_vector": Value("string"),
        "business_impact": Value("string"),
        "cve": Value("string"),
        "impact": Value("string"),
        "real_world_incident": Value("string"),
        "year": Value("int64"),
    },
    "conversations": [{
        "from": Value("string"),
        "turn": Value("int64"),
        "value": Value("string"),
    }],
    "validation": {
        # ----- v2.0 fields (preserved) -----
        "code_execution": Value("string"),
        "duplication_check": Value("string"),
        "encoding_check": Value("string"),
        "issues": Sequence(Value("string")),  # was List(null) in v2.0; widened to string
        "review_date": Value("string"),
        "reviewed_by": Value("string"),
        "security_review": Value("string"),
        "syntax_check": Value("string"),
    },
})


# ---------------------------------------------------------------------------
# JSONL utilities
# ---------------------------------------------------------------------------


def content_hash(example: dict) -> str:
    convs = example.get("conversations") or example.get("conversation") or []
    return hashlib.sha256(json.dumps(convs, sort_keys=True).encode()).hexdigest()


def load_all_jsonl_instances():
    instances = []
    for path in sorted(DATA_DIR.rglob("*.jsonl")):
        if ARCHIVED in path.parts:
            continue
        if path.name == "batch_007_corrections.jsonl":
            continue
        if path.stat().st_size == 0:
            continue
        text = path.read_text()
        consumed = False
        try:
            obj = json.loads(text)
            if isinstance(obj, dict) and "id" in obj:
                instances.append((path, obj))
                consumed = True
        except json.JSONDecodeError:
            pass
        if consumed:
            continue
        for line in text.split("\n"):
            line = line.strip()
            if not line:
                continue
            try:
                ex = json.loads(line)
                if isinstance(ex, dict) and "id" in ex:
                    instances.append((path, ex))
            except json.JSONDecodeError:
                pass
    return instances


def load_split_rows():
    rows = []
    for split_name in ("train", "validation", "test"):
        path = DATA_DIR / f"{split_name}-00000-of-00001.parquet"
        table = pq.read_table(path)
        for row in table.to_pylist():
            rows.append({
                "split": split_name,
                "hash": content_hash(row),
                "id": row.get("id"),
                "parquet": row,
            })
    return rows


# ---------------------------------------------------------------------------
# Schema projection — convert each example to fit V21_FEATURES exactly
# ---------------------------------------------------------------------------


def _str_or_none(v):
    return v if isinstance(v, str) else None


def _bool_or_none(v):
    return v if isinstance(v, bool) else None


def _float_or_none(v):
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return float(v)
    return None


def _int_or_none(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, int):
        return v
    if isinstance(v, str):
        try:
            return int(v)
        except ValueError:
            return None
    return None


def _list_of_str(v):
    if not isinstance(v, list):
        return []
    return [str(x) for x in v if x is not None]


def project_metadata(md: dict) -> dict:
    if not isinstance(md, dict):
        md = {}
    preconditions_in = md.get("preconditions") or {}
    if not isinstance(preconditions_in, dict):
        preconditions_in = {}
    provenance_in = md.get("provenance") or {}
    if not isinstance(provenance_in, dict):
        provenance_in = {}

    return {
        # v2.0 fields
        "category": _str_or_none(md.get("category")),
        "complexity": _str_or_none(md.get("complexity")),
        "created": _str_or_none(md.get("created")),
        "cwe": _str_or_none(md.get("cwe")),
        "lang": _str_or_none(md.get("lang")),
        "owasp_2021": _str_or_none(md.get("owasp_2021")),
        "severity": _str_or_none(md.get("severity")),
        "subcategory": _str_or_none(md.get("subcategory")),
        "tags": _list_of_str(md.get("tags")),
        "technique": _str_or_none(md.get("technique")),
        "template_engine": _str_or_none(md.get("template_engine")),
        "validated": _bool_or_none(md.get("validated")),

        # v2.1 OWASP 2025
        "owasp_2025": _str_or_none(md.get("owasp_2025")),

        # v2.1 EPSS
        "epss_score": _float_or_none(md.get("epss_score")),
        "epss_percentile": _float_or_none(md.get("epss_percentile")),
        "epss_date": _str_or_none(md.get("epss_date")),
        "epss_source": _str_or_none(md.get("epss_source")),
        "epss_confidence": _str_or_none(md.get("epss_confidence")),

        # v2.1 CVSS v3
        "cvss_v3_vector": _str_or_none(md.get("cvss_v3_vector")),
        "cvss_v3_source": _str_or_none(md.get("cvss_v3_source")),
        "cvss_v3_confidence": _str_or_none(md.get("cvss_v3_confidence")),

        # v2.1 CVSS v4
        "cvss_v4_vector": _str_or_none(md.get("cvss_v4_vector")),
        "cvss_v4_source": _str_or_none(md.get("cvss_v4_source")),
        "cvss_v4_confidence": _str_or_none(md.get("cvss_v4_confidence")),

        # v2.1 ATT&CK
        "attack_techniques": _list_of_str(md.get("attack_techniques")),
        "attack_techniques_source": _str_or_none(md.get("attack_techniques_source")),
        "attack_techniques_confidence": _str_or_none(md.get("attack_techniques_confidence")),

        # v2.1 CAPEC
        "capec_ids": _list_of_str(md.get("capec_ids")),
        "capec_ids_source": _str_or_none(md.get("capec_ids_source")),
        "capec_ids_confidence": _str_or_none(md.get("capec_ids_confidence")),

        # v2.1 Preconditions
        "preconditions": {
            "auth_required": _bool_or_none(preconditions_in.get("auth_required")),
            "network_position": _str_or_none(preconditions_in.get("network_position")),
            "user_interaction": _str_or_none(preconditions_in.get("user_interaction")),
            "prior_access": _str_or_none(preconditions_in.get("prior_access")),
        },
        "preconditions_source": _str_or_none(md.get("preconditions_source")),
        "preconditions_confidence": _str_or_none(md.get("preconditions_confidence")),
        "preconditions_text_overrides": _list_of_str(md.get("preconditions_text_overrides")),

        # v2.1 Provenance
        "provenance": {
            "owasp_migration_date": _str_or_none(provenance_in.get("owasp_migration_date")),
            "owasp_data_corrections": _list_of_str(provenance_in.get("owasp_data_corrections")),
            "enrichment_date": _str_or_none(provenance_in.get("enrichment_date")),
            "enrichment_version": _str_or_none(provenance_in.get("enrichment_version")),
            "composite_heuristic_date": _str_or_none(provenance_in.get("composite_heuristic_date")),
            "composite_heuristic_version": _str_or_none(provenance_in.get("composite_heuristic_version")),
            "v21_conversations_restored_from_v20_parquet": _bool_or_none(provenance_in.get("v21_conversations_restored_from_v20_parquet")),
        },
    }


def project_context(ctx) -> dict:
    if not isinstance(ctx, dict):
        ctx = {}
    return {
        "affected_systems": _str_or_none(ctx.get("affected_systems")),
        "attack_vector": _str_or_none(ctx.get("attack_vector")),
        "business_impact": _str_or_none(ctx.get("business_impact")),
        "cve": _str_or_none(ctx.get("cve")),
        "impact": _str_or_none(ctx.get("impact")),
        "real_world_incident": _str_or_none(ctx.get("real_world_incident")),
        "year": _int_or_none(ctx.get("year")),
    }


def project_conversations(convs):
    if not isinstance(convs, list):
        return []
    out = []
    for c in convs:
        if not isinstance(c, dict):
            continue
        out.append({
            "from": _str_or_none(c.get("from")),
            "turn": _int_or_none(c.get("turn")),
            "value": _str_or_none(c.get("value")),
        })
    return out


def project_validation(v):
    if not isinstance(v, dict):
        v = {}
    issues_raw = v.get("issues") or []
    issues = []
    if isinstance(issues_raw, list):
        for x in issues_raw:
            if x is None:
                continue
            issues.append(str(x))
    return {
        "code_execution": _str_or_none(v.get("code_execution")),
        "duplication_check": _str_or_none(v.get("duplication_check")),
        "encoding_check": _str_or_none(v.get("encoding_check")),
        "issues": issues,
        "review_date": _str_or_none(v.get("review_date")),
        "reviewed_by": _str_or_none(v.get("reviewed_by")),
        "security_review": _str_or_none(v.get("security_review")),
        "syntax_check": _str_or_none(v.get("syntax_check")),
    }


def project_to_v21_schema(example: dict) -> dict:
    return {
        "id": _str_or_none(example.get("id")),
        "metadata": project_metadata(example.get("metadata") or {}),
        "context": project_context(example.get("context") or {}),
        "conversations": project_conversations(example.get("conversations") or []),
        "validation": project_validation(example.get("validation") or {}),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    print("=" * 80)
    print("SecureCode Web v2.1 — parquet rebuild with explicit Features schema")
    print("=" * 80)

    parquet_rows = load_split_rows()
    print(f"v2.0 parquet rows: {len(parquet_rows)}")

    jsonl_instances = load_all_jsonl_instances()
    print(f"v2.1 JSONL instances: {len(jsonl_instances)}")

    jsonl_by_hash = defaultdict(list)
    jsonl_by_id = defaultdict(list)
    for path, ex in jsonl_instances:
        jsonl_by_hash[content_hash(ex)].append((path, ex))
        jsonl_by_id[ex.get("id")].append((path, ex))

    new_splits = {"train": [], "validation": [], "test": []}
    used_per_hash = Counter()
    used_per_id = Counter()
    hash_matched = 0
    id_only_matched = 0
    no_match = []

    for prow in parquet_rows:
        h = prow["hash"]
        ex_id = prow["id"]
        hits = jsonl_by_hash.get(h, [])
        if hits:
            idx = used_per_hash[h] % len(hits)
            used_per_hash[h] += 1
            chosen_path, chosen_ex = hits[idx]
            new_splits[prow["split"]].append(chosen_ex)
            hash_matched += 1
        elif ex_id in jsonl_by_id and jsonl_by_id[ex_id]:
            id_hits = jsonl_by_id[ex_id]
            idx = used_per_id[ex_id] % len(id_hits)
            used_per_id[ex_id] += 1
            chosen_path, chosen_ex = id_hits[idx]
            hybrid = dict(chosen_ex)
            hybrid["conversations"] = prow["parquet"].get("conversations", [])
            md = hybrid.setdefault("metadata", {})
            prov = md.setdefault("provenance", {})
            prov["v21_conversations_restored_from_v20_parquet"] = True
            new_splits[prow["split"]].append(hybrid)
            id_only_matched += 1
        else:
            no_match.append((prow["split"], ex_id, h))

    print(f"\nMatching: hash={hash_matched}, id_only={id_only_matched}, no_match={len(no_match)}")
    if no_match:
        print(f"\n✗ FATAL: {len(no_match)} unmatched rows")
        sys.exit(1)

    # Backup
    bk = REPO_ROOT / "backups" / "pre-v2.1-parquet-rebuild" / datetime.now().strftime("%Y%m%d_%H%M%S")
    bk.mkdir(parents=True, exist_ok=True)
    for p in DATA_DIR.glob("*.parquet"):
        shutil.copy2(p, bk / p.name)
    print(f"Backup: {bk}")

    # Project + write
    print()
    for split_name, examples in new_splits.items():
        projected = [project_to_v21_schema(ex) for ex in examples]
        try:
            ds = Dataset.from_list(projected, features=V21_FEATURES)
        except Exception as e:
            print(f"\n✗ {split_name} failed: {e}")
            sys.exit(1)
        out_path = DATA_DIR / f"{split_name}-00000-of-00001.parquet"
        ds.to_parquet(str(out_path))
        verify = pq.read_table(out_path)
        size_mb = out_path.stat().st_size / 1024 / 1024
        print(f"  ✓ {split_name}: {len(verify)} rows, {size_mb:.1f} MB, {len(verify.column_names)} top cols")

    print(f"\n✓ Parquet rebuild complete with v2.1 Features schema.")
    print(f"  Rollback: cp {bk}/*.parquet data/")


if __name__ == "__main__":
    main()
