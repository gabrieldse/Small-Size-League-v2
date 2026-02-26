#include <robot_controller.h>

void handlePacket(Robot &robot, const MessagePacket &packet) {
  robot.setMotorFL(packet.frontLeft.setPoint, packet.frontLeft.direction);
  robot.setMotorBL(packet.backLeft.setPoint, packet.backLeft.direction);
  robot.setMotorFR(packet.frontRight.setPoint, packet.frontRight.direction);
  robot.setMotorBR(packet.backRight.setPoint, packet.backRight.direction);

  if (packet.kickerCommand == 1) {
    robot.kick();
  }
}
