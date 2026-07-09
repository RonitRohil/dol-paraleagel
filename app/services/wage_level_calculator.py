"""Pure implementation of the DOL prevailing-wage Level I-IV point worksheet.

Methodology: every job starts at Level I (base value 1). Points are added
across four factors by comparing the job's stated requirements to the
occupation's O*NET "normal" baseline (derived from the SOC's Job Zone).
The total (capped at 4) is the wage level. This mirrors the worksheet used
by DOL's National Prevailing Wage Center, not an official determination.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.services.occupation_lookup import (
    get_job_zone_baseline,
    get_occupation,
    is_supervisory_occupation,
)

DISCLAIMER = (
    "This is a rules-based approximation of published DOL prevailing wage "
    "guidance (the National Prevailing Wage Center worksheet methodology), "
    "not an official prevailing wage determination. Official determinations "
    "involve DOL analyst discretion and should be requested via the NPWC "
    "(ETA-9141) for actual filings."
)

EDUCATION_RANKS = {
    "less_than_hs": 0,
    "hs": 1,
    "associates": 2,
    "bachelors": 3,
    "masters": 4,
    "doctorate": 5,
    "professional": 5,
}

LEVEL_NAMES = {1: "Level I", 2: "Level II", 3: "Level III", 4: "Level IV"}


class UnknownOccupationError(ValueError):
    pass


@dataclass
class FactorResult:
    points: int
    baseline: str
    required: str
    note: str = ""


@dataclass
class WageLevelResult:
    soc_code: str
    occupation_title: str
    job_zone: int
    factor_breakdown: dict[str, FactorResult]
    total_points: int
    wage_level: str
    disclaimer: str = field(default=DISCLAIMER)


def _experience_points(required_years: float, baseline: dict) -> FactorResult:
    min_years = baseline["experience_min_years"]
    max_years = baseline["experience_max_years"]
    midpoint = (min_years + max_years) / 2

    if required_years <= min_years:
        points, note = 0, "at or below the occupation's normal experience range"
    elif required_years <= midpoint:
        points, note = 1, "low end of the occupation's normal experience range"
    elif required_years <= max_years:
        points, note = 2, "high end of the occupation's normal experience range"
    else:
        points, note = 3, "exceeds the occupation's normal experience range"

    return FactorResult(
        points=points,
        baseline=f"{min_years}-{max_years} years ({baseline['svp_note']})",
        required=f"{required_years} years",
        note=note,
    )


def _education_points(required_education: str, baseline: dict) -> FactorResult:
    baseline_education = baseline["education_baseline"]
    diff = EDUCATION_RANKS[required_education] - EDUCATION_RANKS[baseline_education]

    if diff <= 0:
        points, note = 0, "at or below the occupation's normal education level"
    elif diff == 1:
        points, note = 1, "one category above the occupation's normal education level"
    else:
        points, note = 2, "more than one category above the occupation's normal education level"

    return FactorResult(
        points=points,
        baseline=baseline_education,
        required=required_education,
        note=note,
    )


def _special_skills_points(
    special_skills: list[str] | None, foreign_language_required: bool
) -> FactorResult:
    points = 0
    notes = []
    if special_skills:
        points += 1
        notes.append(f"{len(special_skills)} special skill(s)/certification(s) beyond entry-level")
    if foreign_language_required:
        points += 1
        notes.append("non-English language proficiency required")
    points = min(points, 2)

    return FactorResult(
        points=points,
        baseline="none beyond entry-level",
        required="; ".join(notes) if notes else "none",
        note="per DOL guidance, added sparingly and only for requirements genuinely beyond entry-level",
    )


def _supervisory_points(
    supervises_others: bool, number_supervised: int | None, occupation_title: str
) -> FactorResult:
    if not supervises_others:
        return FactorResult(points=0, baseline="no supervisory duty", required="none", note="")

    if is_supervisory_occupation(occupation_title):
        return FactorResult(
            points=0,
            baseline="supervisory duties customary for this occupation",
            required=f"supervises {number_supervised or 'some'} employee(s)",
            note="no point added: supervision is a customary duty of this occupation per DOL guidance",
        )

    return FactorResult(
        points=1,
        baseline="no supervisory duty",
        required=f"supervises {number_supervised or 'some'} employee(s)",
        note="supervisory duty beyond what is customary for this occupation",
    )


def calculate_wage_level(
    soc_code: str,
    required_education: str,
    required_experience_years: float,
    supervises_others: bool,
    special_skills: list[str] | None = None,
    foreign_language_required: bool = False,
    number_supervised: int | None = None,
) -> WageLevelResult:
    occupation = get_occupation(soc_code)
    if occupation is None:
        raise UnknownOccupationError(f"Unknown SOC code: {soc_code}")

    baseline = get_job_zone_baseline(occupation.job_zone)

    experience = _experience_points(required_experience_years, baseline)
    education = _education_points(required_education, baseline)
    special_skills_result = _special_skills_points(special_skills, foreign_language_required)
    supervisory = _supervisory_points(supervises_others, number_supervised, occupation.title)

    total_points = 1 + experience.points + education.points + special_skills_result.points + supervisory.points
    capped_level = min(total_points, 4)

    return WageLevelResult(
        soc_code=occupation.soc_code,
        occupation_title=occupation.title,
        job_zone=occupation.job_zone,
        factor_breakdown={
            "experience": experience,
            "education": education,
            "special_skills": special_skills_result,
            "supervisory": supervisory,
        },
        total_points=capped_level,
        wage_level=LEVEL_NAMES[capped_level],
    )
