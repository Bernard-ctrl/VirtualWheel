# Step 8: Virtual Gamepad Output

Step 8 sends analog output through a vJoy virtual joystick on Windows:

- Steering angle → vJoy X axis, centered at `16384`.
- Right thumb up → vJoy Y axis maximum (accelerate).
- Right thumb down → vJoy Y axis minimum (brake).
- Neutral or unsafe tracking state → both axes centered.

## Requirements

1. Install the vJoy driver from its official project.
2. Configure at least one vJoy device with X and Y axes.
3. Ensure the device ID is `1`, or change `VJOY_DEVICE_ID` in the script.
4. Install the project dependencies in `.venv`.

## Run

```powershell
.\.venv\Scripts\Activate.ps1
python src\step8_virtual_gamepad.py
```

Press `E` to enable or disable output and `Q` to quit. Output starts disabled.
The script centers both axes on disable, tracking loss, camera failure, and
normal exit.

## Testing

Use Windows' vJoy monitor or a compatible game to verify that the X axis moves
with steering. Verify the Y axis moves to maximum with thumb up and minimum
with thumb down. The local test racing game from
`src/test_racing_game.py` reads keyboard input, not vJoy; use a gamepad tester
for this step.

## Limitations

The exact axis mapping and throttle convention vary between games. Select the
vJoy device and map X/Y inside the game settings. vJoy must be installed and
configured separately from this Python project. The installed `pyvjoy` binding
sends each axis change directly through `set_axis`.
