import pygame
import time

WIDTH = 700
HEIGHT = 500
FPS = 60
GRAVITY = -300


bg = pygame.image.load('background.png')
bg_width, bg_height = bg.get_rect().size


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


class Bird(pygame.sprite.Sprite):
    image = pygame.image.load('bird.png')

    def __init__(self, startpos=(WIDTH//5, HEIGHT//2)):
       pygame.sprite.Sprite.__init__(self, self.groups)
       self.image = Bird.image
       self.rect = self.image.get_rect()
       self.dx = startpos[0]
       self.height = startpos[1] - self.rect[1]
       self.radius = self.rect[0] // 2 - 3
       self.time_start_falling = time.monotonic()
       self.initial_velocity = 0
       self.initial_height = self.height
       self.collided = False


    def update_position(self):
        falling_time = time.monotonic() - self.time_start_falling
        self.height = self.initial_velocity * falling_time \
                    + self.initial_height \
                    - 0.5 * GRAVITY * falling_time * falling_time


    def jump(self):
        self.initial_velocity = -250
        self.initial_height = self.height
        self.time_start_falling = time.monotonic()


    def update(self):
        if not self.area.contains(self.rect):
            self.collided = True
        else:
            self.rect.center = (self.dx, self.height)


class Wall(pygame.sprite.Sprite):
    def __init__(self):
       pygame.sprite.Sprite.__init__(self, self.groups)


class PygView:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Press ESC to quit")
        pygame.font.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background_clock = Clock(FPS)
        self.render_clock = Clock(FPS)
        self.gravity_clock = Clock(FPS)
        self.wall_clock = Clock(FPS)
        self.clock = pygame.time.Clock()


    def start_game(self):
        self.bg_1 = 0
        self.bg_2 = bg_width
        self.state = 'running'


    def get_input(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                elif event.key == pygame.K_SPACE:
                    return 'space'


    def check_background(self):
        if self.bg_1 < -bg_width:
            self.bg_1 = bg_width
        if self.bg_2 < -bg_width:
            self.bg_2 = bg_width


    def blit_background(self):
        self.background.blit(bg, (self.bg_1, 0))
        self.background.blit(bg, (self.bg_2, 0))
        self.check_background()


    def run(self):
        self.background.blit(bg, (0, 0))
        self.screen.blit(self.background, (0, 0))
        mainloop = True
        allgroups = pygame.sprite.Group()
        Bird.groups = allgroups
        Bird.area = self.screen.get_rect()
        bird = Bird()
        self.start_game()

        while mainloop:
            event = self.get_input(pygame.event.get())
            if event is False:
                mainloop = False

            if self.state == 'running':
                if event == 'space':
                    bird.jump()

                if bird.collided:
                    self.state = 'game over'

                if self.background_clock.should_update():
                    self.bg_1 -= 1
                    self.bg_2 -= 1
                    self.blit_background()

                if self.gravity_clock.should_update():
                    bird.update_position()

            if self.render_clock.should_update():
                self.clock.tick()
                self.screen.blit(self.background, (0, 0))
                allgroups.clear(self.screen, self.background)
                allgroups.update()
                allgroups.draw(self.screen)

            text = 'FPS: {0:.2f}'.format(self.clock.get_fps())
            pygame.display.set_caption(text)
            pygame.display.update()

        pygame.quit()


if __name__ == '__main__':
    PygView().run()
