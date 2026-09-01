# Step 1: Webcam + Hand Detection

## Overview
This is the foundational step of the VirtualWheel project. We create a basic Python program that:
- Opens the webcam
- Detects both hands using MediaPipe Hands
- Draws hand landmarks in real-time
- Displays the camera feed
- Shows whether 0, 1, or 2 hands are detected

## Project Structure
```
VirtualWheel/
├── src/
│   └── step1_hand_detection.py
├── config/
├── docs/
│   └── STEP1.md (this file)
├── requirements.txt
├── PROMPT.md
└── README.md
```

## Required Python Packages
- **opencv-python** (4.8.1.78): Computer vision library for webcam capture and image processing
- **mediapipe** (0.10.8): Hand detection and landmark tracking
- **numpy** (1.24.3): Numerical computing (used by MediaPipe and OpenCV)

## Installation & Setup

### 1. Install Python (if not already installed)
- Download Python 3.8+ from https://www.python.org/
- Ensure pip is installed

### 2. Create a Virtual Environment (Recommended)
```bash
cd c:\Users\kenny\github\VirtualWheel
python -m venv venv
venv\Scripts\activate
```

### 3. Install Required Packages
```bash
pip install -r requirements.txt
```

**What this installs:**
- `opencv-python`: Handles webcam feed capture and real-time video processing
- `mediapipe`: Detects hands and provides 21 landmark points per hand
- `numpy`: Used for mathematical operations

## How to Run

### 1. Activate Virtual Environment
```bash
venv\Scripts\activate
```

### 2. Run the Program
```bash
python src/step1_hand_detection.py
```

### 3. Interact with the Program
- Position your hands in front of the webcam
- You should see:
  - Your hands drawn with landmark points
  - Number of hands detected (0/1/2)
  - Hand labels (Left/Right) with confidence scores
  - System status (ACTIVE/WAITING)
  - Frame counter
- Press **q** to quit

## Code Explanation

### HandDetector Class
The `HandDetector` class encapsulates all hand detection functionality:

#### `__init__`
- Initializes MediaPipe Hands detector
- Sets parameters:
  - `max_num_hands=2`: Detects up to 2 hands
  - `min_detection_confidence=0.7`: Hand must be 70% confident
  - `min_tracking_confidence=0.5`: After detection, track with 50% confidence

#### `detect_hands(frame)`
- Accepts frame in BGR format (OpenCV default)
- Converts to RGB (MediaPipe requirement)
- Returns detection results and RGB frame

#### `draw_landmarks(frame, results)`
- Draws hand landmarks and connections
- Uses MediaPipe's built-in drawing utilities
- Returns annotated frame

#### `get_hand_count(results)`
- Returns 0, 1, or 2 (number of hands detected)

#### `get_hand_info(results)`
- Returns list of tuples: (hand_label, confidence)
- Labels are 'Left' or 'Right'

### Main Loop
The main function:
1. Initializes hand detector
2. Opens webcam (ID 0 = default webcam)
3. Continuously:
   - Reads frames from webcam
   - Detects hands
   - Draws landmarks
   - Displays text information
   - Shows frame in window
   - Checks for 'q' key to quit

## Expected Output

When you run the program, you should see:
1. A window titled "Hand Detection - Step 1"
2. Your webcam feed in real-time
3. Hand landmarks drawn as circles (joints) and lines (connections)
4. Text displaying:
   - "Hands Detected: 0/2", "1/2", or "2/2"
   - Hand labels ("Left Hand" or "Right Hand") with confidence scores
   - Status: "ACTIVE" (green) when hands detected, "WAITING" (red) when no hands
   - Frame counter

### Sample Output
```
Hand Detection - Step 1
Hands Detected: 2/2
Left Hand: 0.98 confidence
Right Hand: 0.95 confidence
Status: ACTIVE
Frame: 245
```

## MediaPipe Hand Landmarks
Each detected hand provides 21 landmark points:

| # | Landmark | Location |
|---|----------|----------|
| 0 | WRIST | Wrist |
| 1-4 | THUMB | Thumb (4 points) |
| 5-8 | INDEX | Index finger (4 points) |
| 9-12 | MIDDLE | Middle finger (4 points) |
| 13-16 | RING | Ring finger (4 points) |
| 17-20 | PINKY | Pinky finger (4 points) |

Each landmark has: x, y, z coordinates (normalized 0-1) and visibility score

## Common Errors & Solutions

### Error: "Cannot open webcam!"
**Cause**: Webcam not connected or in use by another application

**Solutions**:
- Check if webcam is connected
- Close other applications using webcam (Zoom, Teams, etc.)
- Try camera device ID 1 or 2 instead of 0:
  ```python
  cap = cv2.VideoCapture(1)  # Try different ID
  ```

### Error: "No module named 'mediapipe'"
**Cause**: MediaPipe not installed

**Solution**: Install packages again
```bash
pip install -r requirements.txt
```

### Hands Not Detected
**Causes**: 
- Poor lighting
- Hands too far from camera
- Hand position too unclear
- Confidence threshold too high

**Solutions**:
- Improve lighting
- Move hands closer to camera
- Keep hands clear and open
- Adjust `min_detection_confidence` in HandDetector (lower value = more sensitive)

### Unstable Hand Detection
**Cause**: Tracking confidence is low

**Solution**: Increase minimum tracking confidence in `__init__`:
```python
min_tracking_confidence=0.7  # Increase from 0.5
```

### Low FPS (Slow Video)
**Cause**: Computer is slow or webcam resolution is high

**Solutions**:
- Reduce frame resolution in OpenCV
- Close other applications
- Lower detection confidence threshold

## Testing Instructions

### Test 1: Single Hand Detection
1. Show only your left hand
2. Verify "Hands Detected: 1/2"
3. Verify label shows "Left Hand"
4. Repeat with right hand only

### Test 2: Both Hands Detection
1. Show both hands
2. Verify "Hands Detected: 2/2"
3. Verify both hands labeled correctly

### Test 3: Dynamic Hand Position
1. Move hands around
2. Move hands closer/farther
3. Rotate hands
4. Verify landmarks track smoothly

### Test 4: Hand Removal
1. Start with hands visible
2. Slowly remove one hand
3. Verify detection changes from 2 to 1 to 0

### Test 5: Low Light Condition
1. Dim the lights
2. Check if hands still detected
3. Note any decrease in confidence

## Performance Notes
- Target FPS: 30+ (shown in frame counter)
- MediaPipe Hands is optimized for real-time use
- Typical latency: <100ms on modern hardware
- GPU acceleration: Supported (automatic with CUDA/Metal)

## Next Steps
After verifying this step works:
1. Proceed to **Step 2: Two-Hand Tracking**
2. In Step 2, we'll extract exact hand positions and coordinates
3. We'll prepare for steering angle calculation

## Files in This Step
- `src/step1_hand_detection.py`: Main hand detection program
- `docs/STEP1.md`: This documentation

## Additional Resources
- MediaPipe Documentation: https://google.github.io/mediapipe/
- OpenCV Documentation: https://docs.opencv.org/
- Hand Landmarks: https://google.github.io/mediapipe/solutions/hands

## Notes
- This step focuses on detection and visualization
- No steering calculations yet
- No output modes yet
- Just raw hand detection and display
