import math
import wave
from array import array
from pet.paths import SOUND_DIR

import pygame

SAMPLE_RATE = 44100


def ensure_sound_dir():
    SOUND_DIR.mkdir(parents=True, exist_ok=True)


def generate_tone(filename, notes, volume=0.35):
    """
    notes format:
    [
        (frequency_hz, duration_seconds),
        (frequency_hz, duration_seconds),
    ]

    Use frequency 0 for silence.
    """
    ensure_sound_dir()

    path = SOUND_DIR / filename

    if path.exists():
        return path

    samples = array("h")

    for frequency, duration in notes:
        total_samples = int(SAMPLE_RATE * duration)

        for i in range(total_samples):
            if frequency <= 0:
                sample = 0
            else:
                # Square-ish wave for retro chirp
                t = i / SAMPLE_RATE
                raw = math.sin(2 * math.pi * frequency * t)

                # Simple fade to avoid clicks
                fade = min(1.0, i / 400, (total_samples - i) / 400)
                sample = int(32767 * volume * fade * (1 if raw >= 0 else -1))

            samples.append(sample)

    with wave.open(str(path), "w") as file:
        file.setnchannels(1)
        file.setsampwidth(2)
        file.setframerate(SAMPLE_RATE)
        file.writeframes(samples.tobytes())

    return path


class SoundManager:
    def __init__(self):
        self.enabled = True
        self.sounds = {}

        try:
            pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=1)
            self.create_default_sounds()
            self.load_sounds()
        except Exception as error:
            print(f"Sound disabled: {error}")
            self.enabled = False

    def create_default_sounds(self):
        generate_tone("feed.wav", [(660, 0.08), (880, 0.10)])
        generate_tone("play.wav", [(523, 0.06), (659, 0.06), (784, 0.10)])
        generate_tone("clean.wav", [(1200, 0.04), (0, 0.03), (1500, 0.05), (1800, 0.07)])
        generate_tone("sleep.wav", [(660, 0.10), (440, 0.12), (330, 0.18)])
        generate_tone("error.wav", [(220, 0.16), (180, 0.20)])
        generate_tone("wake.wav", [(392, 0.08), (523, 0.08), (659, 0.12)])
        generate_tone("menu.wav", [(900, 0.025)])
        generate_tone("select.wav", [(700, 0.04), (1000, 0.04)])
        generate_tone("poop.wav", [(180, 0.07), (90, 0.12)])
        generate_tone("medicine.wav", [(1000, 0.05), (750, 0.06), (500, 0.10)])
        generate_tone("pee.wav", [(700, 0.04), (500, 0.04), (350, 0.08)])
        generate_tone("treat.wav", [(500, 0.05), (750, 0.05), (1000, 0.08)])

    def load_sounds(self):
        for name in [
            "feed",
            "play",
            "clean",
            "sleep",
            "error",
            "wake",
            "menu",
            "select",
            "poop",
            "pee",
            "medicine",
            "treat",
        ]:
            path = SOUND_DIR / f"{name}.wav"

            if path.exists():
                self.sounds[name] = pygame.mixer.Sound(str(path))
            else:
                print(f"Missing sound: {path}")

    def play(self, name):
        if not self.enabled:
            return

        sound = self.sounds.get(name)

        if sound:
            sound.play()