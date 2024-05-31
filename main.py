import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
BALL_H = 66
BALL_W = 30
TARGET_ZONE_SIZE = 60
LEVELS = [
    {'background': 'assets/bck1.png', 'target': (60, SCREEN_HEIGHT - 60)},
    {'background': 'assets/bck2.png', 'target': (SCREEN_WIDTH - 60, SCREEN_HEIGHT - 60)},
    {'background': 'assets/bck3.png', 'target': (SCREEN_WIDTH - 60, 60)}
]
END_SCREEN_IMG = 'assets/end.png'
POINTER_IMG = 'assets/pointer.png'


# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space.. I mean Gravity Golf!")

# Load assets
ball_img = pygame.image.load('assets/ball.png')
ball_img = pygame.transform.scale(ball_img, (BALL_H, BALL_W))
pointer_img = pygame.image.load(POINTER_IMG)
pointer_img = pygame.transform.scale(pointer_img, (120, 5))

# Game variables
current_level = 0
ball_position = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
ball_velocity = [0, 0]
shooting = False
click_start_time = None
hold_time = 0

def load_background(level):
    bg = pygame.image.load(LEVELS[level]['background'])
    return pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

def rotate_image(image, angle):
    return pygame.transform.rotate(image, angle)

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
    #screen.fill(WHITE)
    background = load_background(current_level)
    screen.blit(background, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and not shooting:
            click_start_time = pygame.time.get_ticks()
        elif event.type == pygame.MOUSEBUTTONUP and not shooting and click_start_time:
            hold_time = (pygame.time.get_ticks() - click_start_time) / 400  # hold time in seconds
            click_start_time = None
            mouse_pos = pygame.mouse.get_pos()
            dx = mouse_pos[0] - ball_position[0]
            dy = mouse_pos[1] - ball_position[1]
            distance = math.hypot(dx, dy)
            power = min(15, hold_time * 5)  # maximum power capped at 15
            ball_velocity = [dx / distance * power, dy / distance * power]
            shooting = True

    if shooting:
        ball_position[0] += ball_velocity[0]
        ball_position[1] += ball_velocity[1]
        ball_velocity[0] *= 0.99  # simulate friction
        ball_velocity[1] *= 0.99  # simulate friction
        if math.hypot(ball_velocity[0], ball_velocity[1]) < 0.95:  # stop ball when velocity is low
            ball_velocity = [0, 0]
            shooting = False
        bounce_ball()
        if check_collision(ball_position, LEVELS[current_level]['target']):
            shooting = False
            current_level += 1
            ball_position = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
            if current_level >= len(LEVELS):
                game_over()

    # Rotate the ball based on its velocity
    if ball_velocity != [0, 0]:
        angle = math.degrees(math.atan2(ball_velocity[1], ball_velocity[0]))
        rotated_ball = rotate_image(ball_img, -angle)  # Rotate to face the direction of movement
        ball_rect = rotated_ball.get_rect(center=(ball_position[0], ball_position[1]))
        screen.blit(rotated_ball, ball_rect.topleft)
    else:
        screen.blit(ball_img, (ball_position[0] - BALL_H // 2, ball_position[1] - BALL_W // 2))

    # Draw the pointer
    mouse_pos = pygame.mouse.get_pos()
    pointer_angle = math.degrees(math.atan2(mouse_pos[1] - ball_position[1], mouse_pos[0] - ball_position[0]))
    rotated_pointer = rotate_image(pointer_img, -pointer_angle)
    pointer_rect = rotated_pointer.get_rect(center=mouse_pos)
    screen.blit(rotated_pointer, pointer_rect.topleft)

    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()
sys.exit()

