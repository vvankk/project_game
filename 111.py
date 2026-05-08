import pygame
import sys

pygame.init()

W, H = 800, 600
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()

# Кубик
player = pygame.Rect(100, 100, 40, 40)
vx = 0
vy = 0

# Платформа
platform = pygame.Rect(200, 450, 400, 20)

GRAVITY = 0.6
SPEED = 5
JUMP = -12

on_ground = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()

    vx = 0
    if keys[pygame.K_LEFT]:
        vx = -SPEED
    if keys[pygame.K_RIGHT]:
        vx = SPEED
    if keys[pygame.K_SPACE] and on_ground:
        vy = JUMP

    # Гравитация
    vy += GRAVITY

    # Движение по X
    player.x += vx

    # Движение по Y
    player.y += vy
    on_ground = False

    # Коллизия с платформой
    if player.colliderect(platform):
        if vy > 0:
            player.bottom = platform.top
            vy = 0
            on_ground = True
        elif vy < 0:
            player.top = platform.bottom
            vy = 0

    # Границы экрана
    if player.left < 0:
        player.left = 0
    if player.right > W:
        player.right = W
    if player.bottom > H:
        player.bottom = H
        vy = 0
        on_ground = True

    # Рисование
    screen.fill((30, 30, 40))
    pygame.draw.rect(screen, (0, 200, 255), platform)
    pygame.draw.rect(screen, (255, 200, 0), player)

    pygame.display.flip()
    clock.tick(60)