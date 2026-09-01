"""
Step 1: Webcam + Hand Detection
Basic Python program that:
- Opens the webcam
- Detects both hands using MediaPipe
- Draws hand landmarks
- Displays the camera feed
- Shows whether one or two hands are detected
"""

import cv2
import mediapipe as mp
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import sys
import numpy as np

class HandDetector:
    """
    A class to detect hands in webcam feed using MediaPipe Hands.
    """
    
    def __init__(self):
        """Initialize MediaPipe Hands detector."""
        self.mp_hands = solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,  # Detect up to 2 hands
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = solutions.drawing_utils
    
    def detect_hands(self, frame):
        """
        Detect hands in the given frame.
        
        Args:
            frame: Input frame from webcam (BGR format from OpenCV)
        
        Returns:
            results: MediaPipe detection results
            frame_rgb: RGB version of frame (required by MediaPipe)
        """
        # Convert BGR to RGB (MediaPipe expects RGB)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        return results, frame_rgb
    
    def draw_landmarks(self, frame, results):
        """
        Draw hand landmarks on the frame.
        
        Args:
            frame: Input frame (BGR format)
            results: MediaPipe detection results
        
        Returns:
            frame: Frame with drawn landmarks
        """
        if results.multi_hand_landmarks and results.multi_handedness:
            h, w, c = frame.shape
            for hand_landmarks in results.multi_hand_landmarks:
                # Convert landmarks to pixels
                for landmark in hand_landmarks.landmark:
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)
                    cv2.circle(frame, (x, y), 4, (0, 255, 0), -1)
                
                # Draw connections
                for connection in self.mp_hands.HAND_CONNECTIONS:
                    start_idx, end_idx = connection
                    start = hand_landmarks.landmark[start_idx]
                    end = hand_landmarks.landmark[end_idx]
                    
                    start_x = int(start.x * w)
                    start_y = int(start.y * h)
                    end_x = int(end.x * w)
                    end_y = int(end.y * h)
                    
                    cv2.line(frame, (start_x, start_y), (end_x, end_y), (0, 0, 255), 2)
        
        return frame
    
    def get_hand_count(self, results):
        """
        Get the number of hands detected.
        
        Args:
            results: MediaPipe detection results
        
        Returns:
            int: Number of hands detected (0, 1, or 2)
        """
        if results.multi_hand_landmarks:
            return len(results.multi_hand_landmarks)
        return 0
    
    def get_hand_info(self, results):
        """
        Get information about detected hands.
        
        Args:
            results: MediaPipe detection results
        
        Returns:
            list: List of tuples (hand_label, confidence)
        """
        hand_info = []
        if results.multi_handedness:
            for handedness in results.multi_handedness:
                label = handedness.classification[0].label  # 'Left' or 'Right'
                confidence = handedness.classification[0].score
                hand_info.append((label, confidence))
        return hand_info
    
    def release(self):
        """Release resources."""
        self.hands.close()


def main():
    """
    Main function to run the hand detection system.
    """
    # Initialize hand detector
    detector = HandDetector()
    
    # Open webcam
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("ERROR: Cannot open webcam!")
        sys.exit(1)
    
    print("Hand Detection System - Step 1")
    print("=" * 50)
    print("Press 'q' to quit")
    print("=" * 50)
    
    frame_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("ERROR: Failed to read frame from webcam!")
                break
            
            frame_count += 1
            
            # Detect hands
            results, frame_rgb = detector.detect_hands(frame)
            
            # Draw landmarks
            frame = detector.draw_landmarks(frame, results)
            
            # Get hand information
            hand_count = detector.get_hand_count(results)
            hand_info = detector.get_hand_info(results)
            
            # Add text information to frame
            y_offset = 30
            cv2.putText(frame, "Hand Detection - Step 1", (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            y_offset += 40
            cv2.putText(frame, f"Hands Detected: {hand_count}/2", (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            y_offset += 40
            if hand_info:
                for i, (label, confidence) in enumerate(hand_info):
                    status = f"{label} Hand: {confidence:.2f} confidence"
                    cv2.putText(frame, status, (10, y_offset), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    y_offset += 30
            
            # Add system status
            y_offset += 10
            status_text = "ACTIVE" if hand_count > 0 else "WAITING"
            status_color = (0, 255, 0) if hand_count > 0 else (0, 0, 255)
            cv2.putText(frame, f"Status: {status_text}", (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)
            
            # Add frame count (for performance monitoring)
            y_offset += 40
            cv2.putText(frame, f"Frame: {frame_count}", (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
            
            # Display frame
            cv2.imshow("Hand Detection - Step 1", frame)
            
            # Check for quit key
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("\nExiting...")
                break
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    finally:
        # Clean up
        cap.release()
        cv2.destroyAllWindows()
        detector.release()
        print("Cleanup complete!")


if __name__ == "__main__":
    main()
