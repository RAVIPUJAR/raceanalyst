"""
Central config for the RaceAnalyst webapp backend.
Everything is overridable via a .env file (see .env.example) so this
same code works unchanged whether it's running on your laptop today
or on a real server later.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- Filesystem layout of the existing Kudurebaala pipeline ---
# Root folder containing one subfolder per race day, e.g.
#   RACE_DATA_ROOT/BANGALORE-2026-07-19/
RACE_DATA_ROOT = Path(os.getenv("RACE_DATA_ROOT", "/path/to/race-data")).resolve()

# Folder containing run_pipeline.py, run_experts.py, run_analysis.py
PIPELINE_SCRIPTS_ROOT = Path(os.getenv("PIPELINE_SCRIPTS_ROOT", "/path/to/kudurebaala")).resolve()

# Python interpreter to invoke the pipeline scripts with (use the venv
# that already has LangGraph / Azure OpenAI / GraphDB deps installed)
PIPELINE_PYTHON = os.getenv("PIPELINE_PYTHON", "python3")

# Subfolder name (inside each race-day folder) where experts write
# their plain ASCII .txt outputs
EXPERT_CACHE_DIRNAME = os.getenv("EXPERT_CACHE_DIRNAME", "expert_cache")

# race_id (e.g. "BNG-2026-07-04-RACE-1") is both the race folder name
# AND the suffix of the GraphDB named graph URI.
GRAPH_URI_PREFIX = os.getenv("GRAPH_URI_PREFIX", "urn:race-day:")

# run_analysis.py doesn't cache its synthesis to disk (console only) —
# the webapp captures its stdout and writes this file itself so the
# result survives across page loads without re-running the LLM call.
FINAL_ANALYSIS_FILENAME = "final_analysis.txt"

# Race-day artifact files that live as siblings of expert_cache/, each
# in their own subfolder, e.g. {race_folder}/live_odds/live_odds.txt.
# key -> (subfolder_name, filename). The dashboard shows whichever of
# these exist for a race and re-polls for new ones (e.g. live_odds
# typically only appears close to post time).
RACE_DAY_FILES = {
    "live_odds": ("live_odds", "live_odds.txt"),
    "amendments": ("amendments", "amendments.txt"),
    "body_weights": ("body_weights", "body_weights.txt"),
    "track_condition": ("track_condition", "track_condition.txt"),
    "change_of_equipments": ("change_of_equipments", "change_of_equipments.txt"),
    "false_rails": ("false_rails", "false_rails.txt"),
}

# --- Auth ---
# Simple shared-secret auth for now (internal tool). Sent as header
# `X-API-Key`. Swap for Cloudflare Access / proper auth when this
# moves behind raceanalyst.com's member area.
API_KEY = os.getenv("RACEANALYST_API_KEY", "change-me-dev-key")

# --- CORS ---
# Origins allowed to call this API from a browser. Add your Cloudflare
# Pages domain(s) here once deployed.
ALLOWED_ORIGINS = [
    o.strip() for o in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:8000,https://raceanalyst.com,https://www.raceanalyst.com"
    ).split(",") if o.strip()
]

# Confirmed expert list + display order, matching ALL_EXPERTS in
# run_analysis.py exactly. No "expert_" prefix — that's just the
# LangGraph node naming convention, not the cache filenames.
EXPERT_NAMES = [
    "ratings", "pedigree", "trackwork", "sweepstakes", "day_results",
    "medical", "equipment", "connections_form", "competition_form", "field_rivals",
]
