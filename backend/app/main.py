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
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

from . import config, expert_cache

app = FastAPI(title="RaceAnalyst API (read-only)")

# CORS - allow all origins for public access
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Health check endpoint - no auth required
@app.get("/api/health")
def health():
    return {"status": "ok"}

# List all available races - public
@app.get("/api/races")
def races():
    try:
        races_list = expert_cache.list_races()
        return {"races": races_list}
    except Exception as e:
        print(f"Error in /api/races: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=str(e))

# List experts for a specific race - public
@app.get("/api/races/{race_id}/experts")
def race_experts(race_id: str):
    try:
        return {"experts": expert_cache.list_expert_outputs(race_id)}
    except Exception as e:
        print(f"Error in /api/races/{race_id}/experts: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=str(e))

# Get specific expert output - public
@app.get("/api/races/{race_id}/experts/{expert_name}")
def expert_output(race_id: str, expert_name: str):
    try:
        return {"expert": expert_name, "text": expert_cache.read_expert_output(race_id, expert_name)}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Not yet cached")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error in /api/races/{race_id}/experts/{expert_name}: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=str(e))

# Get final analysis - public
@app.get("/api/races/{race_id}/analysis")
def final_analysis(race_id: str):
    try:
        return {"text": expert_cache.read_final_analysis(race_id)}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Not yet available")
    except Exception as e:
        print(f"Error in /api/races/{race_id}/analysis: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=str(e))

# List race day files - public
@app.get("/api/races/{race_id}/race-day-files")
def race_day_files(race_id: str):
    try:
        return {"files": expert_cache.list_race_day_files(race_id)}
    except Exception as e:
        print(f"Error in /api/races/{race_id}/race-day-files: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=str(e))

# Get specific race day file - public
@app.get("/api/races/{race_id}/race-day-files/{key}")
def race_day_file(race_id: str, key: str):
    try:
        return {"key": key, "text": expert_cache.read_race_day_file(race_id, key)}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Not posted yet")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error in /api/races/{race_id}/race-day-files/{key}: {e}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/api/debug")
def debug():
    """Comprehensive debug endpoint"""
    import os
    import sys
    from pathlib import Path
    
    debug_info = {
        "cwd": os.getcwd(),
        "sys_path": sys.path[:5],
        "RENDER": os.getenv("RENDER"),
        "RACE_DATA_ROOT_env": os.getenv("RACE_DATA_ROOT"),
        "RACE_DATA_PATH": str(config.RACE_DATA_PATH),
        "path_exists": config.RACE_DATA_PATH.exists(),
        "path_is_dir": config.RACE_DATA_PATH.is_dir() if config.RACE_DATA_PATH.exists() else False,
        "contents_at_path": [],
        "contents_at_cwd": [],
        "contents_at_project_root": [],
    }
    
    # Check what's at RACE_DATA_PATH
    if config.RACE_DATA_PATH.exists():
        for item in config.RACE_DATA_PATH.iterdir():
            debug_info["contents_at_path"].append({
                "name": item.name,
                "is_dir": item.is_dir()
            })
    
    # Check what's at current working directory
    cwd = Path(os.getcwd())
    if cwd.exists():
        for item in cwd.iterdir():
            if item.is_dir():
                debug_info["contents_at_cwd"].append(item.name)
    
    # Check what's at potential project root
    for parent in [Path("/opt/render/project/src"), Path("/app"), Path(".")]:
        if parent.exists():
            for item in parent.iterdir():
                if item.is_dir() and item.name == "data":
                    debug_info["contents_at_project_root"].append({
                        "path": str(parent),
                        "has_data": True,
                        "data_contents": [x.name for x in item.iterdir() if x.is_dir()][:5]
                    })
    
    return debug_info