import time


class WhisplayIO:
    """
    Whisplay hardware input layer.

    Current controls:
    - Short press: move to next menu item
    - Long press: select current menu item
    """

    def __init__(self, board):
        self.board = board
        self.running = True
        self.actions = []
        self.button_down_at = None
        self.long_press_seconds = 0.65

        self.board.on_button_press(self._on_button_press)
        self.board.on_button_release(self._on_button_release)

        if hasattr(self.board, "on_exit_request"):
            self.board.on_exit_request(self._on_exit_request)

        if hasattr(self.board, "on_focus_revoked"):
            self.board.on_focus_revoked(self._on_focus_revoked)

    def _on_button_press(self):
        self.button_down_at = time.time()

    def _on_button_release(self):
        if self.button_down_at is None:
            return

        held_seconds = time.time() - self.button_down_at
        self.button_down_at = None

        if held_seconds >= self.long_press_seconds:
            self.actions.append("select")
        else:
            self.actions.append("menu_down")

    def _on_exit_request(self, _payload=None):
        self.running = False

    def _on_focus_revoked(self, _payload=None):
        self.running = False

    def poll_events(self):
        pending_actions = self.actions[:]
        self.actions.clear()
        return pending_actions
