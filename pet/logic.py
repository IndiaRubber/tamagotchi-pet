from datetime import datetime, timezone
from pet.mood import get_mood
from pet.state import PetState

import pet

MESS_INTERVAL_SECONDS = 10
PEE_INTERVAL_SECONDS = 8
MAX_MESS_COUNT = 3
MAX_PEE_COUNT = 3

def seconds_since_last_seen(pet):
    if not pet.last_seen:
        return 0

    try:
        last = datetime.fromisoformat(pet.last_seen)
        now = datetime.now(timezone.utc)
        return max(0, (now - last).total_seconds())
    except Exception:
        return 0


def apply_offline_progress(pet):
    seconds = seconds_since_last_seen(pet)

    # Cap offline decay so the pet doesn't instantly implode after a long break.
    seconds = min(seconds, 60 * 60 * 12)

    update_pet(pet, seconds)


def update_pet(pet, dt):
    events = []
    
    if pet.asleep:
        pet.energy += 20.0 * dt / 60
        pet.hunger -= 0.8 * dt / 60
        pet.happiness -= 0.3 * dt / 60
    else:
        pet.hunger -= 20 * dt / 60
        pet.happiness -= 1.7 * dt / 60
        pet.cleanliness -= 0.7 * dt / 60
        pet.energy -= 0.8 * dt / 60
    
    if not pet.asleep:
        pet.time_since_last_mess += dt

        if pet.time_since_last_mess >= MESS_INTERVAL_SECONDS:
            if pet.mess_count < MAX_MESS_COUNT:
                pet.mess_count += 1
                pet.cleanliness -= 12
                pet.happiness -= 5
                events.append("mess_created")                

            pet.time_since_last_mess = 0
    
    if not pet.asleep:
        pet.time_since_last_pee += dt

        if pet.time_since_last_pee >= PEE_INTERVAL_SECONDS:
            if pet.pee_count < MAX_PEE_COUNT:
                pet.pee_count += 1
                pet.cleanliness -= 8
                pet.happiness -= 3
                events.append("pee_created")

            pet.time_since_last_pee = 0
 
    if pet.hunger <= 0:
        pet.health -= 6.0 * dt / 60
    elif pet.hunger < 20:
        pet.health -= 2.0 * dt / 60

    total_accidents = pet.mess_count + pet.pee_count

    if pet.mess_count > 0:
        pet.cleanliness -= pet.mess_count * 1.2 * dt / 60
        pet.happiness -= pet.mess_count * 0.4 * dt / 60

    if pet.pee_count > 0:
        pet.cleanliness -= pet.pee_count * 0.9 * dt / 60
        pet.happiness -= pet.pee_count * 0.5 * dt / 60

    if total_accidents >= 4:
        pet.cleanliness -= 2.0 * dt / 60
        pet.happiness -= 1.0 * dt / 60

    if total_accidents >= 5:
        pet.health -= 1.5 * dt / 60
        
    if pet.energy <= 0:
        pet.health -= 2.0 * dt / 60
    elif pet.energy < 15:
        pet.happiness -= 0.8 * dt / 60
    
    if pet.happiness <= 0:
        pet.health -= 3.0 * dt / 60
    
    mood = get_mood(pet)

    if mood == "sick":
        pet.health -= 30.0 * dt / 30

    well_cared_for = (
        pet.hunger > 50
        and pet.cleanliness > 50
        and pet.energy > 30
        and pet.happiness > 30
    )

    if well_cared_for:
        if pet.health < 30:
            pet.health += 6.0 * dt / 60
        else:
            pet.health += 3.0 * dt / 60

    pet.clamp()
    return events

def feed_pet(pet):
    if pet.asleep:
        return "Bit is asleep..."

    pet.hunger += 22
    pet.cleanliness -= 4
    pet.happiness += 3
    pet.clamp()
    return "Snack acquired."


def play_with_pet(pet):
    if pet.asleep:
        return "Bit is asleep..."

    if pet.energy < 15:
        pet.happiness -= 3
        pet.clamp()
        return "Too tired to play."

    pet.happiness += 18
    pet.energy -= 12
    pet.hunger -= 8
    pet.cleanliness -= 6
    pet.clamp()
    return "Bit had fun."

def medicine_pet(pet):
    if pet.asleep:
        return "Bit is asleep..."

    if pet.health >= 75:
        pet.happiness -= 5
        pet.clamp()
        return "Bit did not need that."

    pet.health += 45
    pet.happiness *= 0.5
    pet.clamp()
    return "Medicine administered."

def energy_treat_pet(pet):
    if pet.asleep:
        return "Bit is asleep..."

    if pet.energy >= 90:
        pet.happiness -= 3
        pet.health -= 2
        pet.clamp()
        return "Bit is too wired."

    pet.energy += 30
    pet.hunger += 5
    pet.happiness += 5
    pet.clamp()
    return "Energy treat eaten."

def clean_pet(pet):
    if pet.mess_count > 0 or pet.pee_count > 0:
        pet.mess_count = 0
        pet.time_since_last_mess = 0
        pet.pee_count = 0
        pet.time_since_last_pee = 0
        pet.cleanliness += 40
        pet.happiness += 2
        pet.clamp()
        return "Room cleaned."

    if pet.asleep:
        return "Bit grumbles but accepts cleaning."

    pet.cleanliness += 28
    pet.happiness -= 2
    pet.clamp()
    return "Clean protocol complete."


def toggle_sleep(pet):
    pet.asleep = not pet.asleep
    return "Sleep mode enabled." if pet.asleep else "Bit wakes up."