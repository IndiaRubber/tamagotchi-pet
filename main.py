import os
import platform
import pygame
import time

from io_layer.windows_io import WindowsIO

from pet.config import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_SIZE, FPS
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

from pet.ui import (
    BG,
    PANEL,
    TEXT,
    DIM,
    get_menu_options,
    draw_text,
    draw_bar,
    draw_mess,
    draw_pee,
    draw_menu,
    get_selected_action,
)

from pet.sprites import load_sprites, choose_sprite
from pet.mood import get_mood, get_mood_label, get_mood_message
from pet.sounds import SoundManager


def create_io():
    return WindowsIO()




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

def create_display():
    if platform.system() == "Linux" and os.path.exists(os.path.expanduser("~/Whisplay/runtime")):
        from io_layer.whisplay_display import WhisplayDisplay

        display = WhisplayDisplay()
        screen = pygame.Surface(SCREEN_SIZE)
        return screen, display

    screen = pygame.display.set_mode(SCREEN_SIZE)
    return screen, None

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

    draw_menu(screen, font, small_font, pet, selected_menu_index)
        
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

    screen = pygame.display.set_mode(SCREEN_SIZE)
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
                selected_action = get_selected_action(pet, selected_menu_index)
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
        
        if whisplay_display:
            whisplay_display.flip(screen)
        else:
            pygame.display.flip()

    save_pet(pet)

    if whisplay_display:
        whisplay_display.cleanup()

    pygame.quit()


if __name__ == "__main__":
    main()