# Step 4: Center Calibration and Angle Unwrapping

## Goal

Step 4 lets the user define the neutral hand position and reports steering
relative to that center. It also removes the apparent jump at the `-180` / `+180`
degree boundary.

## Run

```powershell
.\.venv\Scripts\Activate.ps1
python src\step4_calibrated_steering.py
```

Controls:

- `C`: calibrate the current two-hand position as center
- `R`: reset calibration and angle history
- `Q`: quit

## Why angles appeared to reverse

`atan2` conventionally returns values only from `-180` through `+180` degrees.
For example, a continuous left turn can produce:

```text
-170, -179, +179, +170
```

The `+179` value is mathematically equivalent to `-181`, but displaying it as
`+179` makes the steering appear to jump to the opposite direction.

The `ContinuousAngle` class compares each new raw angle with the previous one
and adds or subtracts `360` degrees so the smallest frame-to-frame change is
chosen. The resulting sequence becomes continuous:

```text
-170, -179, -181, -190
```

## Important limitation

Two palm points define a line, so the visual hand arrangement has an inherent
180-degree ambiguity if the hands cross or MediaPipe swaps their labels. Angle
unwrapping handles the normal frame-boundary problem while tracking remains
continuous, but it cannot infer a full rotation after tracking is lost or hand
labels change. A future integrated version should detect label swaps and pause
output until tracking is stable again.

## Testing

1. Hold both hands in a neutral horizontal position and press `C`.
2. Tilt the right hand upward and confirm a positive angle.
3. Tilt the left hand upward and confirm a negative angle.
4. Rotate continuously through the `180` degree boundary and confirm there is
   no sudden sign reversal.
5. Remove a hand and confirm the display pauses safely.
