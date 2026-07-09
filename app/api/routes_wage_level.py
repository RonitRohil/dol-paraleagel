from fastapi import APIRouter, HTTPException

from app.schemas.wage_level import FactorResultSchema, WageLevelRequest, WageLevelResponse
from app.services.wage_level_calculator import UnknownOccupationError, calculate_wage_level

router = APIRouter(tags=["wage-level"])


@router.post("/wage-level/determine", response_model=WageLevelResponse)
def determine_wage_level(request: WageLevelRequest) -> WageLevelResponse:
    try:
        result = calculate_wage_level(
            soc_code=request.soc_code,
            required_education=request.required_education.value,
            required_experience_years=request.required_experience_years,
            supervises_others=request.supervises_others,
            special_skills=request.special_skills,
            foreign_language_required=request.foreign_language_required,
            number_supervised=request.number_supervised,
        )
    except UnknownOccupationError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return WageLevelResponse(
        soc_code=result.soc_code,
        occupation_title=result.occupation_title,
        job_zone=result.job_zone,
        job_title=request.job_title,
        work_location=request.work_location,
        employment_type=request.employment_type,
        factor_breakdown={
            name: FactorResultSchema(
                points=factor.points, baseline=factor.baseline, required=factor.required, note=factor.note
            )
            for name, factor in result.factor_breakdown.items()
        },
        total_points=result.total_points,
        wage_level=result.wage_level,
        disclaimer=result.disclaimer,
    )
