"""Step 10: Optional serial steering output for Arduino/ESP32."""

import sys
import time

import cv2
import pygame
import serial

from step2_two_hand_tracking import TwoHandTracker
from step3_steering_calculation import calculate_steering_angle, direction_for
from step4_calibrated_steering import ContinuousAngle
from step5_steering_filter import ExponentialSmoother, apply_steering_settings
from step7_keyboard_output import thumb_action

SERIAL_PORT = "COM3"       # Change this to your Arduino/ESP32 port.
BAUD_RATE = 115200
TRACKING_GRACE_FRAMES = 8


def serial_message(angle, action) -> str:
    """Create one human-readable, newline-terminated serial message."""
    steer = 0.0 if angle is None else angle
    throttle = action or "NEUTRAL"
    return f"STEER:{steer:.1f};THROTTLE:{throttle}\n"


def main() -> None:
    try:
        connection = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
        time.sleep(2.0)  # Allow Arduino boards to reset after opening serial.
    except serial.SerialException as error:
        print(f"ERROR: Could not open {SERIAL_PORT} at {BAUD_RATE} baud.")
        print("Change SERIAL_PORT at the top of this file and try again.")
        print(f"Details: {error}")
        sys.exit(1)

    tracker = TwoHandTracker()
    continuous = ContinuousAngle()
    smoother = ExponentialSmoother(0.65)
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        connection.close()
        tracker.close()
        print("ERROR: Cannot open webcam. Try camera index 1.")
        sys.exit(1)

    pygame.init()
    screen = pygame.display.set_mode((900, 620))
    pygame.display.set_caption("VirtualWheel - Step 10 Serial Output")
    font, small = pygame.font.Font(None, 30), pygame.font.Font(None, 24)
    clock = pygame.time.Clock()
    enabled = False
    missing_frames, last_angle, running = 0, 0.0, True
    print(f"Serial Output - Step 10 ({SERIAL_PORT}, {BAUD_RATE} baud)")
    print("E toggles output, Q quits")

    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
                    elif event.key == pygame.K_e:
                        enabled = not enabled
                        print(f"Serial output: {'ENABLED' if enabled else 'DISABLED'}")

            ok, frame = camera.read()
            if not ok:
                break
            results = tracker.process(frame)
            tracker.draw(frame, results)
            data = tracker.get_hand_data(results, frame.shape)
            raw = calculate_steering_angle(data)
            smooth = smoother.update(continuous.update(raw))
            angle = apply_steering_settings(smooth)
            action = thumb_action(data)

            if len(data) == 2 and angle is not None:
                missing_frames, last_angle = 0, angle
            else:
                missing_frames += 1
                if missing_frames <= TRACKING_GRACE_FRAMES:
                    angle = last_angle
                else:
                    angle, action = None, None
                    continuous.reset()
                    smoother.value = None

            active = len(data) == 2 or missing_frames <= TRACKING_GRACE_FRAMES
            if enabled and active:
                connection.write(serial_message(angle, action).encode("ascii"))
            else:
                connection.write(serial_message(None, None).encode("ascii"))

            frame = cv2.cvtColor(cv2.resize(frame, (640, 480)), cv2.COLOR_BGR2RGB)
            screen.fill((12, 14, 18))
            screen.blit(pygame.surfarray.make_surface(frame.swapaxes(0, 1)), (20, 70))
            pygame.draw.rect(screen, (100, 105, 115), (20, 70, 640, 480), 2)
            color = (80, 230, 130) if active else (240, 90, 90)
            angle_text = "--" if angle is None else f"{angle:+.1f} deg"
            screen.blit(font.render("Serial Output - Step 10", True, (80, 200, 255)), (20, 20))
            lines = [f"Steering: {angle_text}", f"Throttle: {action or 'NEUTRAL'}",
                     f"Hands: {len(data)}/2", f"Status: {'ACTIVE' if active else 'PAUSED'}",
                     f"Serial: {'ENABLED' if enabled else 'DISABLED'}", f"Port: {SERIAL_PORT}"]
            for i, line in enumerate(lines):
                screen.blit(font.render(line, True, (255, 210, 80) if i == 4 else color),
                            (690, 120 + i * 38))
            screen.blit(small.render("E: toggle output   Q: quit", True, (210, 210, 215)), (690, 380))
            pygame.display.flip()
            clock.tick(30)
    finally:
        connection.write(serial_message(None, None).encode("ascii"))
        connection.close()
        camera.release()
        tracker.close()
        pygame.quit()
        cv2.destroyAllWindows()
        print("Neutral serial message sent. Cleanup complete!")


if __name__ == "__main__":
    main()
