import os
from pathlib import Path
from . import config

# Expert outputs directory
EXPERT_DIR = Path(config.RACE_DATA_ROOT) / "experts"
RACE_DAY_DIR = Path(config.RACE_DATA_ROOT) / "race_day"
ANALYSIS_DIR = Path(config.RACE_DATA_ROOT) / "analysis"

# Ensure directories exist
EXPERT_DIR.mkdir(parents=True, exist_ok=True)
RACE_DAY_DIR.mkdir(parents=True, exist_ok=True)
ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

def list_races():
    """List all races with available data"""
    races = []
    
    # Check expert outputs
    if EXPERT_DIR.exists():
        for expert_file in EXPERT_DIR.glob("*.txt"):
            race_id = expert_file.stem
            if race_id not in races:
                races.append(race_id)
    
    # Check race day files
    if RACE_DAY_DIR.exists():
        for race_dir in RACE_DAY_DIR.iterdir():
            if race_dir.is_dir():
                race_id = race_dir.name
                if race_id not in races:
                    races.append(race_id)
    
    # Check analysis
    if ANALYSIS_DIR.exists():
        for analysis_file in ANALYSIS_DIR.glob("*.txt"):
            race_id = analysis_file.stem
            if race_id not in races:
                races.append(race_id)
    
    # Return sorted list with has_outputs flag
    return [{"race_id": r, "has_outputs": True} for r in sorted(races)]

def list_expert_outputs(race_id):
    """List available expert outputs for a race"""
    experts = {}
    pattern = f"{race_id}-*.txt"
    
    if EXPERT_DIR.exists():
        for expert_file in EXPERT_DIR.glob(pattern):
            expert_name = expert_file.stem.replace(f"{race_id}-", "")
            experts[expert_name] = True
    
    return experts

def read_expert_output(race_id, expert_name):
    """Read expert output content"""
    expert_file = EXPERT_DIR / f"{race_id}-{expert_name}.txt"
    if not expert_file.exists():
        raise FileNotFoundError(f"Expert output not found: {expert_name}")
    return expert_file.read_text(encoding='utf-8')

def read_final_analysis(race_id):
    """Read final analysis content"""
    analysis_file = ANALYSIS_DIR / f"{race_id}.txt"
    if not analysis_file.exists():
        raise FileNotFoundError(f"Analysis not found for race: {race_id}")
    return analysis_file.read_text(encoding='utf-8')

def list_race_day_files(race_id):
    """List available race day files for a race"""
    files = {}
    race_dir = RACE_DAY_DIR / race_id
    
    if race_dir.exists():
        for file in race_dir.glob("*.txt"):
            key = file.stem
            files[key] = True
    
    return files

def read_race_day_file(race_id, key):
    """Read race day file content"""
    race_file = RACE_DAY_DIR / race_id / f"{key}.txt"
    if not race_file.exists():
        raise FileNotFoundError(f"Race day file not found: {key}")
    return race_file.read_text(encoding='utf-8')