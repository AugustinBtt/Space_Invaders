import pygame
import random

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space invaders")
clock = pygame.time.Clock()
running = True
game_over = False
retry_button = pygame.Rect(0, 0, 0, 0)
exit_button = pygame.Rect(0, 0, 0, 0)
dt = 0
background_image = pygame.image.load('space.png')
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.font.init()
font = pygame.font.Font(None, 50)
lives = 5
score = 0

#player setup
player_pos = pygame.Vector2(600, 600)
spaceshipImg = pygame.image.load('space_fighter.png')
spaceship_width, spaceship_height = spaceshipImg.get_size()

pink_alien = pygame.image.load('pink_alien.png')
red_alien = pygame.image.load('red_alien.png')
orange_alien = pygame.image.load('orange_alien.png')
yellow_alien = pygame.image.load('yellow_alien.png')
aliens = (pink_alien, red_alien, orange_alien, yellow_alien)
created_aliens = []

CREATE_ALIEN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(CREATE_ALIEN_EVENT, 750)
alien_event_enabled = True

def create_alien():
    alien = random.choice(aliens)
    pos = pygame.Vector2(random.choice(range(0, 1190)), 0)
    screen.blit(alien, pos)
    created_aliens.append((alien, pos))

bullet_size = (5, 20)
bullet_color = (255,0,0)
bullets_shot = []
def shoot():
    bullet_pos = pygame.Vector2(player_pos.x + spaceship_width / 2 - bullet_size[0] / 2, player_pos.y + spaceship_height / 2 - bullet_size[1] / 2)
    bullet = pygame.Surface(bullet_size)
    bullet.fill(bullet_color)
    screen.blit(bullet, bullet_pos)
    bullets_shot.append((bullet, bullet_pos))

spaceship_hit_time = None
spaceship_visible = True
spaceship_blink_time = None

spacebar_released = True
started = False

while running:
    current_time = pygame.time.get_ticks()

    screen.blit(background_image, (0, 0))
    dt = clock.tick(144) / 1000

    if not started:
        start_button = pygame.draw.rect(screen, (255, 165, 0), (500, 600, 200, 50))
        start_surface = font.render('Start', True, (0, 0, 0))
        screen.blit(start_surface, (560, 610))

        welcome_image = pygame.image.load('welcome.png')
        screen.blit(welcome_image, (150, 150))

        alien_event_enabled = False

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and spacebar_released:
                shoot()
                spacebar_released = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                spacebar_released = True
        if event.type == CREATE_ALIEN_EVENT and alien_event_enabled:
            create_alien()

        if not started and event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            if start_button.collidepoint((x, y)):
                started = True
                alien_event_enabled = True

        if game_over and event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            if retry_button.collidepoint((x, y)):
                player_pos = pygame.Vector2(600, 600)
                game_over = False
                score = 0
                lives = 5
                created_aliens.clear()
                alien_event_enabled = True
            elif exit_button.collidepoint((x, y)):
                running = False

    if not game_over and started:
        for idx, (alien, pos) in enumerate(created_aliens):
            if pos.y > SCREEN_HEIGHT:  # If the alien has moved off the bottom of the screen
                del created_aliens[idx]
            else:
                pos.y += 0.75
                screen.blit(alien, pos)
                created_aliens[idx] = (alien, pos)

        for idx, (bullet, bullet_pos) in enumerate(bullets_shot):
            if bullet_pos.y < 0:
                del bullets_shot[idx]
            else:
                bullet_pos.y -= 3
                screen.blit(bullet, bullet_pos)
                bullets_shot[idx] = (bullet, bullet_pos)

        keys = pygame.key.get_pressed()
        spaceship_width, spaceship_height = spaceshipImg.get_size()
        if keys[pygame.K_a] and player_pos.x > 0:
            player_pos.x -= 500 * dt
        if keys[pygame.K_d] and player_pos.x < SCREEN_WIDTH - spaceship_width:
            player_pos.x += 500 * dt
        if keys[pygame.K_w] and player_pos.y > 0:
            player_pos.y -= 500 * dt
        if keys[pygame.K_s] and player_pos.y < SCREEN_HEIGHT - spaceship_height:
            player_pos.y += 500 * dt


        spaceship_rect = spaceshipImg.get_rect(topleft=player_pos)
        for idx in range(len(created_aliens) - 1, -1, -1):
            alien, pos = created_aliens[idx]
            alien_rect = alien.get_rect(topleft=pos)
            if spaceship_rect.colliderect(alien_rect):
                if spaceship_hit_time is None or current_time - spaceship_hit_time > 3000:
                    lives -= 1
                    del created_aliens[idx]
                    spaceship_hit_time = current_time
                    spaceship_visible = False
                    spaceship_blink_time = current_time
                    if lives == 0:
                        game_over = True
                        alien_event_enabled = False

        # spaceship blinking and invulnerability
        if spaceship_hit_time is not None:
            if current_time - spaceship_hit_time <= 3000:
                if current_time - spaceship_blink_time > 200:
                    spaceship_visible = not spaceship_visible
                    spaceship_blink_time = current_time
            else:
                spaceship_visible = True

        if spaceship_visible:
            screen.blit(spaceshipImg, player_pos)


        for bullet_idx in range(len(bullets_shot) -1, -1, -1):
            bullet, bullet_pos = bullets_shot[bullet_idx]
            bullet_rect = bullet.get_rect(topleft=bullet_pos)

            for alien_idx in range(len(created_aliens) - 1, -1, -1):
                alien, pos = created_aliens[alien_idx]  # get the alien's surface and position
                alien_rect = alien.get_rect(topleft=pos)
                if alien_rect.colliderect(bullet_rect):
                        score += 1
                        del created_aliens[alien_idx]
                        del bullets_shot[bullet_idx]
                        break

        text_color = (255, 0, 0) if lives == 1 else (255, 255, 255)
        life_surface = font.render('Lives: ' + str(lives), True, text_color)
        screen.blit(life_surface, (5, 5))

        score_surface = font.render('Score: ' + str(score), True, (255, 255, 255))
        screen.blit(score_surface, (1120, 5))

    elif game_over and started:
        msg_surface = font.render(f'Your score: {score}', True, (255, 255, 255))
        screen.blit(msg_surface, (SCREEN_WIDTH // 2 - msg_surface.get_width() // 2,
                                  SCREEN_HEIGHT // 2 - msg_surface.get_height() // 2 - 50))

        retry_button = pygame.draw.rect(screen, (0, 255, 0), (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50))
        retry_surface = font.render('Retry', True, (0, 0, 0))
        screen.blit(retry_surface, (SCREEN_WIDTH // 2 - retry_surface.get_width() // 2,
                                    SCREEN_HEIGHT // 2 + retry_surface.get_height() // 2 - 10))

        exit_button = pygame.draw.rect(screen, (255, 0, 0), (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 100, 200, 50))
        exit_surface = font.render('Exit', True, (0, 0, 0))
        screen.blit(exit_surface, (SCREEN_WIDTH // 2 - exit_surface.get_width() // 2,
                                   SCREEN_HEIGHT // 2 + exit_surface.get_height() // 2 + 90))


    pygame.display.flip()
pygame.quit()