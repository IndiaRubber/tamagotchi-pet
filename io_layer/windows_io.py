import pygame


class WindowsIO:
    def __init__(self):
        self.running = True

    def poll_events(self):
        actions = []

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                elif event.key in (pygame.K_UP, pygame.K_w):
                    actions.append("menu_up")

                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    actions.append("menu_down")

                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    actions.append("select")
                    
                elif event.key == pygame.K_m:
                    actions.append("debug_next_mood")

        return actions