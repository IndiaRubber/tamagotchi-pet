from dataclasses import dataclass, asdict
from datetime import datetime, timezone


@dataclass
class PetState:
    name: str = "Bit"
    hunger: float = 80.0
    happiness: float = 80.0
    cleanliness: float = 80.0
    energy: float = 80.0
    health: float = 100.0
    asleep: bool = False
    mess_count: int = 0
    time_since_last_mess: float = 0.0
    pee_count: int = 0
    time_since_last_pee: float = 0.0
    last_seen: str = ""
    

    def clamp(self):
        self.hunger = max(0, min(100, self.hunger))
        self.happiness = max(0, min(100, self.happiness))
        self.cleanliness = max(0, min(100, self.cleanliness))
        self.energy = max(0, min(100, self.energy))
        self.health = max(0, min(100, self.health))
        self.mess_count = max(0, min(3, int(self.mess_count)))
        self.time_since_last_mess = max(0, self.time_since_last_mess)
        self.pee_count = max(0, min(3, int(self.pee_count)))
        self.time_since_last_pee = max(0, self.time_since_last_pee)

    def to_dict(self):
        data = asdict(self)
        data["last_seen"] = datetime.now(timezone.utc).isoformat()
        return data

    @staticmethod
    def from_dict(data):
        pet = PetState()

        for key, value in data.items():
            if hasattr(pet, key):
                setattr(pet, key, value)

        # Backward compatibility for older save files
        if not hasattr(pet, "mess_count"):
            pet.mess_count = 0

        if not hasattr(pet, "time_since_last_mess"):
            pet.time_since_last_mess = 0.0

        pet.clamp()
        return pet