def get_mood(pet):
    if pet.asleep:
        return "asleep"

    problems = []

    total_accidents = pet.mess_count + pet.pee_count

    if total_accidents >= 5:
        problems.append(("sick", 95))
    elif total_accidents >= 4:
        problems.append(("sad", 85))
    elif total_accidents >= 2:
        problems.append(("dirty", 75))

    if pet.health <= 35:
        problems.append(("sick", 100 - pet.health + 50))

    if pet.energy <= 45:
        problems.append(("tired", 45 - pet.energy + 45))

    if pet.hunger <= 40:
        problems.append(("hungry", 40 - pet.hunger + 40))

    if pet.cleanliness <= 40:
        problems.append(("dirty", 40 - pet.cleanliness + 35))

    if pet.happiness <= 40:
        problems.append(("sad", 40 - pet.happiness + 35))

    if problems:
        problems.sort(key=lambda item: item[1], reverse=True)
        return problems[0][0]

    if (
        pet.hunger >= 70
        and pet.happiness >= 70
        and pet.cleanliness >= 70
        and pet.energy >= 60
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