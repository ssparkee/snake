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
num_segments = 12
angle_step = 2 * math.pi / num_segments


def init(width, height, radius=100, circle_radius=10):
    global WIDTH, HEIGHT, center, circle_positions, RADIUS, CIRCLE_RADIUS, EYE_RADIUS, EYE_OFFSET, LEAF_WIDTH, LEAF_HEIGHT, LEAF_OFFSET_X, LEAF_OFFSET_Y
    WIDTH = width
    HEIGHT = height
    RADIUS = radius
    CIRCLE_RADIUS = circle_radius  # Store the circle radius
    center = (WIDTH // 2, HEIGHT // 2)
    circle_positions = get_circle_positions()

    # Adjust eye size and offset based on circle radius
    EYE_RADIUS = 2
    EYE_OFFSET = 7

    # Adjust leaf size and position based on circle radius
    LEAF_WIDTH = CIRCLE_RADIUS // 2.5  # Scale leaf width
    LEAF_HEIGHT = CIRCLE_RADIUS // 1.5  # Scale leaf height
    # Leaf horizontal position relative to apple
    LEAF_OFFSET_X = -CIRCLE_RADIUS // 5
    LEAF_OFFSET_Y = -CIRCLE_RADIUS * 1.6  # Leaf vertical position relative to apple


def get_circle_positions():
    positions = []
    for i in range(num_segments):
        angle = i * angle_step
        x = center[0] + int(math.cos(angle) * RADIUS)
        y = center[1] + int(math.sin(angle) * RADIUS)
        positions.append((x, y))
    return positions


snake_length = 3
snake_segments = [0] * snake_length
head_color = RED
body_color = GREEN
apple_color = RED

current_segment = 0


def drawLoadingSnake(clock, screen, moveSegments=True):
    global current_segment

    if moveSegments:
        apple_position = (current_segment + 2) % num_segments
    else:
        apple_position = (current_segment + 1) % num_segments

    # Draw circles for the snake and the apple
    for i, pos in enumerate(circle_positions):
        # Use dynamic circle radius
        pygame.draw.circle(screen, GREY, pos, CIRCLE_RADIUS)

    pygame.draw.circle(screen, apple_color,
                       circle_positions[apple_position], CIRCLE_RADIUS)

    if moveSegments:
        for i in range(snake_length - 1, 0, -1):
            snake_segments[i] = snake_segments[i - 1]
        snake_segments[0] = current_segment

    head_position = circle_positions[snake_segments[0]]
    apple_pos = circle_positions[apple_position]
    head_look = circle_positions[apple_position-1]

    # Define the rectangle for the leaf, adjusted to the circle size
    leaf_rect = pygame.Rect(apple_pos[0] + LEAF_OFFSET_X,
                            apple_pos[1] + LEAF_OFFSET_Y, LEAF_WIDTH, LEAF_HEIGHT)

    # Create the leaf surface
    leaf_surface = pygame.Surface((LEAF_WIDTH, LEAF_HEIGHT), pygame.SRCALPHA)
    pygame.draw.ellipse(leaf_surface, LEAF_GREEN,
                        (0, 0, LEAF_WIDTH, LEAF_HEIGHT))

    rotated_leaf = pygame.transform.rotate(leaf_surface, -60)

    # Blit (draw) the rotated leaf on the screen
    screen.blit(rotated_leaf, leaf_rect.topleft)

    # Adjust head angle for eye positioning
    head_angle = math.atan2(
        head_look[1] - head_position[1], head_look[0] - head_position[0])

    left_eye_position = (
        head_position[0] +
        int(math.cos(head_angle + math.pi / 4) * EYE_OFFSET),
        head_position[1] +
        int(math.sin(head_angle + math.pi / 4) * EYE_OFFSET)
    )
    right_eye_position = (
        head_position[0] +
        int(math.cos(head_angle - math.pi / 4) * EYE_OFFSET),
        head_position[1] +
        int(math.sin(head_angle - math.pi / 4) * EYE_OFFSET)
    )

    # Draw snake head and eyes
    for i, segment in enumerate(snake_segments):
        if i == 0:
            pygame.draw.circle(screen, head_color,
                               head_position, CIRCLE_RADIUS)
            if CIRCLE_RADIUS == 10:
                pygame.draw.circle(screen, WHITE, left_eye_position, EYE_RADIUS)
                pygame.draw.circle(screen, WHITE, right_eye_position, EYE_RADIUS)
        else:
            pygame.draw.circle(screen, body_color,
                               circle_positions[segment], CIRCLE_RADIUS)

    if moveSegments:
        current_segment = (current_segment + 1) % num_segments
