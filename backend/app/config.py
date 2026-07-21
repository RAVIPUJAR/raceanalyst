# backend/app/config.py
import os
from pathlib import Path

# Load .env for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def find_data_path():
    """Find the data directory by searching aggressively"""
    
    # Get current working directory
    cwd = Path(os.getcwd())
    print(f"Current working directory: {cwd}")
    
    # List of possible paths to check
    possible_paths = []
    
    # 1. Check environment variable first
    env_path = os.getenv("RACE_DATA_ROOT")
    if env_path:
        possible_paths.append(Path(env_path))
    
    # 2. Check common Render paths
    possible_paths.extend([
        Path("/opt/render/project/src/data"),
        Path("/app/data"),
        Path("/data"),
    ])
    
    # 3. Check relative paths from cwd
    possible_paths.extend([
        cwd / "data",
        cwd / "src/data",
        cwd / "backend/data",
        cwd.parent / "data",
    ])
    
    # 4. Check if there's a data folder in any subdirectory
    # Walk up to 3 levels
    for level in range(3):
        base = cwd
        for _ in range(level):
            base = base.parent
        possible_paths.append(base / "data")
    
    # Try each path
    for path in possible_paths:
        try:
            if path.exists() and path.is_dir():
                # Check if it contains race folders
                has_race = any(
                    item.is_dir() and item.name.startswith(("BNG-", "MUM-", "KOL-", "HYD-", "PUN-", "MYS-"))
                    for item in path.iterdir()
                )
                if has_race:
                    print(f"✅ Found data with races at: {path}")
                    return path
                else:
                    print(f"⚠️ Found data folder but no races at: {path}")
                    # Still use it even if no races yet
                    return path
        except PermissionError:
            pass
    
    # If none found, create default
    default_path = cwd / "data"
    print(f"⚠️ No data path found. Using default: {default_path}")
    default_path.mkdir(parents=True, exist_ok=True)
    return default_path

# Set RACE_DATA_PATH
RACE_DATA_PATH = find_data_path()

# Debug prints
print(f"RACE_DATA_PATH: {RACE_DATA_PATH.absolute()}")
print(f"Path exists: {RACE_DATA_PATH.exists()}")
if RACE_DATA_PATH.exists():
    all_items = list(RACE_DATA_PATH.iterdir())
    dirs = [item.name for item in all_items if item.is_dir()]
    print(f"Directories: {dirs}")
    race_dirs = [d for d in dirs if d.startswith(("BNG-", "MUM-", "KOL-", "HYD-", "PUN-", "MYS-"))]
    print(f"Race directories: {race_dirs}")

# CORS settings
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000,https://raceanalyst.com,https://www.raceanalyst.com").split(",")
ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS]

# Keep API_KEY for compatibility but not used
API_KEY = os.getenv("RACEANALYST_API_KEY", "")