"""Small keyboard-controlled racing game for testing VirtualWheel output."""

import random
import sys

import pygame

WIDTH, HEIGHT = 900, 650
ROAD_LEFT, ROAD_RIGHT = 220, 680
CAR_SIZE = (42, 72)
FPS = 60
STEERING_SPEED = 720.0


def make_obstacle(y: int):
    return pygame.Rect(random.randint(ROAD_LEFT + 35, ROAD_RIGHT - 35 - 34), y, 34, 58)


def main() -> None:
    pygame.init()
    pygame.joystick.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("VirtualWheel Test Racing Game")
    clock = pygame.time.Clock()
    joystick = None
    joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
    vjoy_candidates = [j for j in joysticks if "vjoy" in j.get_name().lower()]
    if vjoy_candidates:
        joystick = vjoy_candidates[0]
    elif joysticks:
        joystick = joysticks[0]
    if joystick:
        joystick.init()
        print(f"Joystick selected: {joystick.get_name()}")
        print(f"Axes available: {joystick.get_numaxes()}")
    else:
        print("No joystick detected; keyboard controls only")
    title_font = pygame.font.Font(None, 34)
    font = pygame.font.Font(None, 26)

    car = pygame.Rect(WIDTH // 2 - CAR_SIZE[0] // 2, HEIGHT - 125, *CAR_SIZE)
    obstacles = [make_obstacle(-100), make_obstacle(-360)]
    road_dash_offset = 0
    speed = 5
    score = 0
    game_over = False
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game_over:
                    car.x = WIDTH // 2 - CAR_SIZE[0] // 2
                    obstacles = [make_obstacle(-100), make_obstacle(-360)]
                    score = 0
                    game_over = False

        keys = pygame.key.get_pressed()
        if not game_over:
            steering = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
            throttle = int(keys[pygame.K_UP]) - int(keys[pygame.K_DOWN])
            joystick_steering = 0.0
            joystick_throttle = 0.0
            if joystick and joystick.get_numaxes() >= 2:
                joystick_steering = joystick.get_axis(0)
                joystick_throttle = joystick.get_axis(1)
                if abs(joystick_steering) > 0.02:
                    steering = max(-1.0, min(1.0, joystick_steering * 1.8))
                if abs(joystick_throttle) > 0.02:
                    throttle = joystick_throttle
            car.x += int(STEERING_SPEED * steering * dt)
            car.left = max(car.left, ROAD_LEFT + 12)
            car.right = min(car.right, ROAD_RIGHT - 12)

            if throttle > 0.2:
                speed = min(12.0, speed + 8.0 * dt)
            elif throttle < -0.2:
                speed = max(1.0, speed - 14.0 * dt)
            else:
                speed = max(5.0, speed - 2.0 * dt)

            for obstacle in obstacles:
                obstacle.y += int(speed)
                if obstacle.top > HEIGHT:
                    obstacle.topleft = make_obstacle(-random.randint(100, 260)).topleft
                    score += 1
            if any(car.colliderect(obstacle) for obstacle in obstacles):
                game_over = True
            road_dash_offset = (road_dash_offset + int(speed)) % 80

        screen.fill((25, 125, 55))
        pygame.draw.rect(screen, (55, 55, 60), (ROAD_LEFT, 0, ROAD_RIGHT - ROAD_LEFT, HEIGHT))
        pygame.draw.line(screen, (245, 245, 245), (ROAD_LEFT, 0), (ROAD_LEFT, HEIGHT), 5)
        pygame.draw.line(screen, (245, 245, 245), (ROAD_RIGHT, 0), (ROAD_RIGHT, HEIGHT), 5)
        for y in range(-80, HEIGHT, 80):
            y_position = y + road_dash_offset
            pygame.draw.rect(screen, (220, 220, 180), (WIDTH // 2 - 5, y_position, 10, 42))

        for obstacle in obstacles:
            pygame.draw.rect(screen, (230, 75, 45), obstacle, border_radius=5)
            pygame.draw.rect(screen, (255, 220, 80), (obstacle.x + 6, obstacle.y + 8, 22, 12))
        pygame.draw.rect(screen, (55, 150, 245), car, border_radius=8)
        pygame.draw.rect(screen, (180, 230, 255), (car.x + 8, car.y + 10, 26, 20), border_radius=4)
        pygame.draw.rect(screen, (25, 70, 145), (car.x + 6, car.bottom - 15, 30, 8), border_radius=3)

        screen.blit(title_font.render("VirtualWheel Test Racing Game", True, (255, 255, 255)), (20, 18))
        screen.blit(font.render("Use arrows, keyboard output, or vJoy axes", True, (235, 235, 235)), (20, 58))
        screen.blit(font.render(f"Score: {score}    Speed: {speed:.1f}", True, (255, 255, 255)), (20, 92))
        if joystick:
            screen.blit(font.render(f"vJoy X: {joystick_steering:+.2f}  Y: {joystick_throttle:+.2f}",
                                    True, (255, 255, 255)), (20, 126))
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            message = title_font.render("CRASH! Press R to restart or Esc to quit", True, (255, 220, 80))
            screen.blit(message, message.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
