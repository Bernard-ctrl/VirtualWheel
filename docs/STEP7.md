# Step 7: Keyboard Output

Step 7 maps steering direction to the Windows left and right arrow keys for
games that accept keyboard steering. Output is disabled by default.

## Run

```powershell
.\.venv\Scripts\Activate.ps1
python src\step7_keyboard_output.py
```

- Press `E` to enable or disable keyboard output.
- Press `Q` to quit.

Enable output only after the intended racing game is focused. The script
releases held keys during cleanup. A short 8-frame grace period prevents
motion-blurred frames from repeatedly toggling the game input.

Small movements beyond the `1.5` degree keyboard threshold activate the
corresponding arrow key. While steering continues in one direction, the program emits repeated key-down
events on each camera frame so applications continue moving instead of
receiving only one arrow-key action.

This mode is digital left/right input, not analog steering. The game must
accept Windows arrow keys. Analog gamepad output is planned for a later step.

The right thumb also controls throttle:

- Thumb up: hold the Up arrow to accelerate.
- Thumb down: hold the Down arrow to brake.
- Thumb neutral, unavailable, or uncertain: release both keys.
