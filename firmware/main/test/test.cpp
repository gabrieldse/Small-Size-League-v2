#include <config.h>
#include <motor.h>
#include <robot.h>

const RobotID CURRENT_ROBOT = SIMON; // Change to ALVIN, SIMON, or THEODORE
Robot robot(CURRENT_ROBOT);

void setup() {
  Serial.begin(19200);
  robot.initializeRobot();
  Serial.println("Robot ready and waiting for commands...");
}

void loop() {

  setMotorFL(200, 1);
  setMotorBL(200, 1);
  setMotorFR(200, 1);
  setMotorBR(200, 1);
}
