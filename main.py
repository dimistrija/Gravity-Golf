import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
BALL_H = 72
BALL_W = 33
TARGET_ZONE_SIZE = 60
OBJECT_SIZE = 45
#assets lvls etc.
LEVELS = [
    {'background': 'assets/intro.png', 'target': (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 25, 60, 50)},
    {'background': 'assets/bck1.png', 'target': (60, SCREEN_HEIGHT - 60), 'spawn': (1200, 30)},
    {'background': 'assets/bck2.png', 'target': (SCREEN_WIDTH - 60, SCREEN_HEIGHT - 60), 'spawn': (30, 30)},
    {'background': 'assets/bck3.png', 'target': (SCREEN_WIDTH - 60, 60), 'spawn': (40, 650)}
]
END_SCREEN_IMG = 'assets/end.png'
POINTER_IMG = 'assets/pointer.png'
OBJECT_IMGS = ['assets/cat1.png', 'assets/cat2.png', 'assets/cat3.png']
SAVED_IMG = 'assets/saved.png'
saved_img = pygame.image.load(SAVED_IMG)
saved_img = pygame.transform.scale(saved_img, (333, 53))




# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space.. I mean Gravity Golf!")

# Load assets
ball_img = pygame.image.load('assets/ball.png')
ball_img = pygame.transform.scale(ball_img, (BALL_H, BALL_W))
pointer_img = pygame.image.load(POINTER_IMG)
pointer_img = pygame.transform.scale(pointer_img, (120, 5))
object_imgs = [pygame.image.load(img) for img in OBJECT_IMGS]
object_imgs = [pygame.transform.scale(img, (OBJECT_SIZE, OBJECT_SIZE)) for img in object_imgs]

# Game variables
current_level = 0
ball_position = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
ball_velocity = [0, 0]
shooting = False
click_start_time = None
hold_time = 0
custom_objects = []
display_collected = False
display_start_time = 0



def load_background(level):
    bg = pygame.image.load(LEVELS[level]['background'])
    return pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

def rotate_image(image, angle):
    return pygame.transform.rotate(image, angle)

def check_collision(pos, target):
    if current_level == 0:
        target_x, target_y, target_width, target_height = target
        return (target_x - target_width // 2 <= pos[0] <= target_x + target_width // 2 and
                target_y - target_height <= pos[1] <= target_y)
    else:
        return (target[0] - TARGET_ZONE_SIZE / 2 <= pos[0] <= target[0] + TARGET_ZONE_SIZE / 2 and
                target[1] - TARGET_ZONE_SIZE / 2 <= pos[1] <= target[1] + TARGET_ZONE_SIZE / 2)


def check_object_collision(ball_pos, obj_pos):
    extra = 10  #extra size helping collision
    return (obj_pos[0] - OBJECT_SIZE / 2 - extra <= ball_pos[0] <= obj_pos[0] + OBJECT_SIZE / 2 + extra and
            obj_pos[1] - OBJECT_SIZE / 2 - extra <= ball_pos[1] <= obj_pos[1] + OBJECT_SIZE / 2 + extra)


def game_over():
    end_screen = pygame.image.load(END_SCREEN_IMG)
    end_screen = pygame.transform.scale(end_screen, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(end_screen, (0, 0))
    pygame.display.flip()
    pygame.time.wait(10000)
    pygame.quit()
    sys.exit()

def bounce_ball():
    if ball_position[0] <= 0 or ball_position[0] >= SCREEN_WIDTH:
        ball_velocity[0] = -ball_velocity[0]
    if ball_position[1] <= 0 or ball_position[1] >= SCREEN_HEIGHT:
        ball_velocity[1] = -ball_velocity[1]

def spawn_objects(num_objects):
    for _ in range(num_objects):
        x = random.randint(OBJECT_SIZE, SCREEN_WIDTH - OBJECT_SIZE)
        y = random.randint(OBJECT_SIZE, SCREEN_HEIGHT - OBJECT_SIZE)
        img = random.choice(object_imgs)
        custom_objects.append({'pos': [x, y], 'img': img})

# Main game loop
running = True
spawn_objects(3)

while running:
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
            else:
                ball_position = list(LEVELS[current_level]['spawn'])

    # Rotate the ball based on its velocity
    if ball_velocity != [0, 0]:
        angle = math.degrees(math.atan2(ball_velocity[1], ball_velocity[0]))
        rotated_ball = rotate_image(ball_img, -angle)  # Rotate to face the direction of movement
        ball_rect = rotated_ball.get_rect(center=(ball_position[0], ball_position[1]))
        screen.blit(rotated_ball, ball_rect.topleft)
    else:
        screen.blit(ball_img, (ball_position[0] - BALL_H // 2, ball_position[1] - BALL_W // 2))






    #kittiess
    if current_level == 0:
        pass
    else:
        for obj in custom_objects:
            screen.blit(obj['img'], obj['pos'])

    current_time = pygame.time.get_ticks()
    if display_collected and current_time - display_start_time < 3000 and current_level !=0:  # Display for 3 seconds
        screen.blit(saved_img, (
        SCREEN_WIDTH // 2 - saved_img.get_width() // 2, 60 - saved_img.get_height() // 2))
    else:
        display_collected = False

    for obj in custom_objects[:]:
        if check_object_collision(ball_position, obj['pos']):
            custom_objects.remove(obj)

            # Set the flag and start time to display the collected image
            display_collected = True
            display_start_time = pygame.time.get_ticks()

            if not custom_objects:  # If all objects are collected, spawn new ones
                spawn_objects(3)

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
