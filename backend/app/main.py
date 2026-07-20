"""
RaceAnalyst API — read-only viewer.

By design this API cannot trigger the pipeline, experts, or synthesizer
(no LLM-cost or GraphDB-write endpoints exist here at all). You keep
running run_pipeline.py / run_experts.py / run_analysis.py by hand on
your machine, exactly as today; this just reads whatever's already on
disk under RACE_DATA_ROOT and serves it to the dashboard. Safe to put
behind a public domain later with no risk of someone else triggering
paid LLM calls, since there's nothing here that can.
"""
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from . import config, expert_cache

app = FastAPI(title="RaceAnalyst API (read-only)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_methods=["GET"],
    allow_headers=["*"],
)


def require_api_key(x_api_key: str | None = Header(default=None)):
    if x_api_key != config.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/races")
def races(x_api_key: str | None = Header(default=None)):
    require_api_key(x_api_key)
    return {"races": expert_cache.list_races()}


@app.get("/api/races/{race_id}/experts")
def race_experts(race_id: str, x_api_key: str | None = Header(default=None)):
    require_api_key(x_api_key)
    return {"experts": expert_cache.list_expert_outputs(race_id)}


@app.get("/api/races/{race_id}/experts/{expert_name}")
def expert_output(race_id: str, expert_name: str, x_api_key: str | None = Header(default=None)):
    require_api_key(x_api_key)
    try:
        return {"expert": expert_name, "text": expert_cache.read_expert_output(race_id, expert_name)}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Not yet cached")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/races/{race_id}/analysis")
def final_analysis(race_id: str, x_api_key: str | None = Header(default=None)):
    require_api_key(x_api_key)
    try:
        return {"text": expert_cache.read_final_analysis(race_id)}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Not yet available")


@app.get("/api/races/{race_id}/race-day-files")
def race_day_files(race_id: str, x_api_key: str | None = Header(default=None)):
    require_api_key(x_api_key)
    return {"files": expert_cache.list_race_day_files(race_id)}


@app.get("/api/races/{race_id}/race-day-files/{key}")
def race_day_file(race_id: str, key: str, x_api_key: str | None = Header(default=None)):
    require_api_key(x_api_key)
    try:
        return {"key": key, "text": expert_cache.read_race_day_file(race_id, key)}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Not posted yet")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
