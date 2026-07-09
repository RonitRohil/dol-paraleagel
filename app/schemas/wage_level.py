from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EducationLevel(str, Enum):
    less_than_hs = "less_than_hs"
    hs = "hs"
    associates = "associates"
    bachelors = "bachelors"
    masters = "masters"
    doctorate = "doctorate"
    professional = "professional"


# Accepts common free-text spellings (as an interviewer/tester is likely to send)
# and normalizes them to the internal enum values above.
_EDUCATION_ALIASES = {
    "less than high school": EducationLevel.less_than_hs,
    "none": EducationLevel.less_than_hs,
    "high school": EducationLevel.hs,
    "hs": EducationLevel.hs,
    "high school diploma": EducationLevel.hs,
    "associate": EducationLevel.associates,
    "associates": EducationLevel.associates,
    "associate's": EducationLevel.associates,
    "associate degree": EducationLevel.associates,
    "bachelor": EducationLevel.bachelors,
    "bachelors": EducationLevel.bachelors,
    "bachelor's": EducationLevel.bachelors,
    "bachelor's degree": EducationLevel.bachelors,
    "master": EducationLevel.masters,
    "masters": EducationLevel.masters,
    "master's": EducationLevel.masters,
    "master's degree": EducationLevel.masters,
    "doctorate": EducationLevel.doctorate,
    "doctoral": EducationLevel.doctorate,
    "phd": EducationLevel.doctorate,
    "ph.d.": EducationLevel.doctorate,
    "professional": EducationLevel.professional,
    "professional degree": EducationLevel.professional,
}


def _normalize_education(value: object) -> object:
    if isinstance(value, str):
        key = value.strip().lower()
        if key in _EDUCATION_ALIASES:
            return _EDUCATION_ALIASES[key]
    return value


class WorkLocation(BaseModel):
    state: str
    city: str | None = None


class WageLevelRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    job_title: str | None = Field(default=None, alias="jobTitle")
    soc_code: str = Field(
        ..., alias="socCode", examples=["15-1252.00"], description="O*NET-SOC code for the occupation"
    )
    work_location: WorkLocation | None = Field(
        default=None,
        alias="workLocation",
        description=(
            "Captured for context/future wage-amount lookups. Not used in the level "
            "calculation: DOL wage LEVEL is location-independent, only the dollar wage "
            "amount varies by geography."
        ),
    )
    required_education: EducationLevel = Field(..., alias="education")
    required_experience_years: float = Field(..., alias="experienceYears", ge=0, le=30)
    supervises_others: bool = Field(default=False, alias="supervisoryDuties")
    special_skills: list[str] | None = Field(
        default=None,
        alias="specialSkills",
        description="Specific skills/certifications/licenses required beyond entry-level",
    )
    foreign_language_required: bool = Field(default=False, alias="foreignLanguageRequired")
    number_supervised: int | None = Field(default=None, alias="numberSupervised", ge=0)
    employment_type: str | None = Field(
        default=None,
        alias="employmentType",
        description="Captured for context. Not used in the level calculation.",
    )

    @field_validator("required_education", mode="before")
    @classmethod
    def normalize_education(cls, value: object) -> object:
        return _normalize_education(value)


class FactorResultSchema(BaseModel):
    points: int
    baseline: str
    required: str
    note: str = ""


class WageLevelResponse(BaseModel):
    soc_code: str
    occupation_title: str
    job_zone: int
    job_title: str | None = None
    work_location: WorkLocation | None = None
    employment_type: str | None = None
    factor_breakdown: dict[str, FactorResultSchema]
    total_points: int
    wage_level: str
    disclaimer: str


class OccupationSchema(BaseModel):
    soc_code: str
    title: str
    job_zone: int
