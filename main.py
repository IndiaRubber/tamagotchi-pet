import pygame
import time
from pet.sounds import SoundManager

from pet.save import load_pet, save_pet
from pet.logic import (
    apply_offline_progress,
    update_pet,
    feed_pet,
    play_with_pet,
    clean_pet,
    medicine_pet,
    energy_treat_pet,
    toggle_sleep,
)
from pet.sprites import load_sprites, choose_sprite
from io_layer.windows_io import WindowsIO
from pet.mood import get_mood, get_mood_label, get_mood_message

def create_io():
    return WindowsIO()

SCREEN_WIDTH = 240
SCREEN_HEIGHT = 280
FPS = 30


DEBUG_MOODS = [
    "idle",
    "happy",
    "hungry",
    "dirty",
    "tired",
    "sad",
    "sick",
    "asleep",
]

BG = (18, 22, 28)
PANEL = (32, 38, 48)
TEXT = (230, 230, 230)
DIM = (150, 160, 170)
BAR_BACK = (60, 65, 75)
BAR_FILL = (180, 220, 180)
WARNING = (240, 190, 80)
DANGER = (240, 110, 110)

def get_menu_options(pet):
    sleep_label = "Wake" if pet.asleep else "Sleep"

    options = [
        ("Feed", "feed"),
        ("Play", "play"),
        ("Clean", "clean"),
        (sleep_label, "sleep"),
    ]
    
    if not pet.asleep and pet.energy < 60:
        options.append(("Treat", "energy_treat"))
    if not pet.asleep and pet.health < 75:
        options.append(("Meds", "medicine"))

    return options

def draw_text(screen, font, text, x, y, color=TEXT):
    image = font.render(text, True, color)
    screen.blit(image, (x, y))


def draw_bar(screen, font, label, value, x, y):
    draw_text(screen, font, label, x, y, DIM)

    bar_x = x + 72
    bar_y = y + 3
    bar_w = 120
    bar_h = 9

    pygame.draw.rect(screen, BAR_BACK, (bar_x, bar_y, bar_w, bar_h), border_radius=3)

    fill_w = int(bar_w * (value / 100))

    if value < 20:
        color = DANGER
    elif value < 45:
        color = WARNING
    else:
        color = BAR_FILL

    pygame.draw.rect(screen, color, (bar_x, bar_y, fill_w, bar_h), border_radius=3)

def draw_mess(screen, count):
    poop_color = (110, 75, 45)
    poop_dark = (70, 45, 30)

    positions = [
        (48, 116),
        (120, 118),
        (190, 116),
    ]

    for index in range(count):
        x, y = positions[index]

        pygame.draw.ellipse(screen, poop_color, (x, y + 8, 18, 8))
        pygame.draw.ellipse(screen, poop_color, (x + 3, y + 3, 12, 8))
        pygame.draw.ellipse(screen, poop_color, (x + 7, y, 6, 6))
        pygame.draw.circle(screen, poop_dark, (x + 5, y + 11), 1)
        pygame.draw.circle(screen, poop_dark, (x + 12, y + 10), 1)

def draw_pee(screen, count):
    pee_color = (210, 190, 70)
    pee_light = (235, 220, 110)

    positions = [
        (34, 124),
        (104, 124),
        (174, 124),
    ]

    for index in range(count):
        x, y = positions[index]

        pygame.draw.ellipse(screen, pee_color, (x, y, 24, 8))
        pygame.draw.ellipse(screen, pee_light, (x + 5, y + 2, 8, 2))

