"""Step 2: Two-Hand Tracking."""

import sys
from typing import Dict, Optional, Tuple

import cv2
import mediapipe as mp
import numpy as np

Point = Tuple[float, float]


class TwoHandTracker:
    """Detect hands and expose coordinates needed by later steps."""

    def __init__(self) -> None:
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            model_complexity=0,
            min_detection_confidence=0.55,
            min_tracking_confidence=0.5,
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_styles = mp.solutions.drawing_styles

    def process(self, frame: np.ndarray):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb.flags.writeable = False
        results = self.hands.process(rgb)
        rgb.flags.writeable = True
        return results

    @staticmethod
    def _palm_center(landmarks) -> Point:
        # Wrist plus the four finger MCP joints gives a stable palm reference.
        indices = (0, 5, 9, 13, 17)
        return (
            sum(landmarks.landmark[i].x for i in indices) / len(indices),
            sum(landmarks.landmark[i].y for i in indices) / len(indices),
        )

    def get_hand_data(self, results, shape) -> Dict[str, Dict[str, Point]]:
        """Return normalized and pixel wrist/palm coordinates by hand label."""
        height, width = shape[:2]
        data: Dict[str, Dict[str, Point]] = {}
        if not results.multi_hand_landmarks:
            return data

        for index, landmarks in enumerate(results.multi_hand_landmarks):
            label = "Hand"
            if results.multi_handedness and index < len(results.multi_handedness):
                label = results.multi_handedness[index].classification[0].label

            wrist = landmarks.landmark[0]
            thumb_tip = landmarks.landmark[4]
            thumb_mcp = landmarks.landmark[2]
            palm = self._palm_center(landmarks)
            data[label] = {
                "wrist_normalized": (wrist.x, wrist.y),
                "palm_normalized": palm,
                "wrist_pixels": (wrist.x * width, wrist.y * height),
                "palm_pixels": (palm[0] * width, palm[1] * height),
                "thumb_tip_normalized": (thumb_tip.x, thumb_tip.y),
                "thumb_mcp_normalized": (thumb_mcp.x, thumb_mcp.y),
            }
        return data

    def draw(self, frame: np.ndarray, results) -> np.ndarray:
        if results.multi_hand_landmarks:
            for landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame,
                    landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_styles.get_default_hand_landmarks_style(),
                    self.mp_styles.get_default_hand_connections_style(),
                )
        return frame

    @staticmethod
    def distance_between_hands(data: Dict[str, Dict[str, Point]]) -> Optional[float]:
        if "Left" not in data or "Right" not in data:
            return None
        left = np.array(data["Left"]["palm_pixels"])
        right = np.array(data["Right"]["palm_pixels"])
        return float(np.linalg.norm(right - left))

    def close(self) -> None:
        self.hands.close()


def text(frame, value: str, position, color=(0, 255, 0)) -> None:
    cv2.putText(frame, value, position, cv2.FONT_HERSHEY_SIMPLEX, 0.58,
                color, 2, cv2.LINE_AA)


def main() -> None:
    tracker = TwoHandTracker()
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("ERROR: Cannot open webcam. Try camera index 1.")
        tracker.close()
        sys.exit(1)

    frame_count = 0
    print("Two-Hand Tracking System - Step 2")
    print("Press 'q' to quit")
    try:
        while True:
            ok, frame = camera.read()
            if not ok:
                print("ERROR: Failed to read frame from webcam!")
                break

            frame_count += 1
            results = tracker.process(frame)
            tracker.draw(frame, results)
            data = tracker.get_hand_data(results, frame.shape)
            distance = tracker.distance_between_hands(data)

            text(frame, "Two-Hand Tracking - Step 2", (10, 30))
            text(frame, f"Hands Detected: {len(data)}/2", (10, 58))
            y = 90
            for label in ("Left", "Right"):
                if label not in data:
                    text(frame, f"{label}: not detected", (10, y), (0, 0, 255))
                    y += 54
                    continue
                item = data[label]
                px, py = item["palm_pixels"]
                nx, ny = item["palm_normalized"]
                wx, wy = item["wrist_pixels"]
                text(frame, f"{label}: palm px=({px:.0f}, {py:.0f})", (10, y))
                text(frame, f"  normalized=({nx:.3f}, {ny:.3f})", (10, y + 24))
                cv2.circle(frame, (int(px), int(py)), 8, (255, 0, 255), -1)
                cv2.line(frame, (int(wx), int(wy)), (int(px), int(py)), (255, 255, 0), 2)
                y += 54

            if distance is None:
                text(frame, "Palm distance: unavailable", (10, y), (0, 0, 255))
            else:
                text(frame, f"Palm distance: {distance:.1f} px", (10, y))
            text(frame, f"Frame: {frame_count}", (10, y + 30), (200, 200, 200))
            cv2.imshow("Two-Hand Tracking - Step 2", frame)
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
