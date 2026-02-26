#include "RadioCommunication.h"
#include <Arduino.h>

#define CHANNEL 76 // canal menos poluído (2.476 GHz)
#define DATARATE RF24_250KBPS
#define POWER RF24_PA_MAX // máxima potência

RadioCommunication::RadioCommunication(RF24 &radio, const byte *address)
    : _radio(radio), _address(address) {}

// Inicializa para receber
void RadioCommunication::beginRX() {
  Serial.println("Iniciando comunicacao via radio (RX)...");

  if (!_radio.begin()) {
    Serial.println("Falha ao iniciar o radio! Verifique a fiacao.");
    while (1) {
    }
  }

  // Configurações básicas
  _radio.setChannel(CHANNEL);
  _radio.setDataRate(DATARATE);
  _radio.setPALevel(POWER, true); // força override
  _radio.setRetries(5, 15);       // habilita retransmissões
  _radio.setAutoAck(true);
  _radio.enableAckPayload();
  _radio.enableDynamicPayloads();

  // Mesmo endereço para RX e TX
  _radio.openReadingPipe(1, _address);
  _radio.openWritingPipe(_address); // garante simetria

  _radio.startListening();

  Serial.println("Radio pronto para receber pacotes.");
  //_radio.printDetails();
}

// Inicializa para transmitir
void RadioCommunication::beginTX() {
  Serial.println("Iniciando comunicacao via radio (TX)...");

  if (!_radio.begin()) {
    Serial.println("Falha ao iniciar o radio!");
    while (1) {
    }
  }

  // Configurações básicas
  _radio.setChannel(CHANNEL);
  _radio.setDataRate(DATARATE);
  _radio.setPALevel(POWER, true); // força override
  _radio.setRetries(5, 15);
  _radio.setAutoAck(true);
  _radio.enableAckPayload();
  _radio.enableDynamicPayloads();

  // Mesmo endereço para RX e TX
  _radio.openWritingPipe(_address);
  _radio.openReadingPipe(1, _address); // habilita ACK no mesmo pipe

  _radio.stopListening();

  Serial.println("Radio pronto para transmitir pacotes.");
  //_radio.printDetails();
}

bool RadioCommunication::receivePacket(void *buffer, size_t bufferSize) {
  if (_radio.available()) {
    _radio.read(buffer, bufferSize);
    return true;
  }
  return false;
}
