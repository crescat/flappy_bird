import pygame
import time
import random

WIDTH = 700
HEIGHT = 500
FPS = 60
GRAVITY = -400
PILLAR_WIDTH = 60
PILLAR_SPEED = 2
FONT = 'Uroob, Bold'


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
        pygame.sprite.Sprite.__init__(self)
        self.image = Bird.image
        self.rect = self.image.get_rect()
        self.x = startpos[0]
        self.height = startpos[1] - self.rect[1]
        self.radius = self.rect.height // 2
        self.time_start_falling = time.monotonic()
        self.velocity = 0
        self.collided = False


    def update_position(self):
        falling_time = time.monotonic() - self.time_start_falling
        self.time_start_falling = time.monotonic()
        self.velocity -= GRAVITY * falling_time
        self.height += self.velocity * falling_time


    def jump(self):
        self.velocity = -250
        self.time_start_falling = time.monotonic()


    def update(self):
        if not self.area.contains(self.rect):
            self.collided = True
        else:
            self.rect.x = self.x
            self.rect.y = self.height


class Pillar(pygame.sprite.Sprite):
    image = pygame.image.load('pillar.png')
    image = pygame.transform.scale(image, (PILLAR_WIDTH, HEIGHT))
    def __init__(self, height):
        pygame.sprite.Sprite.__init__(self)
        self.image = Pillar.image
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH
        self.rect.y = height
        self.dx = PILLAR_SPEED
        self.passed = False

    def update(self):
        self.rect.x -= self.dx

    def is_out_of_screen(self):
        return self.rect.topright[0] < 0


class PygView:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.background = pygame.Surface(self.screen.get_size()).convert()
        self.background_clock = Clock(FPS)
        self.render_clock = Clock(FPS)
        self.bird_clock = Clock(FPS)
        self.pillar_clock = Clock(.5)
        self.font = pygame.font.SysFont(FONT, 100)
        self.clock = pygame.time.Clock()


    def start_game(self):
        self.bg_1 = 0
        self.bg_2 = bg_width
        self.state = 'running'
        self.score = 0


    def get_input(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                elif event.key == pygame.K_SPACE:
                    return 'space'


    def check_collision(self, rectangle, circle):
        # rectangle = (x, y, width, height)
        # circle = (centerx, centery, radius)
        def dist(a, b):
            x1, y1 = a
            x2, y2 = b
            return ((x2-x1)**2 + (y2-y1)**2)**0.5

        x, y, width, height = rectangle
        cx, cy, radius = circle
        topleft, topright = (x, y), (x+width, y)
        bottomleft, bottomright = (x, y+height), (x+width, y+height)
        center = (cx, cy)

        if y < 0: # upper pillar
            if cx + radius > x and cy <= y+height:
                return True
            if cy - radius < y+height and cx>=x and cx<=x+width:
                return True

        if y > 0: # lower pillar
            if cx + radius > x and cy >= y:
                return True
            if cy + radius > y and cx>=x and cx<=x+width:
                return True

        for point in [topleft, topright, bottomleft, bottomright]:
            if dist(point, center) < radius:
                return True
        return False


    def new_pillar(self):
        position = random.randint(50, HEIGHT-HEIGHT//3)
        gap = random.randint(HEIGHT//4, HEIGHT//3)
        upper_pillar = Pillar(position-HEIGHT)
        lower_pillar = Pillar(position + gap)
        return upper_pillar, lower_pillar


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
        all_groups = pygame.sprite.Group()
        pillar_groups = pygame.sprite.Group()
        Bird.area = self.screen.get_rect()
        bird = Bird()
        all_groups.add(bird)

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

                if self.bird_clock.should_update():
                    bird.update_position()
                    for pillar in pillar_groups:
                        if pillar.is_out_of_screen():
                            all_groups.remove(pillar)
                            pillar_groups.remove(pillar)

                        if not pillar.passed:
                            rect = (pillar.rect.x, pillar.rect.y, PILLAR_WIDTH, HEIGHT)
                            circle = (*bird.rect.center, bird.radius)
                            if self.check_collision(rect, circle):
                                self.state = 'game over'
                            elif pillar.rect.topright[0] < bird.rect.x:
                                pillar.passed = True
                                self.score += 0.5



                if self.pillar_clock.should_update():
                    upper_pillar, lower_pillar = self.new_pillar()
                    all_groups.add(upper_pillar)
                    all_groups.add(lower_pillar)
                    pillar_groups.add(upper_pillar)
                    pillar_groups.add(lower_pillar)


            elif self.state == 'game over':
                if event == 'space':
                    self.start_game()
                    all_groups.empty()
                    pillar_groups.empty()
                    bird = Bird()
                    all_groups.add(bird)
                    self.state == 'running'


            if self.render_clock.should_update():
                self.clock.tick()
                if self.state == 'running':
                    self.screen.blit(self.background, (0, 0))
                    all_groups.clear(self.screen, self.background)
                    all_groups.update()
                    all_groups.draw(self.screen)
                elif self.state == 'game over':
                    text = self.font.render('GAME OVER', False, (255, 255, 255))
                    text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2))
                    self.screen.blit(text, text_rect)

                text = 'FPS: {0:.2f}, Score: {1}'.format(self.clock.get_fps(), int(self.score))
                pygame.display.set_caption(text)
                pygame.display.update()

        pygame.quit()


if __name__ == '__main__':
    PygView().run()
