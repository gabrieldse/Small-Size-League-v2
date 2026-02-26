#include <Arduino.h>
#include <robot.h>

Robot::Robot(RobotID id)
    : Robot((id == ALVIN)   ? ALVIN_CONFIG
            : (id == SIMON) ? SIMON_CONFIG
                            : THEODORE_CONFIG) {
  this->id = id;
  Serial.printf("Initializing with config for Robot ID: %d\n", id);
}

Robot::Robot(const RobotConfig &config)
    : motorFL(config.frontLeft.in1_pin, config.frontLeft.in2_pin,
              config.frontLeft.channel1, config.frontLeft.channel2),
      motorBL(config.backLeft.in1_pin, config.backLeft.in2_pin,
              config.backLeft.channel1, config.backLeft.channel2),
      motorFR(config.frontRight.in1_pin, config.frontRight.in2_pin,
              config.frontRight.channel1, config.frontRight.channel2),
      motorBR(config.backRight.in1_pin, config.backRight.in2_pin,
              config.backRight.channel1, config.backRight.channel2),
      _kickerPin(config.kickerPin) {
  Serial.println("Robot instance created with provided configuration.");
}

void Robot::initializeRobot() {
  motorFL.begin();
  motorBL.begin();
  motorFR.begin();
  motorBR.begin();

  pinMode(_kickerPin, OUTPUT);
  digitalWrite(_kickerPin, LOW);

  Serial.println("Robot initialized: 4 motors and Kicker pins configured.");
}

void Robot::setMotorFL(int speed, int direction) {
  this->motorFL.move(speed, direction);
}

void Robot::setMotorFR(int speed, int direction) {
  this->motorFR.move(speed, direction);
}

void Robot::setMotorBL(int speed, int direction) {
  this->motorBL.move(speed, direction);
}

void Robot::setMotorBR(int speed, int direction) {
  this->motorBR.move(speed, direction);
}

void Robot::kick() {
  digitalWrite(_kickerPin, HIGH);
  delay(100); // AJUSTE ESTE VALOR COM CUIDADO!
  digitalWrite(_kickerPin, LOW);
  Serial.println("Kicker acionado!");
}

void Robot::stopAllMotors() {
  motorFL.stop();
  motorBL.stop();
  motorFR.stop();
  motorBR.stop();
  // Serial.println("All motors stopped.");
}

int Robot::getId() { return static_cast<int>(this->id); }
