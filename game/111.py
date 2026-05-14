import pygame
import sys
import config
import os

pygame.init()

screen = pygame.display.set_mode((config.W, config.H))
clock = pygame.time.Clock()

TILE = config.TILE

base_path = os.path.dirname(os.path.abspath(__file__))

player_health = config.PLAYER_HEALTH
max_health = config.MAX_HEALTH

font = pygame.font.SysFont(None, 48)

# TODO: Заменить текстовый массив уровня на загрузку из файла (например, .txt или .json)
# Символы:
#   # - блок
#   H - платформа/точка восстановления здоровья
#   V - враг
#   . - пустота
level = [
    "####################",
    "#..................#",
    "#....H.............#",
    "#..................#",
    "#..V...............#",
    "#..................#",
    "############.......#",
    "#..................#",
    "#........H.........#",
    "#..................#",
    "#..............V...#",
    "#..................#",
    "###############....#",
    "#..................#",
    "#....H.............#",
    "#..................#",
    "#..V...............#",
    "#..................#",
    "####################"
]

def load_img(path, size):
    """Загрузка и масштабирование изображения."""
    try:
        return pygame.transform.scale(pygame.image.load(path).convert_alpha(), size)
    except pygame.error as e:
        print(f"Ошибка загрузки изображения {path}: {e}")
        sys.exit(1)

def crop_image(image):
    """Обрезка прозрачных краёв изображения."""
    # TODO: При необходимости кешировать обрезанные спрайты, если будет много ресурсов
    rect = image.get_bounding_rect()
    return image.subsurface(rect) if rect.width and rect.height else image

def make_frames(paths, size):
    """Загрузка набора кадров анимации из списка путей."""
    # TODO: Добавить поддержку анимаций с разной длительностью кадров (timings)
    return [
        pygame.transform.scale(
            crop_image(pygame.image.load(p).convert_alpha()),
            size
        )
        for p in paths
    ]

# TODO: Вынести все пути к ресурсам в отдельный файл/конфиг
player_images = make_frames([os.path.join(base_path, '../image/1.1.png'), os.path.join(base_path, '../image/1.2.png')], (40, 40))
jump_images = make_frames([os.path.join(base_path, '../jump/1.png'), os.path.join(base_path, '../jump/2.png'), os.path.join(base_path, '../jump/3.png'), os.path.join(base_path, '../jump/4.png'), os.path.join(base_path, '../jump/5.png')], (40, 40))
right_images = make_frames([os.path.join(base_path, '../back/1.1.png'), os.path.join(base_path, '../back/1.2.png')], (40, 40))
left_images = [pygame.transform.flip(img, True, False) for img in right_images]

block_image = load_img(os.path.join(base_path, '../image/block.png'), (40, 40))
enemy_image = load_img(os.path.join(base_path, '../image/vrag.png'), (40, 40))
health_image = load_img(os.path.join(base_path, '../image/health.png'), (20, 20))
health_platform_image = load_img(os.path.join(base_path, '../image/health_platform.png'), (40, 40))

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE, TILE)
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.jump_held = False
        self.jump_frames = 0
        self.health = config.PLAYER_HEALTH

    def update(self, keys, dt):
        # ДВИЖЕНИЕ ПО X
        ax = 0
        if keys[pygame.K_LEFT]:
            ax = -config.ACCEL
        elif keys[pygame.K_RIGHT]:
            ax = config.ACCEL

        self.vx += ax
        self.vx *= config.FRICTION
        self.vx = max(-config.MAX_VX, min(self.vx, config.MAX_VX))

        # Прыжок
        if self.jump_held and keys[pygame.K_SPACE] and self.jump_frames < config.JUMP_FRAMES_MAX and self.vy < 0 and -self.vy < config.JUMP_MAX:
            self.vy -= config.JUMP_EXTRA
            self.jump_frames += 1

        # Гравитация
        self.vy += config.GRAVITY

        # Применяем движение
        self.rect.x += int(self.vx)
        self.collide_x(level)

        self.rect.y += int(self.vy)
        self.on_ground = False
        self.collide_y(level)

    def collide_x(self, level):
        for y, row in enumerate(level):
            for x, tile in enumerate(row):
                if tile == '#':
                    r = pygame.Rect(x * TILE, y * TILE, TILE, TILE)
                    if self.rect.colliderect(r):
                        if self.vx > 0:
                            self.rect.right = r.left
                        elif self.vx < 0:
                            self.rect.left = r.right
                        self.vx = 0

    def collide_y(self, level):
        for y, row in enumerate(level):
            for x, tile in enumerate(row):
                if tile == '#':
                    r = pygame.Rect(x * TILE, y * TILE, TILE, TILE)
                    if self.rect.colliderect(r):
                        if self.vy > 0:
                            self.rect.bottom = r.top
                            self.vy = 0
                            self.on_ground = True
                        elif self.vy < 0:
                            self.rect.top = r.bottom
                            self.vy = 0

    def draw(self, screen, camera_x, camera_y, current_frame):
        pos = (self.rect.x - camera_x, self.rect.y - camera_y)
        if self.vy != 0:
            frame = min(len(jump_images) - 1, max(0, int(abs(self.vy) / config.JUMP_MAX * (len(jump_images) - 1))))
            screen.blit(jump_images[frame], pos)
        elif self.vx > 0.1:
            screen.blit(right_images[current_frame], pos)
        elif self.vx < -0.1:
            screen.blit(left_images[current_frame], pos)
        else:
            screen.blit(player_images[current_frame], pos)

