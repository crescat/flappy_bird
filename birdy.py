import pygame
import time

WIDTH = 700
HEIGHT = 500
FPS = 60
GRAVITY = -150


bird = pygame.image.load('bird.png')
bird_length, bird_width = bird.get_rect().size

class Clock:
    def __init__(self, ups):
        self.ups = ups
        self.prev_time = time.monotonic()
        self.paused = False

    def should_update(self):
        if self.paused:
            return False
        now = time.monotonic()
        if now - self.prev_time >= 1 / self.ups:
            self.prev_time = now
            return True
        return False

    def pause(self):
        self.paused = True

    def unpause(self):
        self.paused = False

    def set_ups(self, new_ups):
        self.ups = new_ups


class PygView:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Press ESC to quit")
        pygame.font.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.render_clock = Clock(FPS)
        self.gravity_clock = Clock(FPS)
        self.background.fill((255,255,255))


    def calculate_position(self):
        falling_time = time.monotonic() - self.time_start_falling
        return self.initial_velocity * falling_time \
               + self.initial_height \
               - 0.5 * GRAVITY * falling_time**2


    def start_game(self):
        self.time_start_falling = time.monotonic()
        self.initial_velocity = 0
        self.initial_height = 50
        self.height = 50


    def get_input(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                elif event.key == pygame.K_SPACE:
                    return 'space'


    def run(self):
        self.screen.blit(self.background, (0,0))
        mainloop = True
        self.start_game()

        while mainloop:
            event = self.get_input(pygame.event.get())
            if event is False:
                mainloop = False

            if event == 'space':
                self.initial_velocity = -150
                self.initial_height = self.height
                self.time_start_falling = time.monotonic()

            if self.gravity_clock.should_update:
                self.height = self.calculate_position()

            if self.render_clock.should_update:
                self.background.fill((255,255,255))
                self.background.blit(bird, (WIDTH//4, self.height))
                self.screen.blit(self.background, (0, 0))
            pygame.display.update()

        pygame.quit()


if __name__ == '__main__':
    PygView().run()
