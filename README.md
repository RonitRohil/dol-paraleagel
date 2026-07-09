# DOL Prevailing Wage Level Service

### Paralegal DOL Assignment

A FastAPI service that determines a **DOL prevailing wage level (Level I–IV)** for a
job opportunity, using the point-based worksheet methodology used by DOL's National
Prevailing Wage Center (NPWC) for H-1B / PERM filings, compared against O\*NET Job
Zone baselines.

> **Not legal advice / not an official determination.** This is a rules-based
> approximation of published DOL guidance. Official prevailing wage determinations
> require filing an ETA-9141 with the NPWC and involve analyst discretion. Every API
> response includes this disclaimer.

## Methodology

Every job starts at **Level I** (base value = 1). Points are added across four
factors by comparing the job's stated requirements to the occupation's O\*NET
"normal" baseline (derived from the SOC's **Job Zone**, itself derived from an SVP —
Specific Vocational Preparation — range):

| Factor | Rule |
|---|---|
| Experience | at/below normal range: +0, low end: +1, high end: +2, exceeds range: +3 |
| Education | at/below normal: +0, one category above: +1, more than one above: +2 |
| Special skills/requirements | beyond entry-level (certifications, non-English language, etc.): +1 to +2 |
| Supervisory duties | supervises others: +1, unless supervision is customary for the occupation itself (e.g. "Managers"/"Supervisors" titles): +0 |

Total points (base 1 + all factor points), capped at 4, map directly to
Level I–IV.

## Data

`app/data/occupations.csv` and `app/data/job_zone_baselines.json` are derived from
the [O\*NET Database](https://www.onetcenter.org/database.html) (Occupation Data +
Job Zones files), which maps ~1,000 O\*NET-SOC codes to their Job Zone (1–5).

> This product was developed by the National Center for O\*NET Development. O\*NET is
> a trademark of USDOL/ETA.

## API

- `GET /health` — liveness check
- `GET /occupations/search?q=<text>` — search embedded SOC titles to find a `soc_code`
- `POST /wage-level/determine` — main endpoint, request body:

```json
{
  "soc_code": "15-1252.00",
  "required_education": "masters",
  "required_experience_years": 5,
  "supervises_others": true,
  "special_skills": ["Kubernetes"],
  "foreign_language_required": false,
  "number_supervised": 3
}
```

`required_education` is one of: `less_than_hs`, `hs`, `associates`, `bachelors`,
`masters`, `doctorate`, `professional`.

Interactive docs available at `/docs` once running.

## Local development

```bash
python -m venv venv
./venv/Scripts/activate        # Windows; use `source venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Run tests:

```bash
pytest
```

## Deployment (Render)

1. Push this repo to GitHub.
2. In the Render dashboard: **New > Blueprint**, point it at the repo — Render will
   read `render.yaml` and provision the Docker-based web service automatically
   (free plan, health check on `/health`).
3. Once deployed, verify with `curl https://<your-service>.onrender.com/health`.

Alternatively, build and run the Docker image directly anywhere that supports it:

```bash
docker build -t wage-level-service .
docker run -p 8000:8000 wage-level-service
```

## Known limitations

- Education/experience baselines are derived from O\*NET Job Zones, a simplification
  of DOL's full Appendix D occupation-specific baselines used in real NPWC
  determinations.
- Special skills and language-requirement scoring is a simplified 1–2 point
  heuristic; real determinations weigh these qualitatively per analyst judgment.
- This service returns a wage **level**, not a dollar wage amount (that requires
  ingesting DOL's OES wage survey data, out of scope for this service).