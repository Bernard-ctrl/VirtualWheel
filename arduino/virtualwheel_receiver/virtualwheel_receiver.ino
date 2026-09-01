// VirtualWheel Step 10 serial receiver example.
// Protocol: STEER:32.5;THROTTLE:ACCELERATE\n
String inputLine;
float steeringDegrees = 0.0;
String throttle = "NEUTRAL";

void setup() {
  Serial.begin(115200);
  inputLine.reserve(80);
}

void loop() {
  while (Serial.available() > 0) {
    char character = (char)Serial.read();
    if (character == '\n') {
      parseMessage(inputLine);
      inputLine = "";
    } else if (character != '\r') {
      inputLine += character;
    }
  }

  // Use steeringDegrees and throttle here to control a servo, motor, etc.
}

void parseMessage(String message) {
  int steerStart = message.indexOf("STEER:");
  int throttleStart = message.indexOf(";THROTTLE:");
  if (steerStart < 0 || throttleStart < 0) return;

  String steerText = message.substring(steerStart + 6, throttleStart);
  steeringDegrees = steerText.toFloat();
  throttle = message.substring(throttleStart + 10);

  Serial.print("Steering: ");
  Serial.print(steeringDegrees, 1);
  Serial.print("  Throttle: ");
  Serial.println(throttle);
}
