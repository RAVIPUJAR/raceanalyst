# backend/app/config.py
import os
from pathlib import Path

# Load .env for local development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Determine if running on Render
IS_RENDER = os.getenv("RENDER") is not None

# Find the data directory
def find_data_path():
    """Find the data directory in multiple possible locations"""
    # List of possible paths to check
    possible_paths = [
        Path("./data"),                    # Current directory
        Path("../data"),                   # Parent directory
        Path("/opt/render/project/src/data"),  # Render's typical path
        Path("/app/data"),                 # Docker path
        Path(os.getcwd()) / "data",        # Current working directory
    ]
    
    # Also check if RACE_DATA_ROOT is set in environment
    env_path = os.getenv("RACE_DATA_ROOT")
    if env_path:
        possible_paths.insert(0, Path(env_path))
    
    # Try each path
    for path in possible_paths:
        if path.exists() and path.is_dir():
            print(f"✅ Found data at: {path}")
            return path
    
    # If no path found, create a default
    default_path = Path("./data")
    print(f"⚠️ No data path found. Using default: {default_path}")
    default_path.mkdir(parents=True, exist_ok=True)
    return default_path

# Set RACE_DATA_PATH
RACE_DATA_PATH = find_data_path()

# Debug prints
print(f"IS_RENDER: {IS_RENDER}")
print(f"RACE_DATA_PATH: {RACE_DATA_PATH.absolute()}")
print(f"Path exists: {RACE_DATA_PATH.exists()}")
if RACE_DATA_PATH.exists():
    contents = [item.name for item in RACE_DATA_PATH.iterdir() if item.is_dir()]
    print(f"Found directories: {contents[:10]}")

# CORS settings
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000,https://raceanalyst.com,https://www.raceanalyst.com").split(",")
ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS]

# Keep API_KEY for compatibility but not used
API_KEY = os.getenv("RACEANALYST_API_KEY", "")