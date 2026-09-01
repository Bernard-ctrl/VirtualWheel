"""Step 6: Display a virtual steering wheel driven by both hands."""

import math
import sys

import cv2
import pygame

from step2_two_hand_tracking import TwoHandTracker
from step3_steering_calculation import calculate_steering_angle, direction_for
from step4_calibrated_steering import ContinuousAngle
from step5_steering_filter import ExponentialSmoother, SMOOTHING, apply_steering_settings

WINDOW_SIZE = (1100, 700)
CAMERA_SIZE = (640, 480)
WHEEL_CENTER = (855, 365)
WHEEL_RADIUS = 190
TRACKING_GRACE_FRAMES = 8


def draw_wheel(screen: pygame.Surface, angle: float) -> None:
    center = WHEEL_CENTER
    pygame.draw.circle(screen, (45, 48, 55), center, WHEEL_RADIUS + 12)
    pygame.draw.circle(screen, (18, 20, 25), center, WHEEL_RADIUS)
    pygame.draw.circle(screen, (115, 125, 140), center, WHEEL_RADIUS, 10)
    for spoke_angle in (0, 120, 240):
        radians = math.radians(spoke_angle - angle)
        end = (int(center[0] + math.cos(radians) * (WHEEL_RADIUS - 18)),
               int(center[1] - math.sin(radians) * (WHEEL_RADIUS - 18)))
        pygame.draw.line(screen, (40, 175, 235), center, end, 14)
    pygame.draw.circle(screen, (35, 38, 45), center, 48)
    pygame.draw.circle(screen, (105, 115, 130), center, 48, 5)
    pygame.draw.circle(screen, (40, 175, 235), center, 12)


def draw_camera(screen: pygame.Surface, frame) -> None:
    frame = cv2.resize(frame, CAMERA_SIZE)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    surface = pygame.surfarray.make_surface(frame.swapaxes(0, 1))
    screen.blit(surface, (20, 100))
    pygame.draw.rect(screen, (100, 105, 115), (20, 100, *CAMERA_SIZE), 2)


def draw_text(screen, font, message: str, position, color=(235, 235, 240)) -> None:
    screen.blit(font.render(message, True, color), position)


def main() -> None:
    tracker = TwoHandTracker()
    continuous = ContinuousAngle()
    smoother = ExponentialSmoother(SMOOTHING)
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("ERROR: Cannot open webcam. Try camera index 1.")
        tracker.close()
        sys.exit(1)

    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("VirtualWheel - Step 6")
    title_font = pygame.font.Font(None, 36)
    body_font = pygame.font.Font(None, 28)
    clock = pygame.time.Clock()
    running = True
    missing_frames = 0
    last_angle = 0.0
    print("Virtual Steering Wheel - Step 6")
    print("Press Q or close the window to quit")

    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
                    running = False

            ok, frame = camera.read()
            if not ok:
                print("ERROR: Failed to read frame from webcam!")
                break
            results = tracker.process(frame)
            tracker.draw(frame, results)
            data = tracker.get_hand_data(results, frame.shape)
            raw = calculate_steering_angle(data)
            continuous_value = continuous.update(raw)
            smooth_value = smoother.update(continuous_value)
            angle = apply_steering_settings(smooth_value)
            if len(data) == 2 and angle is not None:
                missing_frames = 0
                last_angle = angle
            else:
                missing_frames += 1
                if missing_frames <= TRACKING_GRACE_FRAMES:
                    angle = last_angle
                else:
                    angle = None
                    continuous.reset()
                    smoother.value = None
            direction = direction_for(angle)
            active = len(data) == 2 or missing_frames <= TRACKING_GRACE_FRAMES

            screen.fill((12, 14, 18))
            draw_text(screen, title_font, "Virtual Steering Wheel - Step 6", (20, 24), (80, 200, 255))
            draw_camera(screen, frame)
            draw_wheel(screen, 0.0 if angle is None else angle)
            draw_text(screen, body_font, "Camera feed", (20, 72), (180, 185, 195))
            draw_text(screen, body_font, "Virtual wheel", (755, 72), (180, 185, 195))

            info_x, info_y = 700, 585
            info_color = (80, 230, 130) if active else (240, 90, 90)
            angle_text = "--" if angle is None else f"{angle:+.1f} deg"
            draw_text(screen, body_font, f"Steering Angle: {angle_text}", (info_x, info_y))
            draw_text(screen, body_font, f"Direction: {direction}", (info_x, info_y + 30), info_color)
            draw_text(screen, body_font, f"Hands Detected: {len(data)}/2", (info_x, info_y + 60), info_color)
            draw_text(screen, body_font, f"Status: {'ACTIVE' if active else 'PAUSED'}", (info_x, info_y + 90), info_color)
            pygame.display.flip()
            clock.tick(30)
    finally:
        camera.release()
        tracker.close()
        pygame.quit()
        cv2.destroyAllWindows()
        print("Cleanup complete!")


if __name__ == "__main__":
    main()
