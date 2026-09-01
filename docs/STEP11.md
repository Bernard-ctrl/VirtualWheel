# Step 11: Integrated Application

Step 11 combines tracking, filtering, the virtual wheel, and output modes in a
single application.

## Run

```powershell
.\.venv\Scripts\Activate.ps1
python src\virtual_wheel_app.py
```

## Controls

- `0`: disable all output
- `1`: keyboard output
- `2`: vJoy output
- `3`: serial output
- `E`: enable or disable the selected output
- `Q`: quit

Output is disabled whenever the mode changes. Select the mode, enable it with
`E`, and then focus the intended target application if using keyboard or vJoy.

## Output mappings

- Keyboard: steering arrows, Up/Down throttle and brake.
- vJoy: X axis steering, Y axis throttle/brake.
- Serial: `STEER:<degrees>;THROTTLE:<action>` at the configured COM port.

The application uses the shared Step 5 settings, including smoothing,
sensitivity, dead zone, and inversion. It also uses an 8-frame tracking grace
period and sends neutral output after prolonged tracking loss or shutdown.

## Configuration

- Steering settings: `src/step5_steering_filter.py`
- vJoy device ID: `src/step8_virtual_gamepad.py`
- Serial port and baud rate: `src/step10_serial_output.py`

This is the main integrated application; the earlier step scripts remain useful
for isolated testing and troubleshooting.
