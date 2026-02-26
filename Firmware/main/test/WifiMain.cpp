#include <Arduino.h>
#include <communication.h>
#include <config.h>
#include <network_protocol.h>
#include <robot.h>
#include <robot_controller.h>

// --- Configuration Section ---
const RobotID CURRENT_ROBOT = SIMON; // Change to ALVIN, SIMON, or THEODORE
Robot robot(CURRENT_ROBOT);

Communication messenger(LARSIS_ROBOS_CONFIG);
// --- End Configuration Section ---

unsigned long lastPacketTime = 0;

void setup() {
  Serial.begin(19200);
  robot.initializeRobot();
  messenger.begin();
  Serial.println("Robot ready and waiting for commands...");
}

/**
 * Main loop function
 *
 * - Continuously checks for incoming message packets.
 * - If a packet is received, updates the timestamp and dispatches the packet to
 * the robot controller.
 * - If no packet is received for more than 500 milliseconds, stops all robot
 * motors as a safety measure.
 */

void loop() {
  MessagePacket packet;
  if (messenger.receivePacket(packet)) {
    Serial.println("Comando Front Left:");
    Serial.print("  SetPoint: ");
    Serial.println(packet.frontLeft.setPoint);
    Serial.print("  Direction: ");
    Serial.println(packet.frontLeft.direction);

    Serial.println("Comando Front Right:");
    Serial.print("  SetPoint: ");
    Serial.println(packet.frontRight.setPoint);
    Serial.print("  Direction: ");
    Serial.println(packet.frontRight.direction);

    Serial.println("Comando Back Left:");
    Serial.print("  SetPoint: ");
    Serial.println(packet.backLeft.setPoint);
    Serial.print("  Direction: ");
    Serial.println(packet.backLeft.direction);

    Serial.println("Comando Back Right:");
    Serial.print("  SetPoint: ");
    Serial.println(packet.backRight.setPoint);
    Serial.print("  Direction: ");
    Serial.println(packet.backRight.direction);

    // Imprimir o comando do kicker
    Serial.print("Comando Kicker: ");
    Serial.println(packet.kickerCommand);
    lastPacketTime = millis();
    handlePacket(robot, packet);
  }
  if (millis() - lastPacketTime > 500) {
    robot.stopAllMotors();
  }
}
