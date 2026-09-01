# Step 3: Steering Calculation

## Goal

Step 3 calculates the signed angle of the line joining the two palm centers.
This is the first steering signal:

- Positive angle: `RIGHT`
- Negative angle: `LEFT`
- Within 5 degrees of horizontal: `CENTER`
- Fewer than two hands: `PAUSED`

The angle is calculated with `atan2`, which preserves direction and works for
both clockwise and counterclockwise hand movement.

## Run

Activate the project environment and run:

```powershell
.\.venv\Scripts\Activate.ps1
python src\step3_steering_calculation.py
```

Press `q` to quit.

## Algorithm

For the left palm `(Lx, Ly)` and right palm `(Rx, Ry)` in image pixels:

```text
dx = Rx - Lx
dy = Ly - Ry
angle = degrees(atan2(dy, dx))
```

The Y subtraction accounts for the camera image having its vertical axis
increasing downward. A perfectly horizontal hand line produces `0 degrees`.

## Testing

1. Hold both hands level and verify an angle near `0 degrees`.
2. Raise the right hand relative to the left and verify a positive angle and
   `RIGHT` direction.
3. Raise the left hand relative to the right and verify a negative angle and
   `LEFT` direction.
4. Remove one hand and verify the status becomes `PAUSED`.

## Limitation

This step reports the raw angle, so small tracking movements may cause minor
jitter. Calibration, smoothing, sensitivity, and a configurable dead zone are
added in the following steps.
