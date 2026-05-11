import pygame
import sys

pygame.init()

W, H = 800, 600
TILE = 40
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()

GRAVITY = 0.55
SPEED = 5
ACCEL = 0.5
FRICTION = 0.85
MAX_VX = SPEED
JUMP_MIN = 8
JUMP_EXTRA = 0.5
JUMP_MAX = 15
JUMP_FRAMES_MAX = 15

player_health = 3
max_health = 3

level = [
    "#######################",
    "#.....................#",
    "#....H................#",
    "#.....................#",
    "#..V..................#",
    "#.....................#",
    "#######################"
]

def load_img(path, size):
    return pygame.transform.scale(pygame.image.load(path).convert_alpha(), size)

def crop_image(image):
    rect = image.get_bounding_rect()
    return image.subsurface(rect) if rect.width and rect.height else image

def make_frames(paths, size):
    return [pygame.transform.scale(crop_image(pygame.image.load(p).convert_alpha()), size) for p in paths]

player_images = make_frames(['image/1.1.png', 'image/1.2.png'], (40, 40))
jump_images = make_frames(['jump/1.png', 'jump/2.png', 'jump/3.png', 'jump/4.png', 'jump/5.png'], (40, 40))
right_images = make_frames(['back/1.1.png', 'back/1.2.png'], (40, 40))
left_images = [pygame.transform.flip(img, True, False) for img in right_images]

block_image = load_img('image/block.png', (40, 40))
enemy_image = load_img('image/vrag.png', (40, 40))
health_image = load_img('image/health.png', (20, 20))
health_platform_image = load_img('image/health_platform.png', (40, 40))

def tiles_of(ch):
    for y, row in enumerate(level):
        for x, tile in enumerate(row):
            if tile == ch:
                yield x, y

player = pygame.Rect(100, 100, 40, 40)
vx = vy = 0.0
on_ground = False
jump_held = False
jump_frames = 0

camera_x = camera_y = 0
current_frame = 0
anim_timer = 0
frame_rate = 150

enemies = [pygame.Rect(x * TILE, y * TILE, TILE, TILE) for x, y in tiles_of('V')]
enemy_vx = {id(r): 2 for r in enemies}

running = True
while running:
    dt = clock.tick(60)
    anim_timer += dt

    if anim_timer >= frame_rate:
        current_frame = (current_frame + 1) % len(player_images)
        anim_timer = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and on_ground:
            vy = -JUMP_MIN
            jump_held = True
            jump_frames = 0
        elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
            jump_held = False

    keys = pygame.key.get_pressed()
    ax = 0
    if keys[pygame.K_LEFT]:
        ax = -ACCEL
    elif keys[pygame.K_RIGHT]:
        ax = ACCEL

    vx += ax
    vx *= FRICTION
    vx = max(-MAX_VX, min(vx, MAX_VX))

    if jump_held and keys[pygame.K_SPACE] and jump_frames < JUMP_FRAMES_MAX and vy < 0 and -vy < JUMP_MAX:
        vy -= JUMP_EXTRA
        jump_frames += 1

    vy += GRAVITY

    player.x += int(vx)
    for y, row in enumerate(level):
        for x, tile in enumerate(row):
            if tile == '#':
                r = pygame.Rect(x * TILE, y * TILE, TILE, TILE)
                if player.colliderect(r):
                    if vx > 0:
                        player.right = r.left
                    elif vx < 0:
                        player.left = r.right
                    vx = 0

    player.y += int(vy)
    on_ground = False
    for y, row in enumerate(level):
        for x, tile in enumerate(row):
            if tile == '#':
                r = pygame.Rect(x * TILE, y * TILE, TILE, TILE)
                if player.colliderect(r):
                    if vy > 0:
                        player.bottom = r.top
                        vy = 0
                        on_ground = True
                    elif vy < 0:
                        player.top = r.bottom
                        vy = 0

    for enemy in enemies:
        enemy.x += enemy_vx[id(enemy)]
        for y, row in enumerate(level):
            for x, tile in enumerate(row):
                if tile == '#':
                    r = pygame.Rect(x * TILE, y * TILE, TILE, TILE)
                    if enemy.colliderect(r):
                        enemy_vx[id(enemy)] *= -1
                        enemy.x += enemy_vx[id(enemy)] * 2
                        break

    for enemy in enemies:
        if player.colliderect(enemy):
            player_health -= 1
            if player.centerx < enemy.centerx:
                player.x -= 10
            else:
                player.x += 10
            if player_health <= 0:
                player_health = max_health
                player.topleft = (100, 100)

    for y, row in enumerate(level):
        for x, tile in enumerate(row):
            if tile == 'H':
                r = pygame.Rect(x * TILE, y * TILE, TILE, TILE)
                if player.colliderect(r) and player_health < max_health:
                    player_health += 1
                    level[y] = row[:x] + '.' + row[x+1:]

    camera_x = player.centerx - W // 2
    camera_y = player.centery - H // 2

    screen.fill((30, 30, 40))

    for y, row in enumerate(level):
        for x, tile in enumerate(row):
            px, py = x * TILE - camera_x, y * TILE - camera_y
            if tile == '#':
                screen.blit(block_image, (px, py))
            elif tile == 'H':
                screen.blit(health_platform_image, (px, py))

    for enemy in enemies:
        screen.blit(enemy_image, (enemy.x - camera_x, enemy.y - camera_y))

    for i in range(player_health):
        screen.blit(health_image, (W - 30 - i * 25, 10))

    pos = (player.x - camera_x, player.y - camera_y)
    if vy != 0:
        frame = min(len(jump_images) - 1, max(0, int(abs(vy) / JUMP_MAX * (len(jump_images) - 1))))
        screen.blit(jump_images[frame], pos)
    elif vx > 0.1:
        screen.blit(right_images[current_frame], pos)
    elif vx < -0.1:
        screen.blit(left_images[current_frame], pos)
    else:
        screen.blit(player_images[current_frame], pos)

    pygame.display.flip()

pygame.quit()
sys.exit()