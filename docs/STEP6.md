# Step 6: Virtual Steering Wheel

Step 6 adds a Pygame interface with the webcam feed on the left and a virtual
steering wheel on the right. The wheel rotates using the filtered hand angle.

## Run

```powershell
.\.venv\Scripts\Activate.ps1
python src\step6_virtual_wheel.py
```

Press `Q` or close the Pygame window to quit.

The interface shows the camera feed, landmarks, virtual wheel, steering angle,
direction, hand count, and active/paused status. If either hand is lost, the
wheel holds its last value briefly while tracking recovers. After 8 missed
frames, it returns visually to center and status becomes `PAUSED`.

This step is visual only; it does not send keyboard, gamepad, or serial input.
Smoothing settings remain in `src/step5_steering_filter.py`.

## Testing

1. Start with both hands visible and verify `ACTIVE`.
2. Tilt the hands left and right and verify the wheel follows smoothly.
3. Remove one hand and verify `PAUSED`.
4. Close the window and verify the webcam is released cleanly.
