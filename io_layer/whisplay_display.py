import os
import sys

from PIL import Image

from pet.config import WHISPLAY_BACKLIGHT

def add_whisplay_runtime_to_path():
    """
    The Whisplay demo imports whisplay_client from its runtime folder.
    This tries the common install locations.
    """
    candidates = [
        os.path.expanduser("~/Whisplay/runtime"),
        os.path.expanduser("~/whisplay/runtime"),
        "/opt/whisplay/runtime",
    ]

    for path in candidates:
        if os.path.isdir(path) and path not in sys.path:
            sys.path.append(path)


class WhisplayDisplay:
    def __init__(self):
        add_whisplay_runtime_to_path()

        from whisplay_client import create_whisplay_hardware

        self.board = create_whisplay_hardware(
            app_id=os.getenv("WHISPLAY_APP_ID", "tamagotchi-pet"),
            display_name="Tamagotchi",
            icon="T",
            use_daemon_default_log=True,
        )

        self.board.set_backlight(WHISPLAY_BACKLIGHT)

        self.width = self.board.LCD_WIDTH
        self.height = self.board.LCD_HEIGHT

    def surface_to_rgb565_bytes(self, surface):
        """
        Convert a Pygame Surface into Whisplay RGB565 byte format.
        """
        import pygame

        rgb_bytes = pygame.image.tostring(surface, "RGB")
        image = Image.frombytes("RGB", surface.get_size(), rgb_bytes)

        if image.size != (self.width, self.height):
            image = image.resize((self.width, self.height))

        output = bytearray()

        for r, g, b in image.getdata():
            value = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
            output.append((value >> 8) & 0xFF)
            output.append(value & 0xFF)

        return bytes(output)

    def flip(self, surface):
        frame = self.surface_to_rgb565_bytes(surface)
        self.board.draw_image(0, 0, self.width, self.height, frame)

    def cleanup(self):
        self.board.set_rgb(0, 0, 0)
        self.board.cleanup()