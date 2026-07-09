from fastapi import FastAPI

from app.api.routes_occupations import router as occupations_router
from app.api.routes_wage_level import router as wage_level_router

app = FastAPI(
    title="DOL Prevailing Wage Level Service",
    description=(
        "Determines a DOL prevailing wage level (I-IV) for a job opportunity using "
        "the National Prevailing Wage Center's point-based worksheet methodology, "
        "compared against O*NET Job Zone baselines. This is an approximation of "
        "published DOL guidance, not an official prevailing wage determination."
    ),
    version="0.1.0",
)

app.include_router(occupations_router)
app.include_router(wage_level_router)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
