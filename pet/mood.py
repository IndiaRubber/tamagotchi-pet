def get_mood(pet):
    if pet.asleep:
        return "asleep"

    problems = []

    total_accidents = pet.mess_count + pet.pee_count

# Accident-based moods
    if total_accidents >= 5:
        problems.append(("sick", 95))
    elif total_accidents >= 4:
        problems.append(("sad", 85))
    elif total_accidents >= 2:
        problems.append(("dirty", 75))

    # Stat-based moods
    if pet.health <= 25:
        problems.append(("sick", 100 - pet.health + 40))

    if pet.hunger <= 20:
        problems.append(("hungry", 20 - pet.hunger + 30))

    if pet.cleanliness <= 20:
        problems.append(("dirty", 20 - pet.cleanliness + 25))

    if pet.energy <= 20:
        problems.append(("tired", 20 - pet.energy + 20))

    if pet.happiness <= 25:
        problems.append(("sad", 25 - pet.happiness + 10))

    if problems:
        problems.sort(key=lambda item: item[1], reverse=True)
        return problems[0][0]

    if (
        pet.hunger >= 70
        and pet.happiness >= 70
        and pet.cleanliness >= 70
        and pet.energy >= 50
        and pet.health >= 70
    ):
        return "happy"

    return "idle"


def get_mood_label(mood):
    labels = {
        "happy": "HAPPY",
        "idle": "OKAY",
        "hungry": "HUNGRY",
        "dirty": "DIRTY",
        "tired": "TIRED",
        "sad": "SAD",
        "sick": "SICK",
        "asleep": "ASLEEP",
    }

    return labels.get(mood, "UNKNOWN")


def get_mood_message(mood):
    messages = {
        "happy": "Bit is thriving.",
        "idle": "Bit is vibing.",
        "hungry": "Bit wants snacks.",
        "dirty": "Bit's room is gross.",
        "tired": "Bit is sleepy.",
        "sad": "Bit is upset.",
        "sick": "Bit is unwell.",
        "asleep": "Bit is dreaming.",
    }

    return messages.get(mood, "Bit exists mysteriously.")