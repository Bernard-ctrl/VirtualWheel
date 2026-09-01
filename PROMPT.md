AI Project Development Prompt

I want to develop a project titled “Vision-Based Virtual Steering Wheel Using Real-Time Hand Gesture Recognition.”

The project should use a webcam/camera and computer vision to detect my hands and mimic the movement of a real steering wheel without using a physical steering wheel.

1. Main Objective

Create a system where a user places both hands in front of a webcam as if holding a steering wheel.

The system should:

Detect both hands in real time.
Track the position of the hands.
Calculate their relative movement and rotation.
Convert the movement into a steering-wheel angle.
Display a virtual steering wheel that rotates according to the user's hand movement.
Convert the steering angle into an input that can be used by racing games.

The system should be designed as a general-purpose hand-controlled steering system, not for only one specific game.

2. Technologies

Use:

Python
OpenCV — webcam and image processing
MediaPipe Hands — real-time hand landmark detection
NumPy — mathematical calculations
Pygame — virtual steering-wheel visualization/interface
A suitable virtual gamepad/joystick solution for Windows when gamepad output is required

Keep the project modular so that the input/output system can be changed without rewriting the hand-tracking system.

3. Hand Tracking

The system should use the webcam to detect both hands.

Track appropriate hand landmarks, such as:

Wrist
Thumb
Index finger
Other useful finger landmarks

The system should determine the relative position of the left and right hands.

Use the relationship between the two hands to estimate the steering-wheel rotation.

For example:

             Right Hand
                  ●
                 /
                /
               /
              ●
          Left Hand


When the hands rotate clockwise, the virtual steering wheel should rotate right.

When the hands rotate counterclockwise, the virtual steering wheel should rotate left.

4. Steering Calculation

Calculate a steering angle from the hand positions.

The system should support:

Left steering
Center/neutral steering
Right steering

Example:

-90°             0°              +90°
LEFT           CENTER            RIGHT


The steering calculation should be stable and should not jump significantly because of small tracking errors.

5. Calibration

Implement an automatic or manual center-calibration system.

When the user holds their hands in the neutral steering position, the system should allow them to set that position as:

Steering Center = 0°


The system should then calculate steering relative to this calibrated center.

Also provide a way to recalibrate when necessary.

6. Smoothing and Stability

Camera-based hand tracking can be noisy.

Implement smoothing to prevent:

10°
15°
8°
17°
11°


from causing the virtual wheel to shake.

The output should instead behave more like:

10°
11°
12°
12°
13°


Allow the smoothing level to be configurable.

Also implement:

Dead zone
Sensitivity
Maximum steering angle
Steering inversion
7. Virtual Steering Wheel

Create a graphical virtual steering wheel using Pygame or another suitable Python library.

The wheel should visually rotate according to the calculated steering angle.

Display information such as:

Steering Angle: +32°
Direction: RIGHT
Hands Detected: YES
System Status: ACTIVE
Output Mode: GAMEPAD


Also display the detected hand landmarks and/or webcam feed.

8. Universal Racing Game Compatibility

The system should be designed as a universal hand-controlled racing input device, rather than being limited to one specific racing game.

Support multiple output modes.

Mode A — Keyboard Output

Map the steering movement to keyboard controls.

For example:

Hand turns LEFT
       ↓
Left keyboard input

Hand turns RIGHT
       ↓
Right keyboard input


Allow configuration of:

Steering sensitivity
Dead zone
Key bindings
Response speed

This mode should work with racing games that accept keyboard steering.

Mode B — Virtual Gamepad / Analog Steering

Implement a virtual gamepad/joystick output mode.

The calculated steering angle should be converted into an analog steering axis rather than only Left/Right keyboard presses.

For example:

Full Left       Center        Full Right
   -1.0            0              +1.0
     │             │                │
     └──────── Steering Axis ───────┘


The goal is for compatible Windows racing games to detect the system as a controller and use the steering value like an analog steering wheel.

Allow configuration of:

Steering range
Sensitivity
Dead zone
Smoothing
Inversion
Center position

Do not hard-code the system for a specific racing game.

Mode C — Browser Game Support

Support browser-based racing games that accept:

Keyboard input
Gamepad/joystick input

The system should work regardless of whether the racing game is running as:

A Windows .exe application
A browser-based game

