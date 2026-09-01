"""Step 8: Optional vJoy analog steering and throttle output."""

import sys

import cv2
import pygame
import pyvjoy

from step2_two_hand_tracking import TwoHandTracker
from step3_steering_calculation import calculate_steering_angle, direction_for
from step4_calibrated_steering import ContinuousAngle
from step5_steering_filter import ExponentialSmoother, MAX_STEERING_DEGREES, apply_steering_settings
from step7_keyboard_output import THUMB_GESTURE_THRESHOLD, thumb_action

VJOY_DEVICE_ID = 1
TRACKING_GRACE_FRAMES = 8
STEERING_AXIS = pyvjoy.HID_USAGE_X
THROTTLE_AXIS = pyvjoy.HID_USAGE_Y


def axis_value(value: float) -> int:
    """Convert a -1..+1 value to a vJoy axis value from 0..32768."""
    return max(0, min(32768, int((value + 1.0) * 16384)))


def steering_axis(angle) -> int:
    if angle is None:
        return 16384
    normalized = max(-1.0, min(1.0, angle / MAX_STEERING_DEGREES))
    return axis_value(normalized)


def throttle_axis(action) -> int:
    if action == "ACCELERATE":
        return 32768
    if action == "BRAKE":
        return 0
    return 16384


def main() -> None:
    try:
        joystick = pyvjoy.VJoyDevice(VJOY_DEVICE_ID)
    except Exception as error:
        print("ERROR: Could not connect to vJoy device 1.")
        print("Install the vJoy driver, create device 1, and try again.")
        print(f"Details: {error}")
        sys.exit(1)

    tracker = TwoHandTracker()
    continuous = ContinuousAngle()
    smoother = ExponentialSmoother(0.65)
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        joystick.set_axis(STEERING_AXIS, 16384)
        joystick.set_axis(THROTTLE_AXIS, 16384)
        tracker.close()
        print("ERROR: Cannot open webcam. Try camera index 1.")
        sys.exit(1)

    pygame.init()
    screen = pygame.display.set_mode((900, 620))
    pygame.display.set_caption("VirtualWheel - Step 8 Virtual Gamepad")
    font, small = pygame.font.Font(None, 30), pygame.font.Font(None, 24)
    clock = pygame.time.Clock()
    enabled = False
    missing_frames, last_angle, running = 0, 0.0, True
    print("Virtual Gamepad Output - Step 8")
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
                        print(f"vJoy output: {'ENABLED' if enabled else 'DISABLED'}")

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
                    angle = None
                    action = None
                    continuous.reset()
                    smoother.value = None

            active = len(data) == 2 or missing_frames <= TRACKING_GRACE_FRAMES
            if enabled and active:
                joystick.set_axis(STEERING_AXIS, steering_axis(angle))
                joystick.set_axis(THROTTLE_AXIS, throttle_axis(action))
            else:
                joystick.set_axis(STEERING_AXIS, 16384)
                joystick.set_axis(THROTTLE_AXIS, 16384)

            frame = cv2.cvtColor(cv2.resize(frame, (640, 480)), cv2.COLOR_BGR2RGB)
            screen.fill((12, 14, 18))
            screen.blit(pygame.surfarray.make_surface(frame.swapaxes(0, 1)), (20, 70))
            pygame.draw.rect(screen, (100, 105, 115), (20, 70, 640, 480), 2)
            color = (80, 230, 130) if active else (240, 90, 90)
            angle_text = "--" if angle is None else f"{angle:+.1f} deg"
            screen.blit(font.render("Virtual Gamepad - Step 8", True, (80, 200, 255)), (20, 20))
            lines = [f"Steering: {angle_text}", f"Direction: {direction_for(angle)}",
                     f"Throttle: {action or 'NEUTRAL'}", f"Hands: {len(data)}/2",
                     f"Status: {'ACTIVE' if active else 'PAUSED'}",
                     f"vJoy: {'ENABLED' if enabled else 'DISABLED'}"]
            for i, line in enumerate(lines):
                screen.blit(font.render(line, True, (255, 210, 80) if i == 5 else color),
                            (690, 120 + i * 38))
            screen.blit(small.render("E: toggle output   Q: quit", True, (210, 210, 215)), (690, 380))
            screen.blit(small.render("X: steering   Y: throttle/brake", True, (210, 210, 215)), (690, 410))
            pygame.display.flip()
            clock.tick(30)
    finally:
        joystick.set_axis(STEERING_AXIS, 16384)
        joystick.set_axis(THROTTLE_AXIS, 16384)
        camera.release()
        tracker.close()
        pygame.quit()
        cv2.destroyAllWindows()
        print("vJoy axes centered. Cleanup complete!")


if __name__ == "__main__":
    main()
