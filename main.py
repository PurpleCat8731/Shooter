import pygame

from random import randint

from src.constants import MAX_FPS, DISPLAY_SIZE, SHOOT_EVENT, SPAWN_EVENT, HEALTH_BAR_WIDE, PLAYER_HEALTH, PLAYER_SPEED, ENEMY_DAMAGE, ENEMY_SPEED, BULLET_SPEED
from src.player import Player 
from src.bullet import Bullet
from src.enemy import Enemy
from src.utils import load_image, get_path



def game(display: pygame.Surface, clock: pygame.time.Clock) -> None:
    asteroid_image = load_image("assets", "images", "asteroid.png", size=[164, 164])
    background_image = load_image("assets", "images", "background.png", size=DISPLAY_SIZE)
    player_image = load_image("assets", "images", "player.png", size=[96, 96])
    shot_image = load_image("assets", "images", "shot.png", size=[64, 64])

    coords = DISPLAY_SIZE[0] /2, DISPLAY_SIZE[1] -50
    player = Player(player_image, coords, 6, 100)

    bullets = list()
    enemies = list()

    difficulty = 0
    score = 0
    font = pygame.Font(get_path("assets", "fonts", "pixel.ttf"), 24)
    pygame.time.set_timer(SPAWN_EVENT, 3000, 1)

    if pygame.mixer.get_init():
        shot_sound = pygame.Sound(get_path("assets", "sounds", "shot.wav"))
        death_sound = pygame.Sound(get_path("assets", "sounds", "death.wav"))
        explosion_sound = pygame.Sound(get_path("assets", "sounds", "explosion.wav"))

    while player.health > 0:
        difficulty += clock.get_time()

        # events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == SHOOT_EVENT:
                if pygame.mixer.get_init():
                    shot_sound.play()
                b = Bullet(shot_image, player.rect.midtop, 10)
                bullets.append(b)
            elif event.type == SPAWN_EVENT:
                millis = max(750, round(2000 - difficulty / 70)) 
                pygame.time.set_timer(SPAWN_EVENT, millis, 1)
                new_image = pygame.transform.rotozoom(asteroid_image, randint(0, 360), 1 + randint(-50, 50) / 100)

                coords = [randint(50, DISPLAY_SIZE[0] - 50), -new_image.height]
                speed = 5 + difficulty / 35_000
                damage = round(10 + difficulty / 7000)


                e = Enemy(new_image, coords, speed, damage)
                enemies.append(e)

        for e in enemies:
            if e.collide_entity(player):
                player.get_damage(e.damage)
                if pygame.mixer.get_init():
                    death_sound.play()
                e.kill()

        # update
        player.update()

        for b in bullets.copy():
            b.update()
            if not b.alive:
                bullets.remove(b)

        for e in enemies.copy():
            e.update()
            if not e.alive:
                enemies.remove(e)

        for b in bullets:
            for e in enemies:
                if b.collide_entity(e):
                    b.kill()
                    e.kill()
                    if pygame.mixer.get_init():
                        explosion_sound.play()
                    score += 1
                

        # render
        display.fill((0,0,0))
        display.blit(background_image, (0, 0))

        player.render(display)

        for b in bullets:
            b.render(display)

        for e in enemies:
            e.render(display)

        pygame.draw.rect(display, (100, 0, 0), [10, 10, HEALTH_BAR_WIDE, 30])
        width = int(player.health / PLAYER_HEALTH * HEALTH_BAR_WIDE)
        pygame.draw.rect(display, (235, 0, 0), [10, 10, width, 30])

        image_score = font.render(str(score), True, (50, 200, 50))
        rect_score = image_score.get_rect(topright = [DISPLAY_SIZE[0]-10, 10])
        display.blit(image_score, rect_score)

        pygame.display.update()
        clock.tick(MAX_FPS)

def main() -> None:
    pygame.init()

    display = pygame.display.set_mode(DISPLAY_SIZE, flags=pygame.RESIZABLE | pygame.SCALED ,vsync=True)
    pygame.display.set_caption('Shooter')
    clock = pygame.time.Clock()

    if pygame.mixer.get_init():
        pygame.mixer.music.load(get_path("assets", "sounds", "background-1.mp3"))
        pygame.mixer.music.ser_volume(0.2)
        pygame.mixer.music.play(-1)

    while True:
        game(display, clock)


if __name__ == '__main__':
    main()
