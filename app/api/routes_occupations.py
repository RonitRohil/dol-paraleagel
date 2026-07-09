from fastapi import APIRouter, Query

from app.schemas.wage_level import OccupationSchema
from app.services.occupation_lookup import search_occupations

router = APIRouter(tags=["occupations"])


@router.get("/occupations/search", response_model=list[OccupationSchema])
def search(q: str = Query(..., min_length=2), limit: int = Query(20, ge=1, le=100)) -> list[OccupationSchema]:
    results = search_occupations(q, limit=limit)
    return [OccupationSchema(soc_code=o.soc_code, title=o.title, job_zone=o.job_zone) for o in results]
