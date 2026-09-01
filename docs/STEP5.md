# Step 5: Steering Smoothing and Limits

## Goal

Step 5 keeps the accurate Step 3 angle but makes its output more usable by
reducing jitter and applying configurable limits. Center calibration is not
used.

## Run

```powershell
.\.venv\Scripts\Activate.ps1
python src\step5_steering_filter.py
```

Press `q` to quit.

## Settings

Edit the constants at the top of `src/step5_steering_filter.py`:

- `SMOOTHING`: exponential smoothing factor from `0.01` to `1.0`. Lower values
  are smoother but add more delay.
- `DEAD_ZONE_DEGREES`: small movements treated as center.
- `SENSITIVITY`: multiplies the angle before limiting it.
- `MAX_STEERING_DEGREES`: maximum magnitude of the output angle.
- `INVERT_STEERING`: reverses left and right when set to `True`.

The default configuration uses a `5` degree neutral range, `2x` sensitivity,
and `0.65` smoothing for a responsive output while still allowing slightly
imperfectly level hands.

The dead zone is removed from larger values as well, so the output starts at
zero and then responds progressively outside the dead zone.

## Processing pipeline

```text
hand landmarks
    -> raw hand-line angle
    -> continuous angle unwrapping
    -> exponential smoothing
    -> sensitivity
    -> dead zone
    -> inversion
    -> maximum-angle clamp
```

When fewer than two hands are visible, the output is cleared and the status is
`PAUSED`, preventing stale steering commands from being used later.

## Testing

1. Hold both hands steady and confirm the smoothed value moves less than the
   raw value.
2. Make small movements below the dead zone and verify output remains zero.
3. Increase `SENSITIVITY` and confirm the output responds more strongly.
4. Set `INVERT_STEERING = True` and verify left/right directions reverse.
5. Remove a hand and verify the output becomes `--` and status becomes `PAUSED`.
