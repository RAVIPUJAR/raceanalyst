# backend/app/expert_cache.py
from pathlib import Path
from . import config

def list_races():
    """List all races from folders in RACE_DATA_PATH"""
    races = []
    
    print(f"Looking for races in: {config.RACE_DATA_PATH}")
    
    if not config.RACE_DATA_PATH.exists():
        print(f"ERROR: Path does not exist: {config.RACE_DATA_PATH}")
        return races
    
    # Check if there are any race folders directly in data
    for item in config.RACE_DATA_PATH.iterdir():
        if item.is_dir():
            print(f"Found directory: {item.name}")
            # Check if it looks like a race folder
            if item.name.startswith(("BNG-", "MUM-", "KOL-", "HYD-", "PUN-", "MYS-")):
                races.append({"race_id": item.name, "has_outputs": True})
                print(f"✅ Added race: {item.name}")
    
    return sorted(races, key=lambda x: x["race_id"])

def list_expert_outputs(race_id):
    """List expert outputs from expert_cache folder inside race folder"""
    experts = {}
    expert_cache_path = config.RACE_DATA_PATH / race_id / "expert_cache"
    
    print(f"Looking for expert_cache at: {expert_cache_path}")
    
    if expert_cache_path.exists():
        for file in expert_cache_path.glob("*.txt"):
            experts[file.stem] = True
            print(f"Found expert: {file.stem}")
    else:
        print(f"expert_cache path does not exist: {expert_cache_path}")
        # Try alternate location: maybe expert_cache is directly in race folder
        alternate_path = config.RACE_DATA_PATH / race_id
        print(f"Checking alternate: {alternate_path}")
        for item in alternate_path.iterdir():
            print(f"  Found: {item.name}")
    
    return experts

def read_expert_output(race_id, expert_name):
    """Read expert output from expert_cache folder"""
    file_path = config.RACE_DATA_PATH / race_id / "expert_cache" / f"{expert_name}.txt"
    print(f"Looking for expert file: {file_path}")
    if not file_path.exists():
        raise FileNotFoundError(f"Expert {expert_name} not found for race {race_id}")
    return file_path.read_text(encoding='utf-8')

def read_final_analysis(race_id):
    """Read final analysis from expert_cache folder"""
    file_path = config.RACE_DATA_PATH / race_id / "expert_cache" / "final_analysis.txt"
    print(f"Looking for analysis at: {file_path}")
    if not file_path.exists():
        raise FileNotFoundError(f"Analysis not found for race {race_id}")
    return file_path.read_text(encoding='utf-8')

def list_race_day_files(race_id):
    """List race day files from race folder (excluding expert_cache)"""
    files = {}
    race_path = config.RACE_DATA_PATH / race_id
    
    for subdir in race_path.iterdir():
        if subdir.is_dir() and subdir.name != "expert_cache":
            txt_file = subdir / f"{subdir.name}.txt"
            if txt_file.exists():
                files[subdir.name] = True
    
    return files

def read_race_day_file(race_id, key):
    """Read race day file from its subfolder"""
    file_path = config.RACE_DATA_PATH / race_id / key / f"{key}.txt"
    if not file_path.exists():
        raise FileNotFoundError(f"Race day file {key} not found for race {race_id}")
    return file_path.read_text(encoding='utf-8')