# Step 2: Two-Hand Tracking

## Goal

This step extracts coordinates for both hands and displays each hand's palm
center, wrist position, normalized coordinates, and the distance between palm
centers. These values are the inputs for steering-angle calculation.

## Setup and run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python src\step2_two_hand_tracking.py
```

Press `q` to quit.

## Coordinate definitions

- Pixel `(0, 0)` is the top-left of the camera frame.
- Normalized coordinates range approximately from `0.0` to `1.0`.
- Palm center is the average of landmarks `0, 5, 9, 13, 17`.
- Palm distance is Euclidean pixel distance between left and right palm centers.
  It is unavailable until both hands are detected.

## Testing

1. Show one hand and verify `Hands Detected: 1/2`.
2. Show both hands and verify both coordinate blocks and palm distance appear.
3. Move both hands and confirm coordinates and distance update.
4. Remove either hand and verify it changes to `not detected`.

## Common errors

- Import errors: activate `.venv` and reinstall from `requirements.txt`.
- Webcam error: close other camera applications or change camera index `0` to
  `1` in the source.
- Hand labels should be tested with the user’s camera setup before using them
  in steering calculations.
