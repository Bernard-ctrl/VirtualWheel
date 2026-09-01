# Test Racing Game

This is a simple local game for testing Step 7 keyboard steering and Step 8
vJoy gamepad steering. It requires no image or sound assets.

## Run

```powershell
.\.venv\Scripts\Activate.ps1
python src\test_racing_game.py
```

Use the left and right arrow keys to move the car. Hold the Up arrow to
accelerate and the Down arrow to brake. A connected joystick's X axis controls
steering and Y axis controls throttle/brake. Avoid the red obstacles.
Press `R` after a crash to restart, or `Esc` to quit.

## Test with VirtualWheel

1. Start the test racing game.
2. Start Step 7 in a second terminal:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   python src\step7_keyboard_output.py
   ```

3. Press `E` while the Step 7 window is focused to enable output.
4. Click the racing game window so it is focused.
5. Steer with both hands. The car should move left and right continuously.

The test game reads both arrow-key state and joystick axes. For vJoy testing,
check the terminal for `Joystick selected: vJoy`, then let Step 8 drive the X/Y
axes. The game window also displays the current X/Y values.
