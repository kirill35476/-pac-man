import math
import pygame
import random
import time

pygame.init()

# Загрузка изображений
pacman_images = {
    'up': pygame.image.load('resources/pacman_up.png'),
    'down': pygame.image.load('resources/pacman_down.png'),
    'left': pygame.image.load('resources/pacman_left.png'),
    'right': pygame.image.load('resources/pacman_right.png'),
    'up_left': pygame.image.load('resources/pacman_up_left.png'),
    'up_right': pygame.image.load('resources/pacman_up_right.png'),
    'down_left': pygame.image.load('resources/pacman_down_left.png'),
    'down_right': pygame.image.load('resources/pacman_down_right.png'),
}

# Размеры Pac-Man'а
PACMAN_SIZE = 30  # Размер изображения (30x30 пикселей)


# Создаем точки для сбора
class Dot:
    def __init__(self, pos):
        self.pos = pos
        self.collected = False
        self.radius = 5

    def draw(self, screen):
        if not self.collected:
            pygame.draw.circle(screen, (255, 255, 0), self.pos, self.radius)


def create_dots(count, size):
    dots = []
    for _ in range(count):
        x = random.randint(50, size[0] - 50)
        y = random.randint(50, size[1] - 50)
        dots.append(Dot((x, y)))
    return dots


# Функции для определения направления и движения
def get_direction(pos1, pos2):
    dx = pos2[0] - pos1[0]
    dy = pos2[1] - pos1[1]

    direction = 'right'

    if dy < 0:
        if dx < 0:
            direction = 'up_left'
        elif dx > 0:
            direction = 'up_right'
        else:
            direction = 'up'
    elif dy > 0:
        if dx < 0:
            direction = 'down_left'
        elif dx > 0:
            direction = 'down_right'
        else:
            direction = 'down'
    else:
        if dx < 0:
            direction = 'left'
        elif dx > 0:
            direction = 'right'

    return direction


def distance(pos1, pos2):
    return math.sqrt((pos2[0] - pos1[0]) ** 2 + (pos2[1] - pos1[1]) ** 2)


def move_towards(pos1, pos2, min_speed=1, max_speed=3):
    x1, y1 = pos1
    x2, y2 = pos2
    dx = x2 - x1
    dy = y2 - y1

    dist = distance(pos1, pos2)

    if dist < min_speed:
        return pos2

    if dist == 0:
        return pos1

    speed = max(min_speed, min(dist / 5, max_speed))

    dx /= dist
    dy /= dist

    x1 += dx * speed
    y1 += dy * speed

    return (x1, y1)


# Проверка, находится ли точка внутри Pac-Man'а
def is_dot_inside_pacman(pacman_center, dot_pos):
    # Считаем, что Pac-Man - это круг радиусом PACMAN_SIZE//2
    pacman_radius = PACMAN_SIZE // 2
    dot_distance = distance(pacman_center, dot_pos)
    return dot_distance <= pacman_radius


# Инициализация игры
size = (800, 600)
screen = pygame.display.set_mode(size)
pygame.display.set_caption("Pac-Man Турнир: Собираем всем телом!")
BACKGROUND = (0, 0, 0)
FPS = 60
clock = pygame.time.Clock()

# Позиции игроков
player_pos = [400, 300]  # Управляется мышкой
ai_pos = [200, 200]  # Управляется ИИ

# Счет
player_score = 0
ai_score = 0

# Создаем начальные точки
dots = create_dots(50, size)

# Таймер (3 минуты = 180 секунд)
game_time = 180  # 3 минуты
start_time = time.time()

# Основной игровой цикл
running = True
while running:
    current_time = time.time()
    elapsed = current_time - start_time
    remaining_time = max(0, game_time - elapsed)

    # Проверка окончания времени
    if remaining_time <= 0:
        running = False
        if player_score > ai_score:
            result = "Игрок победил!"
        elif ai_score > player_score:
            result = "ИИ победил!"
        else:
            result = "Ничья!"

        # Вывод результата
        screen.fill(BACKGROUND)
        font = pygame.font.SysFont(None, 72)
        text = font.render(result, True, (255, 255, 255))
        screen.blit(text, (size[0] // 2 - text.get_width() // 2, size[1] // 2 - text.get_height() // 2))
        pygame.display.flip()
        pygame.time.wait(3000)  # Ждем 3 секунды перед закрытием
        break

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Управление игроком (мышка)
    mouse_pos = pygame.mouse.get_pos()
    player_direction = get_direction(player_pos, mouse_pos)
    player_pos = list(move_towards(player_pos, mouse_pos))

    # Проверяем, остались ли точки
    if all(dot.collected for dot in dots):
        dots = create_dots(50, size)  # Создаем новые точки

    # ИИ выбирает ближайшую точку
    if dots:
        # Находим ближайшую не собранную точку
        closest_dot = None
        min_dist = float('inf')
        for dot in dots:
            if not dot.collected:
                dist = distance(ai_pos, dot.pos)
                if dist < min_dist:
                    min_dist = dist
                    closest_dot = dot

        if closest_dot:
            ai_direction = get_direction(ai_pos, closest_dot.pos)
            ai_pos = list(move_towards(ai_pos, closest_dot.pos))

    # Проверка сбора точек (теперь всем телом!)
    for dot in dots:
        if not dot.collected:
            # Для игрока
            if is_dot_inside_pacman(player_pos, dot.pos):
                dot.collected = True
                player_score += 1

            # Для ИИ
            if is_dot_inside_pacman(ai_pos, dot.pos):
                dot.collected = True
                ai_score += 1

    # Отрисовка
    screen.fill(BACKGROUND)

    # Рисуем точки
    for dot in dots:
        dot.draw(screen)

    # Рисуем игроков
    screen.blit(pacman_images[player_direction], (player_pos[0] - PACMAN_SIZE // 2, player_pos[1] - PACMAN_SIZE // 2))
    screen.blit(pacman_images[ai_direction], (ai_pos[0] - PACMAN_SIZE // 2, ai_pos[1] - PACMAN_SIZE // 2))

    # Отображаем счет и время
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Игрок: {player_score}   ИИ: {ai_score}", True, (255, 255, 255))
    time_text = font.render(f"Время: {int(remaining_time // 60)}:{int(remaining_time % 60):02d}", True, (255, 255, 255))

    screen.blit(score_text, (20, 20))
    screen.blit(time_text, (size[0] - time_text.get_width() - 20, 20))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()