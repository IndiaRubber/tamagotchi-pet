import time

from pet.config import WHISPLAY_BACKLIGHT

from pathlib import Path


class WhisplayIO:
    """
    Whisplay hardware input layer.

    Controls:
    - Short press: move to next menu item
    - Long press: select current menu item

    Screen sleep:
    - After idle_sleep_seconds with no button input, backlight turns off.
    - First button press wakes the screen only.
    - That wake press does NOT trigger menu_down or select.
    """

    def __init__(self, board):
        self.board = board
        self.running = True
        self.actions = []

        self.button_down_at = None
        self.long_press_seconds = 0.65

        self.idle_sleep_seconds = 120
        self.last_input_at = time.time()

        self.screen_sleeping = False
        self.awake_backlight = WHISPLAY_BACKLIGHT
        self.sleep_backlight = 0
        
        self.sleep_request_file = Path("/tmp/tamagotchi_sleep")

        self._press_started_while_sleeping = False

        self.board.on_button_press(self._on_button_press)
        self.board.on_button_release(self._on_button_release)

        if hasattr(self.board, "on_exit_request"):
            self.board.on_exit_request(self._on_exit_request)

        if hasattr(self.board, "on_focus_revoked"):
            self.board.on_focus_revoked(self._on_focus_revoked)

    def _set_backlight(self, brightness):
        try:
            self.board.set_backlight(brightness)
        except Exception as exc:
            print(f"Whisplay backlight error: {exc}")

    def sleep_screen(self):
        if self.screen_sleeping:
            return

        self.screen_sleeping = True
        self._set_backlight(self.sleep_backlight)
        self.actions.append("screen_sleep")

    def wake_screen(self):
        if not self.screen_sleeping:
            return

        self.screen_sleeping = False
        self.last_input_at = time.time()
        self._set_backlight(self.awake_backlight)
        self.actions.append("screen_wake")

    def _on_button_press(self):
        self.last_input_at = time.time()
        self.button_down_at = time.time()

        self._press_started_while_sleeping = self.screen_sleeping

        if self.screen_sleeping:
            self.wake_screen()

    def _on_button_release(self):
        if self.button_down_at is None:
            return

        held_seconds = time.time() - self.button_down_at
        self.button_down_at = None
        self.last_input_at = time.time()

        # If the press started while the screen was asleep, use it only as wake.
        # Do not also treat it as menu_down/select.
        if self._press_started_while_sleeping:
            self._press_started_while_sleeping = False
            return

        if held_seconds >= self.long_press_seconds:
            self.actions.append("select")
        else:
            self.actions.append("menu_down")

    def _on_exit_request(self, _payload=None):
        self.running = False

    def _on_focus_revoked(self, _payload=None):
        self.running = False

    def poll_events(self):
        now = time.time()

        if self.sleep_request_file.exists():
            try:
                self.sleep_request_file.unlink()
            except OSError:
                pass

            self.last_input_at = now
            self.sleep_screen()

        if not self.screen_sleeping:
            idle_seconds = now - self.last_input_at

            if idle_seconds >= self.idle_sleep_seconds:
                self.sleep_screen()

        pending_actions = self.actions[:]
        self.actions.clear()
        return pending_actions
