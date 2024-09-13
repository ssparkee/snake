import pygame
import math

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GREY = (100, 100, 100)
LEAF_GREEN = (0, 200, 0)

# Wheel settings
radius = 100
num_segments = 12

# Angle increment for each segment
angle_step = 2 * math.pi / num_segments


def init(width, height):
    global WIDTH, HEIGHT, center, circle_positions
    WIDTH = width
    HEIGHT = height
    center = (WIDTH // 2, HEIGHT // 2)
    circle_positions = get_circle_positions()

def get_circle_positions():
    positions = []
    for i in range(num_segments):
        angle = i * angle_step
        x = center[0] + int(math.cos(angle) * radius)
        y = center[1] + int(math.sin(angle) * radius)
        positions.append((x, y))
    return positions

snake_length = 3
snake_segments = [0] * snake_length
head_color = RED
body_color = GREEN
apple_color = RED

eye_radius = 2
eye_offset = 7
current_segment = 0

def drawLoadingSnake(clock, screen, moveSegments=True):
    global current_segment

    apple_position = (current_segment + 2) % num_segments

    for i, pos in enumerate(circle_positions):
        pygame.draw.circle(screen, GREY, pos, 10)

    pygame.draw.circle(screen, apple_color,
                       circle_positions[apple_position], 10)

    if moveSegments:
        for i in range(snake_length - 1, 0, -1):
            snake_segments[i] = snake_segments[i - 1]
        snake_segments[0] = current_segment

    head_position = circle_positions[snake_segments[0]]
    apple_pos = circle_positions[apple_position]
    head_look = circle_positions[apple_position-1]

    leaf_offset_x = -2   # More to the right
    leaf_offset_y = -16  # Positioned slightly above the apple

    # Leaf properties
    leaf_width = 4
    leaf_height = 7

    # Define the rectangle for the leaf
    leaf_rect = pygame.Rect(apple_pos[0] + leaf_offset_x,
                            apple_pos[1] + leaf_offset_y, leaf_width, leaf_height)

    leaf_surface = pygame.Surface((leaf_width, leaf_height), pygame.SRCALPHA)
    pygame.draw.ellipse(leaf_surface, LEAF_GREEN, (0, 0, leaf_width, leaf_height))

    rotated_leaf = pygame.transform.rotate(leaf_surface, -60)

    # Blit (draw) the rotated leaf on the screen
    screen.blit(rotated_leaf, leaf_rect.topleft)

    head_angle = math.atan2(
        head_look[1] - head_position[1], head_look[0] - head_position[0])

    left_eye_position = (
        head_position[0] +
        int(math.cos(head_angle + math.pi / 4) * eye_offset),
        head_position[1] +
        int(math.sin(head_angle + math.pi / 4) * eye_offset)
    )
    right_eye_position = (
        head_position[0] +
        int(math.cos(head_angle - math.pi / 4) * eye_offset),
        head_position[1] +
        int(math.sin(head_angle - math.pi / 4) * eye_offset)
    )

    for i, segment in enumerate(snake_segments):
        if i == 0:
            pygame.draw.circle(screen, head_color, head_position, 10)

            pygame.draw.circle(screen, WHITE, left_eye_position, eye_radius)
            pygame.draw.circle(screen, WHITE, right_eye_position, eye_radius)
        else:
            pygame.draw.circle(screen, body_color,
                               circle_positions[segment], 10)

    if moveSegments:
        current_segment = (current_segment + 1) % num_segments
