# VirtualWheel

Vision-based virtual steering wheel using real-time hand gesture recognition.
VirtualWheel uses a webcam to track two hands, calculate steering movement,
display a virtual wheel, and optionally send keyboard, vJoy, or serial output.

## Features

- Real-time two-hand tracking with MediaPipe Hands
- Signed steering-angle calculation with 180-degree boundary handling
- Configurable smoothing, dead zone, sensitivity, maximum angle, and inversion
- Virtual steering-wheel display with webcam feed
- Keyboard steering and thumb-based throttle/brake output
- Optional vJoy analog steering and throttle/brake output
- Optional Arduino/ESP32 serial output
- Hands-off safety pause and neutral output on shutdown
- Local Pygame racing game and browser Gamepad API test page

## Requirements

- Windows 10 or 11
- Python 3.12 recommended
- Webcam
- Optional: vJoy for analog gamepad output
- Optional: Arduino or ESP32 for serial output

## Installation

Open PowerShell in the project directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
```

MediaPipe is pinned to the legacy-compatible `0.10.21` release and NumPy is
kept below version 2 because the source uses the MediaPipe Solutions API.

## Start the integrated application

```powershell
.\.venv\Scripts\Activate.ps1
python src\virtual_wheel_app.py
```

Controls:

- `0`: disable output
- `1`: keyboard output
- `2`: vJoy output
- `3`: serial output
- `E`: enable or disable the selected output
- `Q`: quit

Output starts disabled. Select a mode, press `E`, and then focus the target
game if using keyboard or vJoy output.

## Input mappings

The angle between the left and right palm centers controls steering. Negative
angles steer left and positive angles steer right. The right thumb controls
throttle: thumb up accelerates, thumb down brakes, and neutral releases output.

## Output modes

### Keyboard

Step 7 sends Left/Right arrows for steering and Up/Down arrows for acceleration
and braking. This works with games that accept keyboard input, but is digital
rather than analog.

### vJoy

Step 8 sends analog steering to vJoy X and throttle/brake to vJoy Y. Configure
one enabled vJoy device with X and Y axes, verify output in `joy.cpl`, and bind
the axes inside the game. vJoy is DirectInput and may not work with games that
require XInput.

### Serial

Step 10 sends messages such as:

```text
STEER:32.5;THROTTLE:ACCELERATE
```

Configure `SERIAL_PORT` and `BAUD_RATE` in
`src/step10_serial_output.py`. An Arduino receiver example is available at
`arduino/virtualwheel_receiver/virtualwheel_receiver.ino`.

### Browser games

Browser Gamepad API support for vJoy varies. Test it with:

```powershell
python -m http.server 8000 --directory web
```

Open `http://localhost:8000/gamepad_test.html`. If vJoy is not detected in the
browser while it works in `joy.cpl`, use keyboard output for browser games.

## Development steps

| Step | File | Purpose |
|---|---|---|
| 1 | `src/step1_hand_detection.py` | Webcam and hand landmarks |
| 2 | `src/step2_two_hand_tracking.py` | Palm and wrist coordinates |
| 3 | `src/step3_steering_calculation.py` | Raw steering angle |
| 4 | `src/step4_calibrated_steering.py` | Optional calibration and unwrapping |
| 5 | `src/step5_steering_filter.py` | Smoothing and steering settings |
| 6 | `src/step6_virtual_wheel.py` | Pygame virtual wheel |
| 7 | `src/step7_keyboard_output.py` | Keyboard output |
| 8 | `src/step8_virtual_gamepad.py` | vJoy analog output |
| 9 | `web/gamepad_test.html` | Browser gamepad test |
| 10 | `src/step10_serial_output.py` | Arduino/ESP32 serial output |
| 11 | `src/virtual_wheel_app.py` | Integrated application |
| 12 | `docs/STEP12.md` | Testing and troubleshooting |

## Local test racing game

The project includes an asset-free Pygame racing game that reads keyboard input
and joystick axes:

```powershell
python src\test_racing_game.py
```

It uses joystick X for steering and Y for throttle/brake. The terminal reports
the selected joystick and the game window displays live axis values.

## Tuning

Edit the settings at the top of `src/step5_steering_filter.py`:

```python
SMOOTHING = 0.65
DEAD_ZONE_DEGREES = 5.0
SENSITIVITY = 2.0
MAX_STEERING_DEGREES = 180.0
INVERT_STEERING = False
```

Increase `SMOOTHING` for faster response, increase the dead zone if straight
position is unstable, increase sensitivity for stronger steering, and enable
inversion if left and right are reversed.

## Project structure

```text
VirtualWheel/
├── arduino/virtualwheel_receiver/virtualwheel_receiver.ino
├── docs/                         # Step and testing documentation
├── src/                          # Tracking, outputs, and test game
├── web/gamepad_test.html         # Browser Gamepad API test
├── requirements.txt
└── README.md
```

## Troubleshooting

- **Cannot open webcam:** close other camera applications or try camera index
  `1`.
- **Brief pauses:** improve lighting, reduce motion blur, or adjust the grace
  period.
- **Keyboard output does nothing:** press `E`, then focus the target game.
- **vJoy missing in `joy.cpl`:** enable device 1 and its X/Y axes.
- **vJoy works in `joy.cpl` but not in a game:** bind axes manually; the game
  may require XInput instead of DirectInput.
- **Serial port error:** set the correct COM port and close Serial Monitor.
- **MediaPipe import error:** activate `.venv` and reinstall requirements.

## Safety and limitations

- Keyboard output starts disabled in the integrated application.
- Outputs become neutral after prolonged tracking loss and on shutdown.
- Keyboard steering is digital; vJoy is required for analog steering.
- Browser and game compatibility depends on the target application's input API.
- Fast movement, poor lighting, occlusion, and hand-label swaps can reduce
  tracking reliability.
- Two hand points have an inherent 180-degree ambiguity when hands cross or
  tracking is interrupted.
