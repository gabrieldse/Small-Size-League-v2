#ifndef NETWORK_PROTOCOL_H
#define NETWORK_PROTOCOL_H

#include <stdint.h>

const size_t UDP_PACKET_SIZE = 9;
struct __attribute__((packed)) CommandPacket {
  uint8_t header1;
  uint8_t header2;
  uint8_t robot_id;
  uint8_t m1_speed;
  uint8_t m1_dir;
  uint8_t m2_speed;
  uint8_t m2_dir;
  uint8_t m3_speed;
  uint8_t m3_dir;
  uint8_t m4_speed;
  uint8_t m4_dir;
  uint8_t kicker;
  uint8_t checksum;
  uint8_t tail;
};

// A command for a single motor
struct __attribute__((packed)) MotorCommand {
  uint8_t setPoint;
  uint8_t direction;
};

// The main packet, composed of smaller, logical parts
struct __attribute__((packed)) MessagePacket {
  MotorCommand frontLeft;
  MotorCommand frontRight;
  MotorCommand backLeft;
  MotorCommand backRight;
  uint8_t kickerCommand;
};

// This safety check ensures the memory size is correct for the network
static_assert(sizeof(MessagePacket) == UDP_PACKET_SIZE,
              "MessagePacket size mismatch!");

#endif // NETWORK_PROTOCOL_H
