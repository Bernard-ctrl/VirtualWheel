"""Step 7: Optional Windows keyboard steering output."""

import ctypes
import sys

import cv2
import pygame

from step2_two_hand_tracking import TwoHandTracker
from step3_steering_calculation import calculate_steering_angle, direction_for
from step4_calibrated_steering import ContinuousAngle
from step5_steering_filter import ExponentialSmoother, SMOOTHING, apply_steering_settings

TRACKING_GRACE_FRAMES = 8
KEYBOARD_OUTPUT_ENABLED = False
KEY_THRESHOLD_DEGREES = 1.5
THUMB_GESTURE_THRESHOLD = 0.06
LEFT_KEY, RIGHT_KEY = 0x25, 0x27  # Windows virtual-key codes
ACCELERATE_KEY, BRAKE_KEY = 0x26, 0x28  # Up and Down arrows


class KeyboardOutput:
    def __init__(self):
        self.left_down = False
        self.right_down = False
        self.accelerate_down = False
        self.brake_down = False

    @staticmethod
    def set_key(key, pressed):
        if sys.platform == "win32":
            ctypes.windll.user32.keybd_event(key, 0, 0 if pressed else 2, 0)

    def update(self, angle, enabled):
        left = enabled and angle is not None and angle < -KEY_THRESHOLD_DEGREES
        right = enabled and angle is not None and angle > KEY_THRESHOLD_DEGREES
        if left != self.left_down:
            self.set_key(LEFT_KEY, left)
            self.left_down = left
        elif left:
            # Synthetic key-down events do not always trigger Windows key
            # repeat, so emit one on every video frame while held.
            self.set_key(LEFT_KEY, True)
        if right != self.right_down:
            self.set_key(RIGHT_KEY, right)
            self.right_down = right
        elif right:
            self.set_key(RIGHT_KEY, True)

    def release(self):
        self.update(None, False)
        self.update_throttle(None, False)

    def update_throttle(self, action, enabled):
        accelerate = enabled and action == "ACCELERATE"
        brake = enabled and action == "BRAKE"
        if accelerate != self.accelerate_down:
            self.set_key(ACCELERATE_KEY, accelerate)
            self.accelerate_down = accelerate
        elif accelerate:
            self.set_key(ACCELERATE_KEY, True)
        if brake != self.brake_down:
            self.set_key(BRAKE_KEY, brake)
            self.brake_down = brake
        elif brake:
            self.set_key(BRAKE_KEY, True)


def thumb_action(data):
    """Classify the right thumb using its direction relative to its MCP joint."""
    hand = data.get("Right")
    if hand is None:
        return None
    tip_y = hand["thumb_tip_normalized"][1]
    mcp_y = hand["thumb_mcp_normalized"][1]
    if tip_y < mcp_y - THUMB_GESTURE_THRESHOLD:
        return "ACCELERATE"
    if tip_y > mcp_y + THUMB_GESTURE_THRESHOLD:
        return "BRAKE"
    return None


def main():
    tracker = TwoHandTracker()
    continuous = ContinuousAngle()
    smoother = ExponentialSmoother(SMOOTHING)
    keyboard = KeyboardOutput()
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("ERROR: Cannot open webcam. Try camera index 1.")
        tracker.close()
        sys.exit(1)

    pygame.init()
    screen = pygame.display.set_mode((900, 620))
    pygame.display.set_caption("VirtualWheel - Step 7 Keyboard Output")
    font, small = pygame.font.Font(None, 30), pygame.font.Font(None, 24)
    clock = pygame.time.Clock()
    enabled = KEYBOARD_OUTPUT_ENABLED
    missing_frames, last_angle, running = 0, 0.0, True
    print("Keyboard Output - Step 7 (E toggles output, Q quits)")

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
                        print(f"Keyboard output: {'ENABLED' if enabled else 'DISABLED'}")

            ok, frame = camera.read()
            if not ok:
                break
            results = tracker.process(frame)
            tracker.draw(frame, results)
            data = tracker.get_hand_data(results, frame.shape)
            raw = calculate_steering_angle(data)
            smooth = smoother.update(continuous.update(raw))
            angle = apply_steering_settings(smooth)

            if len(data) == 2 and angle is not None:
                missing_frames, last_angle = 0, angle
            else:
                missing_frames += 1
                if missing_frames <= TRACKING_GRACE_FRAMES:
                    angle = last_angle
                else:
                    angle = None
                    keyboard.update(None, False)
                    continuous.reset()
                    smoother.value = None

            active = len(data) == 2 or missing_frames <= TRACKING_GRACE_FRAMES
            keyboard.update(angle, enabled and active)
            direction = direction_for(angle)
            color = (80, 230, 130) if active else (240, 90, 90)
            action = thumb_action(data)
            keyboard.update_throttle(action, enabled and active)
            frame = cv2.cvtColor(cv2.resize(frame, (640, 480)), cv2.COLOR_BGR2RGB)
            screen.fill((12, 14, 18))
            screen.blit(pygame.surfarray.make_surface(frame.swapaxes(0, 1)), (20, 70))
            pygame.draw.rect(screen, (100, 105, 115), (20, 70, 640, 480), 2)
            screen.blit(font.render("Keyboard Steering - Step 7", True, (80, 200, 255)), (20, 20))
            angle_text = "--" if angle is None else f"{angle:+.1f} deg"
            lines = [f"Steering Angle: {angle_text}", f"Direction: {direction}",
                     f"Hands Detected: {len(data)}/2", f"Status: {'ACTIVE' if active else 'PAUSED'}",
                     f"Keyboard: {'ENABLED' if enabled else 'DISABLED'}",
                     f"Throttle: {action or 'NEUTRAL'}"]
            for i, line in enumerate(lines):
                screen.blit(font.render(line, True, (255, 210, 80) if i == 4 else color), (690, 120 + i * 42))
            screen.blit(small.render("E: toggle output   Q: quit", True, (210, 210, 215)), (690, 410))
            screen.blit(small.render("Right thumb up: Up   down: Down", True, (210, 210, 215)), (690, 440))
            pygame.display.flip()
            clock.tick(30)
    finally:
        keyboard.release()
        camera.release()
        tracker.close()
        pygame.quit()
        cv2.destroyAllWindows()
        print("Cleanup complete!")


if __name__ == "__main__":
    main()
