# Step 12: Testing and Troubleshooting

## Recommended test order

Run tests in isolation before testing a real racing game:

1. `python src\step1_hand_detection.py` — camera and hand landmarks.
2. `python src\step2_two_hand_tracking.py` — two-hand coordinates.
3. `python src\step3_steering_calculation.py` — raw signed angle.
4. `python src\step5_steering_filter.py` — smoothing and sensitivity.
5. `python src\step6_virtual_wheel.py` — visual wheel response.
6. `python src\test_racing_game.py` — keyboard and vJoy test input.
7. `python src\virtual_wheel_app.py` — integrated output modes.

## Functional checklist

### Hand tracking

- Verify 0, 1, and 2 hands are reported correctly.
- Test both hands separately and together.
- Move quickly and confirm brief misses do not repeatedly pause the system.
- Remove both hands and confirm the system eventually becomes `PAUSED`.
- Test indoor lighting, low light, and different distances from the camera.

### Steering

- Level hands should produce an angle near zero.
- Raising the right palm should produce positive/right steering.
- Raising the left palm should produce negative/left steering.
- Test a continuous turn through the 180-degree boundary.
- Tune `SMOOTHING`, `DEAD_ZONE_DEGREES`, and `SENSITIVITY` in Step 5.

### Throttle and brake

- Right thumb up should produce acceleration.
- Right thumb down should produce braking.
- Thumb neutral or uncertain should produce neutral throttle.

### Output modes

- Keyboard: test in Notepad with existing text, then test a game.
- vJoy: verify axes in `joy.cpl` before opening a game, then bind axes in the
  game's controller settings.
- Serial: close Arduino Serial Monitor before starting Python and verify the
  documented newline-terminated messages.
- Browser: use `web\gamepad_test.html`; if vJoy is invisible, use keyboard mode.

## Troubleshooting

| Symptom | Likely cause | Action |
|---|---|---|
| No camera | Camera busy or wrong index | Close camera apps or try index `1` |
| Brief pauses | Motion blur or tracking loss | Improve lighting; adjust grace period |
| Too slow | Smoothing too strong | Increase `SMOOTHING` toward `1.0` |
| Small turns ignored | Dead zone too large | Reduce `DEAD_ZONE_DEGREES` |
| Keyboard does nothing | Output disabled or wrong focus | Press `E`, then focus target app |
| vJoy absent in `joy.cpl` | Driver/device not configured | Enable device and X/Y axes in Configure vJoy |
| `joy.cpl` works but game does not | Game needs binding or XInput | Bind vJoy axes; use keyboard or an XInput solution |
| Serial port unavailable | Wrong port or monitor open | Change `SERIAL_PORT`; close Serial Monitor |

## Safety checks

- Output starts disabled in the integrated application.
- Missing hands eventually produce neutral output.
- Keyboard keys are released during shutdown.
- vJoy axes are centered during shutdown.
- Serial output sends neutral values during shutdown.

## Known limitations

- Keyboard output is digital, not analog.
- vJoy is DirectInput and is not accepted by every modern game.
- Browser Gamepad API support for vJoy varies by browser.
- Thumb gestures can be difficult while both hands are positioned on the wheel.
- Strong motion blur can still cause tracking loss.
- Full 360-degree interpretation is ambiguous if hand labels swap or tracking
  is lost during the rotation.
