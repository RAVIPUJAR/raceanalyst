"""
Read-side access to the pipeline's on-disk outputs: race folders and
their expert_cache/*.txt files. No parsing beyond filenames — the
webapp displays these as plain preformatted ASCII, matching how you
already read them.
"""
from pathlib import Path
from . import config


def list_races() -> list[dict]:
    """Every race-day folder under RACE_DATA_ROOT, most recent first."""
    if not config.RACE_DATA_ROOT.exists():
        return []
    races = []
    for p in sorted(config.RACE_DATA_ROOT.iterdir(), reverse=True):
        if p.is_dir():
            cache_dir = p / config.EXPERT_CACHE_DIRNAME
            has_outputs = cache_dir.exists() and any(cache_dir.glob("*.txt"))
            races.append({"race_id": p.name, "has_outputs": has_outputs})
    return races


def list_expert_outputs(race_id: str) -> dict[str, bool]:
    """Which experts have cached output for this race, present or not."""
    cache_dir = config.RACE_DATA_ROOT / race_id / config.EXPERT_CACHE_DIRNAME
    result = {}
    for name in config.EXPERT_NAMES:
        f = cache_dir / f"{name}.txt"
        result[name] = f.exists()
    return result


def read_expert_output(race_id: str, expert_name: str) -> str:
    if expert_name not in config.EXPERT_NAMES:
        raise ValueError(f"Unknown expert: {expert_name}")
    f = config.RACE_DATA_ROOT / race_id / config.EXPERT_CACHE_DIRNAME / f"{expert_name}.txt"
    if not f.exists():
        raise FileNotFoundError(f"No cached output yet for {expert_name} on {race_id}")
    return f.read_text(encoding="utf-8", errors="replace")


def read_final_analysis(race_id: str) -> str:
    """
    The GPT-5 synthesizer's output for the race. run_analysis.py itself
    only prints this to stdout — the webapp captures that output and
    writes it here (see pipeline_runner._save_synthesis_from_output),
    so this file won't exist until a run has happened through the webapp.
    """
    f = config.RACE_DATA_ROOT / race_id / config.EXPERT_CACHE_DIRNAME / config.FINAL_ANALYSIS_FILENAME
    if not f.exists():
        raise FileNotFoundError(f"No final analysis yet for {race_id}")
    return f.read_text(encoding="utf-8", errors="replace")


def list_race_day_files(race_id: str) -> dict[str, bool]:
    """Which race-day artifact files (live_odds, amendments, ...) exist yet."""
    race_dir = config.RACE_DATA_ROOT / race_id
    result = {}
    for key, (subdir, filename) in config.RACE_DAY_FILES.items():
        f = race_dir / subdir / filename
        result[key] = f.exists() and f.stat().st_size > 0
    return result


def read_race_day_file(race_id: str, key: str) -> str:
    if key not in config.RACE_DAY_FILES:
        raise ValueError(f"Unknown race-day file: {key}")
    subdir, filename = config.RACE_DAY_FILES[key]
    f = config.RACE_DATA_ROOT / race_id / subdir / filename
    if not f.exists():
        raise FileNotFoundError(f"{key} not posted yet for {race_id}")
    return f.read_text(encoding="utf-8", errors="replace")
