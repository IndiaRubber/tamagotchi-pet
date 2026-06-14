# pet/animation.py

import time


class AnimationPlayer:
    def __init__(self, frame_duration=0.45):
        self.frame_duration = frame_duration
        self.current_key = None
        self.frame_index = 0
        self.last_frame_time = time.time()

    def get_frame(self, key, frames):
        """
        key: a string identifying the current animation, like 'baby_idle'
        frames: list of pygame surfaces
        """

        if not frames:
            return None

        now = time.time()

        if key != self.current_key:
            self.current_key = key
            self.frame_index = 0
            self.last_frame_time = now

        if now - self.last_frame_time >= self.frame_duration:
            self.frame_index = (self.frame_index + 1) % len(frames)
            self.last_frame_time = now

        return frames[self.frame_index]