def draw_ui(screen, font, small_font, pet, sprites, message, message_timer, selected_menu_index, debug_mood=None):
    screen.fill(BG)

    pygame.draw.rect(screen, PANEL, (8, 8, 224, 264), border_radius=12)

    draw_text(screen, font, f"{pet.name}", 16, 16)

    mood = debug_mood or get_mood(pet)
    status = get_mood_label(mood)
    draw_text(screen, small_font, status, 164, 20, DIM)

    sprite_name = choose_sprite(pet, message_timer, debug_mood)
    sprite = sprites[sprite_name]

    sprite_rect = sprite.get_rect(center=(120, 82))
    

    draw_pee(screen, pet.pee_count)
    draw_mess(screen, pet.mess_count)
    
    screen.blit(sprite, sprite_rect)
    


    draw_bar(screen, small_font, "Hunger", pet.hunger, 18, 132)
    draw_bar(screen, small_font, "Happy", pet.happiness, 18, 151)
    draw_bar(screen, small_font, "Clean", pet.cleanliness, 18, 170)
    draw_bar(screen, small_font, "Energy", pet.energy, 18, 189)
    draw_bar(screen, small_font, "Health", pet.health, 18, 208)

    # Menu area
    menu_y = 226
    menu_x_left = 28
    menu_x_right = 142

    menu_options = get_menu_options(pet)

    for index, (label, action) in enumerate(menu_options):
        row = index // 2
        col = index % 2

        x = menu_x_left if col == 0 else menu_x_right
        y = menu_y + row * 11

        prefix = ">" if index == selected_menu_index else " "
        color = TEXT if index == selected_menu_index else DIM

        draw_text(screen, small_font, f"{prefix}{label}", x, y, color)
        
    # Message / mood line
    message_box_y = 258

    if message_timer > 0:
        pygame.draw.rect(screen, PANEL, (14, message_box_y, 210, 12))
        draw_text(screen, small_font, message, 18, message_box_y, TEXT)
    else:
        mood = debug_mood or get_mood(pet)
        mood_message = get_mood_message(mood)
        pygame.draw.rect(screen, PANEL, (14, message_box_y, 210, 12))
        draw_text(screen, small_font, mood_message, 18, message_box_y, DIM)

def main():
    pygame.init()
    pygame.display.set_caption("Tamagotchi Pi Prototype")

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("consolas", 18)
    small_font = pygame.font.SysFont("consolas", 12)

    io = create_io()
    pet = load_pet()
    apply_offline_progress(pet)

    sprites = load_sprites()
    sounds = SoundManager()

    message = "Bit has booted."
    message_timer = 1.5
    selected_menu_index = 0

    debug_mood_index = None

    last_save = time.time()

    while io.running:
        dt = clock.tick(FPS) / 1000.0

        actions = io.poll_events()

        for action in actions:
            if action == "menu_up":
                selected_menu_index = (selected_menu_index - 1) % len(get_menu_options(pet))
                sounds.play("menu")

            elif action == "menu_down":
                selected_menu_index = (selected_menu_index + 1) % len(get_menu_options(pet))
                sounds.play("menu")
            
            elif action == "debug_next_mood":
                if debug_mood_index is None:
                    debug_mood_index = 0
                else:
                    debug_mood_index = (debug_mood_index + 1) % len(DEBUG_MOODS)

                message = f"DEBUG: {DEBUG_MOODS[debug_mood_index]}"
                message_timer = 1.5

            elif action == "select":
                selected_action = get_menu_options(pet)[selected_menu_index][1]
                sounds.play("select")

                if selected_action == "feed":
                    message = feed_pet(pet)
                    sounds.play("feed" if "asleep" not in message.lower() else "error")
                    message_timer = 3.0

                elif selected_action == "play":
                    message = play_with_pet(pet)
                    sounds.play("play" if "asleep" not in message.lower() and "too tired" not in message.lower() else "error")
                    message_timer = 3.0

                elif selected_action == "clean":
                    message = clean_pet(pet)
                    sounds.play("clean")
                    message_timer = 3.0
                
                elif selected_action == "energy_treat":
                    message = energy_treat_pet(pet)
                    sounds.play("treat" if "eaten" in message.lower() else "error")
                    message_timer = 3.0
                
                elif selected_action == "medicine":
                    message = medicine_pet(pet)
                    sounds.play("medicine" if "administered" in message.lower() else "error")
                    message_timer = 3.0

                elif selected_action == "sleep":
                    was_asleep = pet.asleep
                    message = toggle_sleep(pet)
                    sounds.play("wake" if was_asleep else "sleep")
                    message_timer = 3.0

        pet_events = update_pet(pet, dt) or []

        for event in pet_events:
            if event == "mess_created":
                sounds.play("poop")
                message = "Uh oh..."
                message_timer = 2.0

            elif event == "pee_created":
                sounds.play("pee")
                message = "Tiny accident..."
                message_timer = 2.0

        selected_menu_index %= len(get_menu_options(pet))

        if message_timer > 0:
            message_timer -= dt

        if time.time() - last_save > 5:
            save_pet(pet)
            last_save = time.time()

        debug_mood = DEBUG_MOODS[debug_mood_index] if debug_mood_index is not None else None

        draw_ui(
            screen,
            font,
            small_font,
            pet,
            sprites,
            message,
            message_timer,
            selected_menu_index,
            debug_mood,
        )
        
        pygame.display.flip()

    save_pet(pet)
    pygame.quit()


if __name__ == "__main__":
    main()