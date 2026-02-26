#ifndef COMMUNICATION_H
#define COMMUNICATION_H

#include <WiFi.h>
#include <WiFiUdp.h>
#include <config.h>
#include <network_protocol.h>

class Communication {
public:
  explicit Communication(const NetworkConfig &config);
  void begin();
  bool receivePacket(MessagePacket &packet);
  IPAddress getRemoteIP();
  int getRemotePort();

private:
  const char *_ssid;
  const char *_password;
  int _port;
  WiFiUDP Udp;
  IPAddress _remoteIP;
  int _remotePort;
  bool receivePacket(uint8_t *buffer, size_t size);
};

#endif
