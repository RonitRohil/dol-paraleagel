"""Loads the embedded O*NET SOC -> title -> Job Zone reference data and
provides lookup/search helpers used by the wage-level calculator and the
occupation search endpoint.
"""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
OCCUPATIONS_CSV = DATA_DIR / "occupations.csv"
JOB_ZONE_BASELINES_JSON = DATA_DIR / "job_zone_baselines.json"


@dataclass(frozen=True)
class Occupation:
    soc_code: str
    title: str
    job_zone: int


def _load_occupations() -> dict[str, Occupation]:
    occupations: dict[str, Occupation] = {}
    with OCCUPATIONS_CSV.open(encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            occupations[row["soc_code"]] = Occupation(
                soc_code=row["soc_code"],
                title=row["title"],
                job_zone=int(row["job_zone"]),
            )
    return occupations


def _load_job_zone_baselines() -> dict[int, dict]:
    with JOB_ZONE_BASELINES_JSON.open(encoding="utf-8") as f:
        raw = json.load(f)
    return {int(k): v for k, v in raw.items()}


_OCCUPATIONS = _load_occupations()
_JOB_ZONE_BASELINES = _load_job_zone_baselines()


def get_occupation(soc_code: str) -> Occupation | None:
    """Look up by O*NET-SOC code (e.g. "15-1252.00"). Also accepts the plain
    6-digit SOC code without the O*NET suffix (e.g. "15-1252"), falling back
    to that occupation's ".00" base entry, since most callers won't know the
    O*NET-specific suffix.
    """
    normalized = soc_code.strip()
    if normalized in _OCCUPATIONS:
        return _OCCUPATIONS[normalized]
    if not normalized.endswith(".00"):
        return _OCCUPATIONS.get(f"{normalized}.00")
    return None


def get_job_zone_baseline(job_zone: int) -> dict:
    return _JOB_ZONE_BASELINES[job_zone]


def search_occupations(query: str, limit: int = 20) -> list[Occupation]:
    q = query.strip().lower()
    if not q:
        return []
    matches = [occ for occ in _OCCUPATIONS.values() if q in occ.title.lower()]
    matches.sort(key=lambda occ: (len(occ.title), occ.title))
    return matches[:limit]


def is_supervisory_occupation(title: str) -> bool:
    """Whether supervising others is a customary duty of this occupation
    itself (per DOL guidance, this shouldn't add a wage-level point)."""
    lowered = title.lower()
    return "supervisor" in lowered or "manager" in lowered or "managing" in lowered