However, clearly document that compatibility depends on the game accepting the selected input method.

Mode D — Serial / Arduino / ESP32 Output

Add an optional serial-output mode.

The Python application should be able to send the steering value through USB serial communication to an Arduino or ESP32.

For example:

Hand Movement
      ↓
Steering Angle
      ↓
Python
      ↓
USB Serial
      ↓
Arduino / ESP32
      ↓
Servo / Motor / Robot


The serial protocol should be simple and documented.

Example:

STEER:32


or another reliable format.

Provide a basic Arduino/ESP32 example that receives the steering value.

This mode is optional and should not be required for controlling PC racing games.

9. Configuration Panel

Create a settings/configuration section containing:

Steering sensitivity
Maximum steering angle
Dead zone
Smoothing level
Steering inversion
Center calibration
Output mode
Keyboard key bindings
Serial port selection
Serial baud rate
Gamepad settings if applicable

Save configuration settings when appropriate.

10. Hands-Off Detection

Detect when the user removes one or both hands.

Display:

HANDS DETECTED: NO
SYSTEM STATUS: PAUSED


When the hands are detected again, allow the system to resume safely.

Avoid sending unintended steering commands when tracking is lost.

11. Performance

The system should operate in real time with low latency.

Optimize the implementation for:

Stable FPS
Low input latency
Smooth steering
Reliable hand tracking

Avoid unnecessary processing that reduces webcam performance.

12. Project Architecture

Use a modular architecture similar to:

                 WEBCAM
                    │
                    ▼
             HAND DETECTION
              MediaPipe
                    │
                    ▼
            HAND LANDMARKS
                    │
                    ▼
          STEERING CALCULATION
                    │
                    ▼
          CALIBRATION + FILTER
                    │
                    ▼
             STEERING VALUE
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
      KEYBOARD   GAMEPAD   SERIAL
       OUTPUT    OUTPUT    OUTPUT
          │         │         │
          ▼         ▼         ▼
      WEB GAME   PC GAME   ARDUINO/
                            ESP32


Keep each component separated into modules/classes where appropriate.

13. Development Approach

Build the project step by step instead of providing the entire project at once.

Start with:

Step 1 — Webcam + Hand Detection

Create a basic Python program that:

Opens the webcam.
Detects both hands using MediaPipe.
Draws hand landmarks.
Displays the camera feed.
Shows whether one or two hands are detected.

Then continue with:

Step 2 — Two-Hand Tracking

Track the positions of both hands and display their coordinates.

Step 3 — Steering Calculation

Calculate the relative angle between the hands.

Step 4 — Center Calibration

Implement neutral-position calibration.

Step 5 — Steering Smoothing

Add filtering, dead zone, and sensitivity control.

Step 6 — Virtual Steering Wheel

Create the graphical steering wheel and rotate it according to the calculated angle.

Step 7 — Keyboard Output

Allow the steering system to control games using keyboard input.

Step 8 — Virtual Gamepad Output

Implement analog steering through a virtual gamepad/joystick so compatible Windows racing games can recognize the steering input.

Step 9 — Browser Game Testing

Test the keyboard and gamepad modes with suitable browser-based racing games.

Step 10 — Serial/Arduino Mode

Add optional serial communication with Arduino/ESP32.

Step 11 — Final Integrated Application

Combine everything into a clean application with:

Webcam feed
Hand tracking
Virtual steering wheel
Steering angle
Calibration
Settings
Output-mode selection
Status indicators
Step 12 — Testing and Troubleshooting

Test:

Different lighting conditions
Different hand positions
Fast steering movements
Slow steering movements
One-hand loss
Both-hand loss
Tracking errors
Different steering sensitivities
Keyboard racing games
Compatible PC racing games
Browser racing games

Document limitations and compatibility requirements.

14. Code Requirements

For every development step, provide:

Complete working code.
File/folder structure.
Required Python packages.
Installation commands.
How to run the program.
Explanation of how the code works.
Expected output.
Common errors and solutions.
Testing instructions.

Do not skip important implementation details.

Keep the code beginner-friendly but structured enough for a university/college project.

At the end, provide:

Complete project folder structure
Final source code
Installation guide
User guide
System architecture diagram
Algorithm explanation
Testing procedure
Limitations
Future improvements
Project presentation points
Possible viva/interview questions and answers