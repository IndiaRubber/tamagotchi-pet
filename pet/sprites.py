import pygame
from pet.paths import ASSET_DIR

from pet.mood import get_mood



SPRITE_FILES = {
    "idle": "pet_idle.png",
    "happy": "pet_happy.png",
    "hungry": "pet_hungry.png",
    "dirty": "pet_dirty.png",
    "tired": "pet_tired.png",
    "sad": "pet_sad.png",
    "sick": "pet_sick.png",
    "asleep": "pet_sleep.png",
}


def load_image_with_alpha(path):
    image = pygame.image.load(str(path))

    try:
        return image.convert_alpha()
    except pygame.error:
        return image.copy()


def load_sprite(filename, size=(96, 96)):
    path = ASSET_DIR / filename

    if path.exists():
        try:
            image = load_image_with_alpha(path)
            return pygame.transform.scale(image, size)
        except Exception as error:
            print(f"Could not load sprite {filename}: {error}")
            return None

    return None

def create_placeholder_pet(size=(96, 96)):
    surface = pygame.Surface(size, pygame.SRCALPHA)
    w, h = size

    # Body
    pygame.draw.ellipse(surface, (230, 230, 230), (12, 18, w - 24, h - 28))

    # Ears / nubs
    pygame.draw.circle(surface, (230, 230, 230), (26, 24), 12)
    pygame.draw.circle(surface, (230, 230, 230), (w - 26, 24), 12)

    # Eyes
    pygame.draw.circle(surface, (0, 0, 0), (w // 2 - 18, h // 2 - 8), 5)
    pygame.draw.circle(surface, (0, 0, 0), (w // 2 + 18, h // 2 - 8), 5)

    # Mouth
    pygame.draw.arc(surface, (0, 0, 0), (w // 2 - 18, h // 2 - 2, 36, 24), 0, 3.14, 2)

    # Feet
    pygame.draw.ellipse(surface, (210, 210, 210), (22, h - 22, 20, 10))
    pygame.draw.ellipse(surface, (210, 210, 210), (w - 42, h - 22, 20, 10))

    return surface


def create_sleep_placeholder(size=(96, 96)):
    surface = create_placeholder_pet(size)
    w, h = size

    # Cover the happy eyes with sleepy lines
    pygame.draw.rect(surface, (230, 230, 230), (w // 2 - 26, h // 2 - 16, 52, 18))
    pygame.draw.line(surface, (0, 0, 0), (w // 2 - 24, h // 2 - 8), (w // 2 - 12, h // 2 - 8), 2)
    pygame.draw.line(surface, (0, 0, 0), (w // 2 + 12, h // 2 - 8), (w // 2 + 24, h // 2 - 8), 2)

    return surface


def load_sprites():
    sprites = {}

    for mood, filename in SPRITE_FILES.items():
        sprite = load_sprite(filename)

        if sprite is None:
            if mood == "asleep":
                sprites[mood] = create_sleep_placeholder()
            else:
                sprites[mood] = create_placeholder_pet()
        else:
            sprites[mood] = sprite

    return sprites


def choose_sprite(pet, message_timer, debug_mood=None):
    mood = debug_mood or get_mood(pet)

    if mood in SPRITE_FILES:
        return mood

    return "idle"