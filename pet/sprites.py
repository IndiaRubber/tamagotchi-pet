# pet/sprites.py

import os
import pygame

from pet.evolution import get_evolution_stage, get_evolution_modifier


SPRITE_SIZE = (128, 128)

MOODS = [
    "idle",
    "happy",
    "hungry",
    "dirty",
    "tired",
    "sad",
    "sick",
    "sleep",
]


def load_image(path):
    image = pygame.image.load(str(path))

    try:
        return image.convert_alpha()
    except pygame.error:
        return image.copy()


def load_animation_frames(folder, animation_name):
    frames = []
    frame_number = 0

    while True:
        filename = f"{animation_name}_{frame_number}.png"
        path = os.path.join(folder, filename)

        if not os.path.exists(path):
            break

        frames.append(load_image(path))
        frame_number += 1

    return frames


def load_sprites():
    sprites = {}

    base_dir = os.path.join("assets", "pets")

    for stage in ["egg", "baby", "child", "teen"]:
        stage_dir = os.path.join(base_dir, stage)

        if not os.path.isdir(stage_dir):
            continue

        sprites[stage] = {}

        for mood in MOODS:
            frames = load_animation_frames(stage_dir, mood)

            if frames:
                sprites[stage][mood] = frames

    adult_dir = os.path.join(base_dir, "adult")

    if os.path.isdir(adult_dir):
        sprites["adult"] = {}

        for form in ["excellent", "normal", "rough"]:
            form_dir = os.path.join(adult_dir, form)

            if not os.path.isdir(form_dir):
                continue

            sprites["adult"][form] = {}

            for mood in MOODS:
                frames = load_animation_frames(form_dir, mood)

                if frames:
                    sprites["adult"][form][mood] = frames

    return sprites


def choose_sprite_frames(pet, sprites, mood):
    stage = get_evolution_stage(pet).value

    if mood == "asleep":
        mood = "sleep"

    if stage == "adult":
        form = get_evolution_modifier(pet)

        adult_sprites = sprites.get("adult", {})
        form_sprites = adult_sprites.get(form, {})
        normal_sprites = adult_sprites.get("normal", {})

        return (
            form_sprites.get(mood)
            or form_sprites.get("idle")
            or normal_sprites.get(mood)
            or normal_sprites.get("idle")
            or sprites.get("baby", {}).get(mood)
            or sprites.get("baby", {}).get("idle")
            or []
        )

    stage_sprites = sprites.get(stage, {})

    return (
        stage_sprites.get(mood)
        or stage_sprites.get("idle")
        or sprites.get("baby", {}).get(mood)
        or sprites.get("baby", {}).get("idle")
        or []
    )