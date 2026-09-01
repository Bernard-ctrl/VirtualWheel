"""Step 11: Integrated VirtualWheel application."""

import sys
import time

import cv2
import pygame
import pyvjoy
import serial

from step2_two_hand_tracking import TwoHandTracker
from step3_steering_calculation import calculate_steering_angle, direction_for
from step4_calibrated_steering import ContinuousAngle
from step5_steering_filter import (
    ExponentialSmoother,
    MAX_STEERING_DEGREES,
    SMOOTHING,
    apply_steering_settings,
)
from step6_virtual_wheel import draw_camera, draw_text, draw_wheel
from step7_keyboard_output import KeyboardOutput, thumb_action
from step8_virtual_gamepad import axis_value, steering_axis, throttle_axis
from step10_serial_output import SERIAL_PORT, BAUD_RATE, serial_message

WINDOW_SIZE = (1100, 700)
TRACKING_GRACE_FRAMES = 8


class IntegratedOutputs:
    def __init__(self):
        self.keyboard = KeyboardOutput()
        self.vjoy = None
        self.serial = None
        self.status = "No output"

    def close_devices(self):
        self.keyboard.release()
        if self.vjoy is not None:
            self.vjoy.set_axis(pyvjoy.HID_USAGE_X, 16384)
            self.vjoy.set_axis(pyvjoy.HID_USAGE_Y, 16384)
            self.vjoy = None
        if self.serial is not None:
            self.serial.write(serial_message(None, None).encode("ascii"))
            self.serial.close()
            self.serial = None

    def select(self, mode):
        self.close_devices()
        if mode == "KEYBOARD":
            self.status = "Keyboard ready"
        elif mode == "VJOY":
            try:
                self.vjoy = pyvjoy.VJoyDevice(1)
                self.status = "vJoy device 1 ready"
            except Exception as error:
                self.status = f"vJoy unavailable: {error}"
        elif mode == "SERIAL":
            try:
                self.serial = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1)
                time.sleep(2.0)
                self.status = f"Serial {SERIAL_PORT} ready"
            except serial.SerialException as error:
                self.status = f"Serial unavailable: {error}"
        else:
            self.status = "Output disabled"

    def send(self, mode, angle, action, enabled):
        if not enabled:
            self.keyboard.update(None, False)
            self.keyboard.update_throttle(None, False)
            if self.vjoy is not None:
                self.vjoy.set_axis(pyvjoy.HID_USAGE_X, 16384)
                self.vjoy.set_axis(pyvjoy.HID_USAGE_Y, 16384)
            if self.serial is not None:
                self.serial.write(serial_message(None, None).encode("ascii"))
            return

        if mode == "KEYBOARD":
            self.keyboard.update(angle, True)
            self.keyboard.update_throttle(action, True)
        elif mode == "VJOY" and self.vjoy is not None:
            self.vjoy.set_axis(pyvjoy.HID_USAGE_X, steering_axis(angle))
            self.vjoy.set_axis(pyvjoy.HID_USAGE_Y, throttle_axis(action))
        elif mode == "SERIAL" and self.serial is not None:
            self.serial.write(serial_message(angle, action).encode("ascii"))


def main():
    tracker = TwoHandTracker()
    continuous = ContinuousAngle()
    smoother = ExponentialSmoother(SMOOTHING)
    outputs = IntegratedOutputs()
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        tracker.close()
        print("ERROR: Cannot open webcam. Try camera index 1.")
        sys.exit(1)

    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("VirtualWheel - Integrated Application")
    title_font = pygame.font.Font(None, 36)
    body_font = pygame.font.Font(None, 27)
    small_font = pygame.font.Font(None, 23)
    clock = pygame.time.Clock()
    modes = ("OFF", "KEYBOARD", "VJOY", "SERIAL")
    mode_index = 0
    mode = modes[mode_index]
    enabled = False
    missing_frames, last_angle, running = 0, 0.0, True
    outputs.select(mode)
    print("VirtualWheel Integrated Application")
    print("1 Keyboard | 2 vJoy | 3 Serial | 0 Off | E enable | Q quit")

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
                    elif event.key in (pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3):
                        mode_index = int(event.unicode)
                        mode = modes[mode_index]
                        enabled = False
                        outputs.select(mode)

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
            outputs.send(mode, angle, action, enabled and active)

            screen.fill((12, 14, 18))
            draw_text(screen, title_font, "VirtualWheel - Integrated Application", (20, 24), (80, 200, 255))
            draw_camera(screen, frame)
            draw_wheel(screen, 0.0 if angle is None else angle)
            draw_text(screen, body_font, "Camera feed", (20, 72), (180, 185, 195))
            draw_text(screen, body_font, "Virtual wheel", (755, 72), (180, 185, 195))
            info_x, info_y = 700, 585
            color = (80, 230, 130) if active else (240, 90, 90)
            angle_text = "--" if angle is None else f"{angle:+.1f} deg"
            draw_text(screen, body_font, f"Steering: {angle_text}", (info_x, info_y))
            draw_text(screen, body_font, f"Direction: {direction_for(angle)}", (info_x, info_y + 29), color)
            draw_text(screen, body_font, f"Throttle: {action or 'NEUTRAL'}", (info_x, info_y + 58), color)
            draw_text(screen, body_font, f"Mode: {mode} ({'ON' if enabled else 'OFF'})", (info_x, info_y + 87), (255, 210, 80))
            draw_text(screen, small_font, "0 Off  1 Keyboard  2 vJoy  3 Serial  E enable  Q quit", (20, 625), (210, 210, 215))
            draw_text(screen, small_font, outputs.status, (700, 440), (210, 210, 215))
            pygame.display.flip()
            clock.tick(30)
    finally:
        outputs.close_devices()
        camera.release()
        tracker.close()
        pygame.quit()
        cv2.destroyAllWindows()
        print("All outputs neutralized. Cleanup complete!")


if __name__ == "__main__":
    main()
