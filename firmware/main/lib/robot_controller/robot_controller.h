#ifndef ROBOT_CONTROLLER_H
#define ROBOT_CONTROLLER_H

#include <network_protocol.h>
#include <robot.h>

void handlePacket(Robot &robot, const MessagePacket &packet);

#endif
