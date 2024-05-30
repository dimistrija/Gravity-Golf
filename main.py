import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
BALL_SIZE = 30
TARGET_ZONE_SIZE = 60
LEVELS = [
    {'background': 'assets/bck1.png', 'target': (60, SCREEN_HEIGHT - 60)},
    {'background': 'assets/bck2.png', 'target': (SCREEN_WIDTH - 60, SCREEN_HEIGHT - 60)},
    {'background': 'assets/bck3.png', 'target': (SCREEN_WIDTH - 60, 60)}
]
END_SCREEN_IMG = 'assets/end.png'

# Colors
WHITE = (255, 255, 255)
RED = (94, 25, 22)

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space.. I mean Gravity Golf!")

# Load assets
ball_img = pygame.image.load('assets/ball.png')
ball_img = pygame.transform.scale(ball_img, (BALL_SIZE, BALL_SIZE))

# Game variables
current_level = 0
ball_position = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
ball_velocity = [0, 0]
shooting = False


def load_background(level):
    bg = pygame.image.load(LEVELS[level]['background'])
    return pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))


def draw_pointer(start_pos, end_pos):
    pygame.draw.line(screen, RED, start_pos, end_pos, 3)


def check_collision(pos, target):
    return (target[0] - TARGET_ZONE_SIZE / 2 <= pos[0] <= target[0] + TARGET_ZONE_SIZE / 2 and
            target[1] - TARGET_ZONE_SIZE / 2 <= pos[1] <= target[1] + TARGET_ZONE_SIZE / 2)


def game_over():
    end_screen = pygame.image.load(END_SCREEN_IMG)
    end_screen = pygame.transform.scale(end_screen, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(end_screen, (0, 0))
    pygame.display.flip()
    pygame.time.wait(15000)
    pygame.quit()
    sys.exit()


def bounce_ball():
    if ball_position[0] <= 0 or ball_position[0] >= SCREEN_WIDTH:
        ball_velocity[0] = -ball_velocity[0]
    if ball_position[1] <= 0 or ball_position[1] >= SCREEN_HEIGHT:
        ball_velocity[1] = -ball_velocity[1]


# Main game loop
running = True
while running:
    screen.fill(WHITE)
    background = load_background(current_level)
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and not shooting:
            mouse_pos = pygame.mouse.get_pos()
            dx = mouse_pos[0] - ball_position[0]
            dy = mouse_pos[1] - ball_position[1]
            distance = math.hypot(dx, dy)
            ball_velocity = [dx / distance, dy / distance]
            shooting = True

    if shooting:
        ball_position[0] += ball_velocity[0] * 10
        ball_position[1] += ball_velocity[1] * 10
        bounce_ball()
        if check_collision(ball_position, LEVELS[current_level]['target']):
            shooting = False
            current_level += 1
            ball_position = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
            if current_level >= len(LEVELS):
                game_over()

    mouse_pos = pygame.mouse.get_pos()
    draw_pointer(ball_position, mouse_pos)

    screen.blit(ball_img, (ball_position[0] - BALL_SIZE // 2, ball_position[1] - BALL_SIZE // 2))

    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
sys.exit()
