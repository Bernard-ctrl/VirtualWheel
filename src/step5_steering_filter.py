"""Step 5: Smooth and constrain the steering signal without calibration."""

import sys
from typing import Optional

import cv2

from step2_two_hand_tracking import TwoHandTracker
from step3_steering_calculation import calculate_steering_angle, direction_for
from step4_calibrated_steering import ContinuousAngle


# These settings are intentionally easy to change while tuning the system.
SMOOTHING = 0.65       # Lower = smoother, higher = more responsive
DEAD_ZONE_DEGREES = 5.0  # Small neutral range for imperfect hand alignment
SENSITIVITY = 2.0
MAX_STEERING_DEGREES = 180.0
INVERT_STEERING = False


class ExponentialSmoother:
    """Low-cost exponential moving average for real-time steering."""

    def __init__(self, factor: float) -> None:
        if not 0.0 < factor <= 1.0:
            raise ValueError("smoothing factor must be greater than 0 and at most 1")
        self.factor = factor
        self.value: Optional[float] = None

    def update(self, value: Optional[float]) -> Optional[float]:
        if value is None:
            self.value = None
            return None
        if self.value is None:
            self.value = value
        else:
            self.value += self.factor * (value - self.value)
        return self.value


def apply_steering_settings(angle: Optional[float]) -> Optional[float]:
    """Apply sensitivity, dead zone, inversion, and maximum output limit."""
    if angle is None:
        return None

    adjusted = angle * SENSITIVITY
    if abs(adjusted) <= DEAD_ZONE_DEGREES:
        adjusted = 0.0
    elif adjusted > 0:
        adjusted -= DEAD_ZONE_DEGREES
    else:
        adjusted += DEAD_ZONE_DEGREES

    if INVERT_STEERING:
        adjusted = -adjusted
    return max(-MAX_STEERING_DEGREES, min(MAX_STEERING_DEGREES, adjusted))


def main() -> None:
    tracker = TwoHandTracker()
    continuous = ContinuousAngle()
    smoother = ExponentialSmoother(SMOOTHING)
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("ERROR: Cannot open webcam. Try camera index 1.")
        tracker.close()
        sys.exit(1)

    print("Filtered Steering System - Step 5")
    print("Edit the settings at the top of this file to tune response")
    print("Press 'q' to quit")

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
            continuous_angle = continuous.update(raw_angle)
            smoothed_angle = smoother.update(continuous_angle)
            output_angle = apply_steering_settings(smoothed_angle)
            direction = direction_for(output_angle)
            color = (0, 255, 0) if output_angle is not None else (0, 0, 255)

            if "Left" in data and "Right" in data:
                left = data["Left"]["palm_pixels"]
                right = data["Right"]["palm_pixels"]
                cv2.line(frame, (int(left[0]), int(left[1])),
                          (int(right[0]), int(right[1])), (255, 0, 255), 3)

            def show(label: str, value: str, y: int, text_color=color) -> None:
                cv2.putText(frame, f"{label}: {value}", (10, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.65, text_color, 2, cv2.LINE_AA)

            show("Filtered Steering - Step 5", "", 30)
            show("Hands", f"{len(data)}/2", 62)
            show("Raw angle", "--" if raw_angle is None else f"{raw_angle:+.1f} deg", 96)
            show("Smoothed", "--" if smoothed_angle is None else f"{smoothed_angle:+.1f} deg", 130)
            show("Output", "--" if output_angle is None else f"{output_angle:+.1f} deg", 164)
            show("Direction", direction, 198)
            show("Settings", f"dead zone {DEAD_ZONE_DEGREES:g} deg, sensitivity {SENSITIVITY:g}", 232,
                 (220, 220, 220))
            show("Status", "ACTIVE" if len(data) == 2 else "PAUSED", 266, color)

            cv2.imshow("Filtered Steering - Step 5", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        camera.release()
        cv2.destroyAllWindows()
        tracker.close()
        print("Cleanup complete!")


if __name__ == "__main__":
    main()
