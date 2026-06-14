# pet/evolution.py

from enum import Enum


class EvolutionStage(str, Enum):
    EGG = "egg"
    BABY = "baby"
    CHILD = "child"
    TEEN = "teen"
    ADULT = "adult"


def get_evolution_stage(state) -> EvolutionStage:
    """
    Decide Bit's current evolution stage.

    For now this is based on age in minutes so testing is not miserable.
    Later we can switch this to real hours/days.
    """

    age_minutes = getattr(state, "age_minutes", 0)

    if age_minutes < 2:
        return EvolutionStage.EGG

    if age_minutes < 5:
        return EvolutionStage.BABY

    if age_minutes < 15:
        return EvolutionStage.CHILD

    if age_minutes < 30:
        return EvolutionStage.TEEN

    return EvolutionStage.ADULT


def get_evolution_modifier(state) -> str:
    """
    Optional future branching.

    This lets Bit become different adult forms depending on care quality.
    For now, return 'normal'.
    """

    hunger = getattr(state, "hunger", 100)
    happiness = getattr(state, "happiness", 100)
    energy = getattr(state, "energy", 100)
    cleanliness = getattr(state, "cleanliness", 100)

    average_care = (hunger + happiness + energy + cleanliness) / 4

    if average_care >= 80:
        return "excellent"

    if average_care >= 50:
        return "normal"

    return "rough"