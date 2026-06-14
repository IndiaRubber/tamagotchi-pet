from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

ASSET_DIR = PROJECT_ROOT / "assets"
SAVE_FILE = PROJECT_ROOT / "save.json"
SOUND_DIR = ASSET_DIR / "sounds"