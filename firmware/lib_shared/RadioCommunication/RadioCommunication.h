#pragma once
#include <RF24.h>

class RadioCommunication {
public:
  RadioCommunication(RF24 &radio, const byte *address);

  void beginTX();
  void beginRX();

  bool receivePacket(void *buffer, size_t bufferSize);

private:
  RF24 &_radio;
  const byte *_address;
};
