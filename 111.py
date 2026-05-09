import pygame
import sys

def crop_image(image):
    """Кадрирует изображение, удаляя прозрачные области."""
    rect = image.get_bounding_rect()
    if rect.width > 0 and rect.height > 0:
        return image.subsurface(rect)
    return image

pygame.init()

W, H = 800, 600
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()

# Загружаем и кадрируем изображения для стояния/ходьбы
player_images = [
    crop_image(pygame.image.load('image/1.1.png').convert_alpha()),
    crop_image(pygame.image.load('image/1.2.png').convert_alpha())
]
player_images = [pygame.transform.scale(img, (40, 40)) for img in player_images]

# Загружаем и кадрируем изображения для прыжка
jump_images = [
    crop_image(pygame.image.load('jump/1.png').convert_alpha()),
    crop_image(pygame.image.load('jump/2.png').convert_alpha()),
    crop_image(pygame.image.load('jump/3.png').convert_alpha()),
    crop_image(pygame.image.load('jump/4.png').convert_alpha()),
    crop_image(pygame.image.load('jump/5.png').convert_alpha())
]
jump_images = [pygame.transform.scale(img, (40, 40)) for img in jump_images]

# Кубик (позиция для изображения)
player = pygame.Rect(100, 100, 40, 40)
vx = 0
vy = 0

# Платформа
platform = pygame.Rect(200, 450, 400, 20)

GRAVITY = 0.55
SPEED = 5
JUMP_MIN = 8   # Минимальная сила прыжка
JUMP_EXTRA = 0.5  # Дополнительная сила при зажатии
JUMP_MAX = 15  # Максимальная сила прыжка

on_ground = False
jump_held = False  # Флаг, зажат ли прыжок

# Переменные для анимации стояния/ходьбы
current_frame = 0
animation_timer = 0
frame_rate = 500

while True:
    dt = clock.tick(60)
    animation_timer += dt
    
    # Переключаем кадр для стояния/ходьбы
    if animation_timer >= frame_rate:
        current_frame = (current_frame + 1) % len(player_images)
        animation_timer = 0
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and on_ground:
                vy = -JUMP_MIN  # Начинаем прыжок сразу
                jump_held = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                jump_held = False  # Прекращаем увеличение силы

    keys = pygame.key.get_pressed()

    vx = 0
    if keys[pygame.K_LEFT]:
        vx = -SPEED
    if keys[pygame.K_RIGHT]:
        vx = SPEED
    
    # Увеличиваем силу прыжка, пока зажат пробел и не достигнут максимум
    if jump_held and keys[pygame.K_SPACE] and vy < 0 and -vy < JUMP_MAX:
        vy -= JUMP_EXTRA  # Делаем прыжок выше

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
    
    # Выбор анимации
    if vy != 0:  # В прыжке или падении
        max_vy = JUMP_MAX
        if vy < 0:  # Подъём
            frame = int((max_vy + vy) / max_vy * (len(jump_images) - 1))
        else:  # Падение (обратная анимация)
            frame = len(jump_images) - 1 - int(vy / max_vy * (len(jump_images) - 1))
        frame = max(0, min(frame, len(jump_images) - 1))
        screen.blit(jump_images[frame], player)
    else:  # На земле
        screen.blit(player_images[current_frame], player)
    
    pygame.display.flip()