# Step 10: Serial / Arduino Output

Step 10 sends steering and throttle information over USB serial to an Arduino
or ESP32.

## Configuration

Edit the constants at the top of `src/step10_serial_output.py`:

```python
SERIAL_PORT = "COM3"
BAUD_RATE = 115200
```

Find the correct COM port in Windows Device Manager. Close Arduino Serial
Monitor before running VirtualWheel because only one application can normally
open a serial port at a time.

## Run

```powershell
.\.venv\Scripts\Activate.ps1
python src\step10_serial_output.py
```

Press `E` to enable output and `Q` to quit. Output is disabled initially.

## Protocol

Each message is ASCII text terminated by a newline:

```text
STEER:32.5;THROTTLE:ACCELERATE
```

Possible throttle values are `ACCELERATE`, `BRAKE`, and `NEUTRAL`. Steering is
the filtered angle in degrees. When tracking is unsafe or the program exits,
the sender transmits `STEER:0.0;THROTTLE:NEUTRAL`.

An example receiver is in
`arduino/virtualwheel_receiver/virtualwheel_receiver.ino`.

## Testing

1. Upload the Arduino example.
2. Set the correct `SERIAL_PORT`.
3. Open the Arduino Serial Monitor first to confirm messages, then close it.
4. Run the Python script and press `E`.
5. Observe parsed steering and throttle values in the Arduino Serial Monitor
   or use the values to drive hardware.
