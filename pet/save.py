import json
from pathlib import Path
from pet.state import PetState

SAVE_FILE = Path("save.json")


def load_pet():
    if not SAVE_FILE.exists():
        return PetState()

    try:
        with SAVE_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return PetState.from_dict(data)

    except Exception as error:
        print(f"Could not load save file: {error}")
        return PetState()


def save_pet(pet):
    try:
        with SAVE_FILE.open("w", encoding="utf-8") as file:
            json.dump(pet.to_dict(), file, indent=2)

    except Exception as error:
        print(f"Could not save pet: {error}")