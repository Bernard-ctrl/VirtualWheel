"""Step 4: Calibrated steering with continuous-angle unwrapping."""

import sys
from typing import Optional

import cv2

from step2_two_hand_tracking import TwoHandTracker
from step3_steering_calculation import calculate_steering_angle, direction_for


class ContinuousAngle:
    """Prevent atan2's -180/+180 boundary from causing a steering jump."""

    def __init__(self) -> None:
        self.previous_raw: Optional[float] = None
        self.value: Optional[float] = None

    def update(self, raw_angle: Optional[float]) -> Optional[float]:
        if raw_angle is None:
            # Reinitialize on the next valid frame after tracking is lost.
            self.previous_raw = None
            return None

        if self.previous_raw is None or self.value is None:
            self.previous_raw = raw_angle
            self.value = raw_angle
            return self.value

        # Choose the equivalent angle closest to the previous frame.
        delta = (raw_angle - self.previous_raw + 180.0) % 360.0 - 180.0
        self.value += delta
        self.previous_raw = raw_angle
        return self.value

    def reset(self) -> None:
        self.previous_raw = None
        self.value = None


def main() -> None:
    tracker = TwoHandTracker()
    angle_tracker = ContinuousAngle()
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("ERROR: Cannot open webcam. Try camera index 1.")
        tracker.close()
        sys.exit(1)

    center_angle: Optional[float] = None
    print("Calibrated Steering System - Step 4")
    print("Hold a neutral hand position and press 'c' to calibrate center")
    print("Press 'r' to reset calibration, or 'q' to quit")

    try:
        while True:
            ok, frame = camera.read()
            if not ok:
                print("ERROR: Failed to read frame from webcam!")
                break

            results = tracker.process(frame)
            tracker.draw(frame, results)
            data = tracker.get_hand_data(results, frame.shape)
            raw_angle = calculate_steering_angle(data)
            continuous_angle = angle_tracker.update(raw_angle)
            relative_angle = (
                None
                if continuous_angle is None or center_angle is None
                else continuous_angle - center_angle
            )
            direction = direction_for(relative_angle)
            hand_count = len(data)
            status_color = (0, 255, 0) if hand_count == 2 else (0, 0, 255)

            if "Left" in data and "Right" in data:
                left = data["Left"]["palm_pixels"]
                right = data["Right"]["palm_pixels"]
                cv2.line(frame, (int(left[0]), int(left[1])),
                          (int(right[0]), int(right[1])), (255, 0, 255), 3)

            cv2.putText(frame, "Calibrated Steering - Step 4", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2, cv2.LINE_AA)
            cv2.putText(frame, f"Hands Detected: {hand_count}/2", (10, 62),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, status_color, 2, cv2.LINE_AA)
            angle_text = "--" if relative_angle is None else f"{relative_angle:+.1f} deg"
            cv2.putText(frame, f"Steering Angle: {angle_text}", (10, 96),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2, cv2.LINE_AA)
            cv2.putText(frame, f"Direction: {direction}", (10, 130),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2, cv2.LINE_AA)
            center_text = "NOT CALIBRATED" if center_angle is None else f"{center_angle:+.1f} deg"
            cv2.putText(frame, f"Center: {center_text}", (10, 164),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(frame, "C: calibrate   R: reset   Q: quit", (10, 198),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (220, 220, 220), 1, cv2.LINE_AA)

            cv2.imshow("Calibrated Steering - Step 4", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("c") and continuous_angle is not None:
                center_angle = continuous_angle
                print(f"Center calibrated at {center_angle:+.1f} degrees")
            elif key == ord("r"):
                center_angle = None
                angle_tracker.reset()
                print("Calibration reset")
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        camera.release()
        cv2.destroyAllWindows()
        tracker.close()
        print("Cleanup complete!")


if __name__ == "__main__":
    main()
