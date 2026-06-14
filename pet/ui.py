import pygame

from pet.config import SCREEN_WIDTH, SCREEN_HEIGHT


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
        {"label": "Feed", "action": "feed", "icon": "feed", "color": (235, 185, 95)},
        {"label": "Play", "action": "play", "icon": "play", "color": (120, 180, 255)},
        {"label": "Clean", "action": "clean", "icon": "clean", "color": (150, 220, 220)},
        {"label": sleep_label, "action": "sleep", "icon": "sleep" if not pet.asleep else "wake", "color": (190, 170, 255)},
    ]

    if not pet.asleep and pet.energy < 60:
        options.append({"label": "Treat", "action": "energy_treat", "icon": "treat", "color": (255, 180, 180)})

    if not pet.asleep and pet.health < 75:
        options.append({"label": "Meds", "action": "medicine", "icon": "medicine", "color": (255, 100, 100)})

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

    for index in range(min(count, len(positions))):
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

    for index in range(min(count, len(positions))):
        x, y = positions[index]

        pygame.draw.ellipse(screen, pee_color, (x, y, 24, 8))
        pygame.draw.ellipse(screen, pee_light, (x + 5, y + 2, 8, 2))

def draw_icon(screen, icon_name, x, y, color):
    """
    Draw tiny portable menu icons using Pygame shapes.
    This avoids emoji/font issues on Windows and Raspberry Pi.
    """
    if icon_name == "feed":
        # Bowl
        pygame.draw.arc(screen, color, (x, y + 5, 14, 10), 0, 3.14, 2)
        pygame.draw.line(screen, color, (x + 2, y + 11), (x + 12, y + 11), 2)
        pygame.draw.circle(screen, color, (x + 7, y + 4), 2)

    elif icon_name == "play":
        # Ball
        pygame.draw.circle(screen, color, (x + 7, y + 7), 6, 1)
        pygame.draw.line(screen, color, (x + 2, y + 7), (x + 12, y + 7), 1)
        pygame.draw.line(screen, color, (x + 7, y + 2), (x + 7, y + 12), 1)

    elif icon_name == "clean":
        # Broom
        pygame.draw.line(screen, color, (x + 3, y + 2), (x + 10, y + 10), 2)
        pygame.draw.polygon(screen, color, [(x + 8, y + 9), (x + 14, y + 12), (x + 6, y + 14)])

    elif icon_name == "sleep":
        # Zzz
        pygame.draw.line(screen, color, (x + 2, y + 3), (x + 8, y + 3), 1)
        pygame.draw.line(screen, color, (x + 8, y + 3), (x + 2, y + 9), 1)
        pygame.draw.line(screen, color, (x + 2, y + 9), (x + 8, y + 9), 1)
        pygame.draw.line(screen, color, (x + 9, y + 8), (x + 14, y + 8), 1)
        pygame.draw.line(screen, color, (x + 14, y + 8), (x + 9, y + 13), 1)
        pygame.draw.line(screen, color, (x + 9, y + 13), (x + 14, y + 13), 1)

    elif icon_name == "medicine":
        # Syringe
        pygame.draw.line(screen, color, (x + 3, y + 11), (x + 11, y + 3), 2)
        pygame.draw.line(screen, color, (x + 9, y + 2), (x + 13, y + 6), 1)
        pygame.draw.line(screen, color, (x + 2, y + 12), (x, y + 14), 1)

    elif icon_name == "treat":
        # Candy
        pygame.draw.rect(screen, color, (x + 4, y + 4, 7, 7), 1)
        pygame.draw.polygon(screen, color, [(x + 4, y + 5), (x, y + 3), (x + 2, y + 8)])
        pygame.draw.polygon(screen, color, [(x + 11, y + 5), (x + 15, y + 3), (x + 13, y + 8)])
    
    elif icon_name == "wake":
        # Sun
        pygame.draw.circle(screen, color, (x + 7, y + 7), 4, 1)
        pygame.draw.line(screen, color, (x + 7, y), (x + 7, y + 2), 1)
        pygame.draw.line(screen, color, (x + 7, y + 12), (x + 7, y + 14), 1)
        pygame.draw.line(screen, color, (x, y + 7), (x + 2, y + 7), 1)
        pygame.draw.line(screen, color, (x + 12, y + 7), (x + 14, y + 7), 1)
        pygame.draw.line(screen, color, (x + 2, y + 2), (x + 4, y + 4), 1)
        pygame.draw.line(screen, color, (x + 12, y + 2), (x + 10, y + 4), 1)
        
def draw_menu(screen, font, small_font, pet, selected_menu_index):
    menu_top = 222
    menu_height = 36
    menu_options = get_menu_options(pet)

    columns = 4
    cell_width = SCREEN_WIDTH // columns
    cell_height = menu_height // 2

    for index, option in enumerate(menu_options):
        col = index % columns
        row = index // columns

        x = col * cell_width
        y = menu_top + row * cell_height

        rect = pygame.Rect(x + 6, y + 1, cell_width - 12, cell_height - 2)
        
        icon_color = option.get("color", TEXT)

        if index == selected_menu_index:
            pygame.draw.rect(screen, (70, 90, 130), rect, border_radius=4)
            pygame.draw.rect(screen, (180, 210, 255), rect, 1, border_radius=4)
            color = icon_color
        else:
            color = tuple(max(60, int(channel * 0.65)) for channel in icon_color)

        icon_x = rect.centerx - 7
        icon_y = rect.centery - 7

        draw_icon(screen, option["icon"], icon_x, icon_y, color)

def get_selected_action(pet, selected_menu_index):
    menu_options = get_menu_options(pet)
    return menu_options[selected_menu_index]["action"]