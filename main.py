# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import pygame
import sys
import math
import random


pygame.init()
pygame.font.init()
#soundtrack
pygame.mixer.init()
pygame.mixer.music.load('assets/stars-of-the-lidmp3.mp3') # got original .flac but it's 40MBs, mp3 was 10 :)
pygame.mixer.music.play(-1) #(-1)==music loops
pygame.mixer.music.set_volume(0.03)
 
#often used constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
OBJECT_SIZE = 45
#variables
current_level = 0
ball_position = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2]
ball_velocity = [0, 0]
shooting = False
click_start_time = None
hold_time = 0
max_power, hold_power = [16, 7] # hard to "balance" between fair/fun and overpowered /w grav zones
custom_objects = []
display_collected = False
display_start_time = 0
blackhole_displayed = False
blackhole_start_time = None
zone_timer = None
points = 0
# Levels dictionary: magic numbers are pixels, and grav zones values
# including spawn locations, gravity zones (x,y,radius,pull), and next lvl 'target' zones, bhole (x,y,rad)
LEVELS = [
    {'background': 'assets/intro.png', 'target': (SCREEN_WIDTH // 2, SCREEN_HEIGHT, 200, 100),
     'gravity_zones': [(60, 60, 350, 2)], 'black_zones': (10, 10, 10)},
    {'background': 'assets/bck1.png', 'target': (60, SCREEN_HEIGHT - 60), 'spawn': (1200, 30),
     'gravity_zones': [(100, 120, 150, 0.4), (620, 700, 170, 0.45), (640, 360, 290, 0.8), (1130, 650, 200, 0.4)],
     'black_zones': (640, 360, 70)},
    {'background': 'assets/bck2.png', 'target': (SCREEN_WIDTH - 60, SCREEN_HEIGHT - 60), 'spawn': (30, 30),
     'gravity_zones': [(240,80, 150, 0.4), (600, 460, 290, 0.85), (140, 600, 170, 0.45), (960, 250, 330, 0.55)],
     'black_zones': (600, 460, 70)},
    {'background': 'assets/bck3.png', 'target': (SCREEN_WIDTH - 60, 60), 'spawn': (40, 650),
     'gravity_zones': [(260, 480, 170, 0.4), (700, 660, 290, 0.85), (320, 60, 150, 0.4), (900, 240, 150, 0.4)],
     'black_zones': (700, 660, 70)}
]


#Assets stuff
FONT = 'assets/font.ttf'
the_font = pygame.font.Font(FONT, size=50)
END_SCREEN_IMG = 'assets/end.png'
POINTER_IMG = 'assets/pointer.png'
OBJECT_IMGS = ['assets/cat1.png', 'assets/cat3.png', 'assets/cat2.png']
SAVED_IMG = 'assets/saved.png'
BLACKHOLE_IMG = 'assets/blackhole.png'
blackhole_img = pygame.image.load(BLACKHOLE_IMG)
blackhole_img = pygame.transform.scale(blackhole_img, (SCREEN_WIDTH, SCREEN_HEIGHT))  # Adjust size as needed
saved_img = pygame.image.load(SAVED_IMG)
saved_img = pygame.transform.scale(saved_img, (333, 53))
ball_img = pygame.image.load('assets/ball.png')
ball_img = pygame.transform.scale(ball_img, (79, 36))
pointer_img = pygame.image.load(POINTER_IMG)
pointer_img = pygame.transform.scale(pointer_img, (170, 5))
object_imgs = [pygame.image.load(img) for img in OBJECT_IMGS]
object_imgs = [pygame.transform.scale(img, (OBJECT_SIZE, OBJECT_SIZE)) for img in object_imgs]


screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space.. I mean Gravity Golf!")

#the holy grail part 
def lose_check(ball_pos, zone):
    """Function to check players position in a circle around a x,y coordinate."""    
    px, py = ball_pos
    zx, zy, r = zone
    return (px - zx) ** 2 + (py - zy) ** 2 <= r ** 2

def apply_gravity(ball_pos, ball_vel, gravity_zones, damping_factor=0.8):
    """
        Applies velocity changes from current 'gravity zone' to the ball and
        updates its velocity. Force is proportional to the center-to-ball distance and inverse
        for zone's radius.
     """
    for (gx, gy, radius, strength) in gravity_zones:
        dx = gx - ball_pos[0]
        dy = gy - ball_pos[1]
        distance = math.hypot(dx, dy)
        if distance < radius:
            # Normalize the direction
            if distance != 0:
                dx /= distance
                dy /= distance
            force = (1 - distance / radius) * strength
            ball_vel[0] += dx * force * damping_factor #damping factor helps movement feel more fluid
            ball_vel[1] += dy * force * damping_factor
    return ball_vel

def load_background(level):
    """
    Function to load levels/backgrounds.
    """
    bg = pygame.image.load(LEVELS[level]['background'])
    return pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

def rotate_image(image, angle):
    """
    Method to rotate an image using pygame's built-in function.
    """
    return pygame.transform.rotate(image, angle)

# sloppy but works
def check_collision(pos, target):
    """
    Function to check collision with target area to switch levels, with an adjustment for level 0.
    """
    if current_level == 0:
        target_x, target_y, target_width, target_height = target
        return (target_x - target_width // 2 <= pos[0] <= target_x + target_width // 2 and
                target_y - target_height <= pos[1] <= target_y)
    else:
        return (target[0] - 60 / 2 <= pos[0] <= target[0] + 60 / 2 and
                target[1] - 60 / 2 <= pos[1] <= target[1] + 60 / 2)


def check_object_collision(ball_pos, obj_pos):
    """ Function checking object collision between the player and the spawned objects. Including extra 
    "size" for better collision detection.
    """
    extra = 13 
    return (obj_pos[0] - OBJECT_SIZE / 2 - extra <= ball_pos[0] <= obj_pos[0] + OBJECT_SIZE / 2 + extra and
            obj_pos[1] - OBJECT_SIZE / 2 - extra <= ball_pos[1] <= obj_pos[1] + OBJECT_SIZE / 2 + extra)


def game_over():
    """ Function for game over screen, including total points scored.
    """
    end_screen = pygame.image.load(END_SCREEN_IMG)
    end_screen = pygame.transform.scale(end_screen, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(end_screen, (0, 0))
    screen.blit(text_2, (380, SCREEN_HEIGHT // 2 - 50))
    pygame.display.flip()
    pygame.time.wait(11000)
    pygame.quit()
    sys.exit()


DAMPING_FACTOR = 0.6 #it works better.
def bounce_ball():
    """ Function for wall bouncing and collision.
    """
    if ball_position[0] <= 0:
        ball_position[0] = 0
        ball_velocity[0] = -ball_velocity[0] * DAMPING_FACTOR
    elif ball_position[0] >= SCREEN_WIDTH:
        ball_position[0] = SCREEN_WIDTH
        ball_velocity[0] = -ball_velocity[0] * DAMPING_FACTOR

    if ball_position[1] <= 0:
        ball_position[1] = 0
        ball_velocity[1] = -ball_velocity[1] * DAMPING_FACTOR
    elif ball_position[1] >= SCREEN_HEIGHT:
        ball_position[1] = SCREEN_HEIGHT
        ball_velocity[1] = -ball_velocity[1] * DAMPING_FACTOR


def spawn_objects(num_objects):
    """ Function to spawn in collectible objects randomly inside the play area.
    """
    for _ in range(num_objects):
        x = random.randint(OBJECT_SIZE, SCREEN_WIDTH - OBJECT_SIZE)
        y = random.randint(OBJECT_SIZE, SCREEN_HEIGHT - OBJECT_SIZE)
        img = random.choice(object_imgs)
        custom_objects.append({'pos': [x, y], 'img': img})

## Main game loop
running = True
spawn_objects(4)
while running:
    background = load_background(current_level)
    screen.blit(background, (0, 0))
#main gameplay/control mechanic for player (click+hold)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and not shooting:
            click_start_time = pygame.time.get_ticks()
        elif event.type == pygame.MOUSEBUTTONUP and not shooting and click_start_time:
            hold_time = (pygame.time.get_ticks() - click_start_time) / 400
            click_start_time = None
            mouse_pos = pygame.mouse.get_pos()
            dx = mouse_pos[0] - ball_position[0]
            dy = mouse_pos[1] - ball_position[1]
            distance = math.hypot(dx, dy)
            power = min(max_power, hold_time * hold_power)
            ball_velocity = [dx / distance * power, dy / distance * power] #easy way to shoot in mouse direction
            shooting = True
    # this part combines gravity+lvl swithc
    if shooting:
        ball_velocity = apply_gravity(ball_position, ball_velocity, LEVELS[current_level].get('gravity_zones', []))
        ball_position[0] += ball_velocity[0]
        ball_position[1] += ball_velocity[1]
        ball_velocity[0] *= 0.99  
        ball_velocity[1] *= 0.99  # ^simulate friction^
        if math.hypot(ball_velocity[0], ball_velocity[1]) < 0.99:  # forces ball to stop earlier, can continue playing faster
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

    # rotating the ball with math :)
    if ball_velocity != [0, 0]:
        angle = math.degrees(math.atan2(ball_velocity[1], ball_velocity[0]))
        rotated_ball = rotate_image(ball_img, -angle)
        ball_rect = rotated_ball.get_rect(center=(ball_position[0], ball_position[1]))
        screen.blit(rotated_ball, ball_rect.topleft)
    else:
        screen.blit(ball_img, (ball_position[0] - 79 // 2, ball_position[1] - 36 // 2))

    # Easter egg blackhole
    if current_level == 0 and 0 <= ball_position[0] <= 150 and 0 <= ball_position[1] <= 150:
        if not blackhole_displayed:
            if blackhole_start_time is None:
                blackhole_start_time = pygame.time.get_ticks()
                #7ish seconds to give enough time for BHole to give the "being sucked in" effect ;)
            elif pygame.time.get_ticks() - blackhole_start_time >= 7000:
                blackhole_displayed = True
                blackhole_display_start_time = pygame.time.get_ticks()
        if blackhole_displayed:
            screen.blit(blackhole_img, (
            SCREEN_WIDTH // 2 - blackhole_img.get_width() // 2, SCREEN_HEIGHT // 2 - blackhole_img.get_height() // 2))
            if pygame.time.get_ticks() - blackhole_display_start_time >= 15000: #enough? time to get the joke I hope)
                running = False

    # Spawning cats + saved picture
    if current_level == 0:
        pass
    else:
        for obj in custom_objects:
            screen.blit(obj['img'], obj['pos'])
        
    #point reset for bholes
    for level in LEVELS:
        black_zone = LEVELS[current_level]['black_zones']
        if lose_check((ball_position[0], ball_position[1]), black_zone):
            if zone_timer is None:
                zone_timer = pygame.time.get_ticks()
            elif pygame.time.get_ticks() - zone_timer >= 5000:
                points = 0
                text_3 = the_font.render("You've lost your crew, again.", False, (255, 255, 255))
                screen.blit(text_3, (320, 80))
        else:
            zone_timer = None


    current_time = pygame.time.get_ticks()
    if display_collected and current_time - display_start_time < 3000 and current_level !=0:  # Display for 3 seconds
        screen.blit(saved_img, (
        SCREEN_WIDTH // 2 - saved_img.get_width() // 2, 60 - saved_img.get_height() // 2))
        text = the_font.render(f'only {points} so far!', False, (255, 255, 255))
        screen.blit(text, (SCREEN_WIDTH // 2 - 160, 115))
    else:
        display_collected = False
    #removing after collision
    for obj in custom_objects[:]:
        if check_object_collision(ball_position, obj['pos']):
            custom_objects.remove(obj)
            points +=1
            text_2 = the_font.render(f'You have saved {points} kitties!', False, (255, 255, 255))
            display_collected = True
            display_start_time = pygame.time.get_ticks()

            if not custom_objects:  # If all kitties r gone, spawn new
                spawn_objects(4)

    # Pointer stuff
    mouse_pos = pygame.mouse.get_pos()
    pointer_angle = math.degrees(math.atan2(mouse_pos[1] - ball_position[1], mouse_pos[0] - ball_position[0]))
    rotated_pointer = rotate_image(pointer_img, -pointer_angle)
    pointer_rect = rotated_pointer.get_rect(center=mouse_pos)
    screen.blit(rotated_pointer, pointer_rect.topleft)
    pygame.display.flip()
    pygame.time.Clock().tick(60)
## end of main loop
pygame.mixer.music.stop()
pygame.mixer.quit()
pygame.quit()
sys.exit()

