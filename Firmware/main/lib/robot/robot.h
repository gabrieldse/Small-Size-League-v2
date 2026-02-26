#ifndef Robot_h
#define Robot_h

#include <Arduino.h>
#include <config.h>
#include <motor.h>

class Robot {
public:
  explicit Robot(RobotID id);

  void initializeRobot();

  void setMotorFL(int speed, int direction);
  void setMotorBL(int speed, int direction);
  void setMotorFR(int speed, int direction);
  void setMotorBR(int speed, int direction);

  void kick();
  void stopAllMotors();

  int getId();

private:
  explicit Robot(const RobotConfig &config);
  Motor motorFL;
  Motor motorBL;
  Motor motorFR;
  Motor motorBR;

  int id;
  uint8_t _kickerPin;
};

#endif
