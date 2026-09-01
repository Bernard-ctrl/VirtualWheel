"""Step 3: Calculate a signed steering angle from two palm centers."""

import math
import sys
from typing import Dict, Optional, Tuple

import cv2

from step2_two_hand_tracking import TwoHandTracker


Point = Tuple[float, float]


def calculate_steering_angle(data: Dict[str, Dict[str, Point]]) -> Optional[float]:
    """Return the hand-line angle in degrees, or None without two hands.

    The angle is measured from the horizontal line between the left and right
    palm centers. Image Y is inverted so that a right palm above the left palm
    produces a positive (right) steering angle.
    """
    if "Left" not in data or "Right" not in data:
        return None

    left_x, left_y = data["Left"]["palm_pixels"]
    right_x, right_y = data["Right"]["palm_pixels"]
    dx = right_x - left_x
    dy = left_y - right_y

    if math.isclose(dx, 0.0) and math.isclose(dy, 0.0):
        return None
    return math.degrees(math.atan2(dy, dx))


def direction_for(angle: Optional[float], threshold: float = 5.0) -> str:
    """Classify an angle as LEFT, CENTER, RIGHT, or PAUSED."""
    if angle is None:
        return "PAUSED"
    if angle > threshold:
        return "RIGHT"
    if angle < -threshold:
        return "LEFT"
    return "CENTER"


def draw_overlay(frame, angle: Optional[float], direction: str, hand_count: int) -> None:
    color = (0, 255, 0) if direction != "PAUSED" else (0, 0, 255)
    cv2.putText(frame, "Steering Calculation - Step 3", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2, cv2.LINE_AA)
    cv2.putText(frame, f"Hands Detected: {hand_count}/2", (10, 62),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2, cv2.LINE_AA)
    angle_text = "--" if angle is None else f"{angle:+.1f} deg"
    cv2.putText(frame, f"Steering Angle: {angle_text}", (10, 96),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA)
    cv2.putText(frame, f"Direction: {direction}", (10, 130),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA)


def main() -> None:
    tracker = TwoHandTracker()
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("ERROR: Cannot open webcam. Try camera index 1.")
        tracker.close()
        sys.exit(1)

    print("Steering Calculation System - Step 3")
    print("Positive angle = RIGHT, negative angle = LEFT")
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
            angle = calculate_steering_angle(data)
            direction = direction_for(angle)

            if "Left" in data and "Right" in data:
                left = data["Left"]["palm_pixels"]
                right = data["Right"]["palm_pixels"]
                cv2.line(frame, (int(left[0]), int(left[1])),
                          (int(right[0]), int(right[1])), (255, 0, 255), 3)

            draw_overlay(frame, angle, direction, len(data))
            cv2.imshow("Steering Calculation - Step 3", frame)
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