def tiles_of(ch):
    """Генератор координат всех тайлов с указанным символом."""
    # TODO: При большом уровне генерировать список один раз и хранить, а не обходить level каждый кадр
    for y, row in enumerate(level):
        for x, tile in enumerate(row):
            if tile == ch:
                yield x, y

# TODO: Вынести игрока и врагов в отдельные классы (Player, Enemy) с методами update/draw
player = Player(100, 100)

camera_x = camera_y = 0
current_frame = 0
anim_timer = 0
frame_rate = config.FRAME_RATE  # TODO: Поиграться со значением для более плавной анимации

# TODO: Вместо id(rect) использовать класс Enemy с собственным vx
enemies = [pygame.Rect(x * TILE, y * TILE, TILE, TILE) for x, y in tiles_of('V')]
enemy_vx = {id(r): 2 for r in enemies}  # скорость каждого врага

state = 'menu'  # 'menu', 'play', 'pause'

running = True

def draw_menu():
    screen.fill((30, 30, 40))
    title = font.render("Игра", True, (255, 255, 255))
    screen.blit(title, (config.W // 2 - title.get_width() // 2, 100))
    play_text = font.render("Играть", True, (255, 255, 255))
    play_rect = play_text.get_rect(center=(config.W // 2, 200))
    screen.blit(play_text, play_rect)
    exit_text = font.render("Выход", True, (255, 255, 255))
    exit_rect = exit_text.get_rect(center=(config.W // 2, 250))
    screen.blit(exit_text, exit_rect)
    return play_rect, exit_rect

def draw_pause():
    screen.fill((30, 30, 40))
    pause_text = font.render("Пауза", True, (255, 255, 255))
    screen.blit(pause_text, (config.W // 2 - pause_text.get_width() // 2, 100))
    resume_text = font.render("Продолжить", True, (255, 255, 255))
    resume_rect = resume_text.get_rect(center=(config.W // 2, 200))
    screen.blit(resume_text, resume_rect)
    menu_text = font.render("Меню", True, (255, 255, 255))
    menu_rect = menu_text.get_rect(center=(config.W // 2, 250))
    screen.blit(menu_text, menu_rect)
    return resume_rect, menu_rect

def update_game(dt):
    global current_frame, anim_timer
    anim_timer += dt
    if anim_timer >= frame_rate:
        current_frame = (current_frame + 1) % len(player_images)
        anim_timer = 0

    player.update(keys, dt)

    # ДВИЖЕНИЕ ВРАГОВ
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

    # СТОЛКНОВЕНИЕ ИГРОКА С ВРАГАМИ
    for enemy in enemies:
        if player.rect.colliderect(enemy):
            player.health -= 1
            if player.rect.centerx < enemy.centerx:
                player.rect.x -= 10
            else:
                player.rect.x += 10
            if player.health <= 0:
                player.health = config.MAX_HEALTH
                player.rect.topleft = (100, 100)

    # ПЛАТФОРМЫ ЗДОРОВЬЯ
    for y, row in enumerate(level):
        for x, tile in enumerate(row):
            if tile == 'H':
                r = pygame.Rect(x * TILE, y * TILE, TILE, TILE)
                if player.rect.colliderect(r) and player.health < config.MAX_HEALTH:
                    player.health += 1
                    level[y] = row[:x] + '.' + row[x+1:]

    # КАМЕРА
    global camera_x, camera_y
    camera_x = player.rect.centerx - config.W // 2
    camera_y = player.rect.centery - config.H // 2
    level_width = len(level[0]) * TILE
    level_height = len(level) * TILE
    camera_x = max(0, min(camera_x, level_width - config.W))
    camera_y = max(0, min(camera_y, level_height - config.H))

def draw_game():
    screen.fill((30, 30, 40))

    # Рисуем уровень
    for y, row in enumerate(level):
        for x, tile in enumerate(row):
            px, py = x * TILE - camera_x, y * TILE - camera_y
            if tile == '#':
                screen.blit(block_image, (px, py))
            elif tile == 'H':
                screen.blit(health_platform_image, (px, py))

    # Рисуем врагов
    for enemy in enemies:
        screen.blit(enemy_image, (enemy.x - camera_x, enemy.y - camera_y))

    # Рисуем здоровье игрока
    for i in range(player.health):
        screen.blit(health_image, (config.W - 30 - i * 25, 10))

    # Рисуем игрока
    player.draw(screen, camera_x, camera_y, current_frame)
while running:
    dt = clock.tick(60)
    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif state == 'menu':
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                play_rect, exit_rect = draw_menu()
                if play_rect.collidepoint(mouse_pos):
                    state = 'play'
                elif exit_rect.collidepoint(mouse_pos):
                    running = False
        elif state == 'play':
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and player.on_ground:
                player.vy = -config.JUMP_MIN
                player.jump_held = True
                player.jump_frames = 0
            elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                player.jump_held = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                state = 'pause'
        elif state == 'pause':
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                resume_rect, menu_rect = draw_pause()
                if resume_rect.collidepoint(mouse_pos):
                    state = 'play'
                elif menu_rect.collidepoint(mouse_pos):
                    state = 'menu'
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                state = 'play'

    if state == 'play':
        update_game(dt)
        draw_game()
    elif state == 'menu':
        draw_menu()
    elif state == 'pause':
        draw_pause()

    pygame.display.flip()

pygame.quit()
sys.exit()