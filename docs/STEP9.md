# Step 9: Browser Game Testing

Browser games use the browser Gamepad API. This step provides a local page to
verify whether the browser can see vJoy before testing an online game.

## Start the test page

From the project directory:

```powershell
python -m http.server 8000 --directory web
```

Open [http://localhost:8000/gamepad_test.html](http://localhost:8000/gamepad_test.html)
in the browser.

## Test procedure

1. Start the browser test page.
2. Start `src\step8_virtual_gamepad.py`.
3. Press `E` in the Step 8 window.
4. Return to the browser test page and click it once.
5. Move your hands.
6. Confirm the X value changes with steering and Y changes with thumb
   acceleration/braking.

## Interpreting the result

- If X/Y move on this page, the browser sees vJoy and a browser game may be
  usable after binding its controller settings.
- If `joy.cpl` moves but this page does not, the browser is not exposing the
  vJoy DirectInput device through its Gamepad API.
- If this page moves but a specific game does not, that game may require
  keyboard input, XInput, or its own controller mapping.

Browser gamepad support depends on the browser and game. The local page is a
diagnostic tool, not a racing game itself.
