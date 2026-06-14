import json
from datetime import datetime, timezone

from pet.mood import get_mood
from pet.paths import SAVE_FILE
from pet.state import PetState


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