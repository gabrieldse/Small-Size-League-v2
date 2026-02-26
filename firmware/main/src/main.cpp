#include "RadioCommunication.h"
#include <Arduino.h>
#include <RF24.h>
#include <communication.h>
#include <config.h>
#include <network_protocol.h>
#include <robot.h>
#include <robot_controller.h>

#define CHANNEL 76 // canal menos poluído (2.476 GHz)
#define DATARATE RF24_250KBPS
#define POWER RF24_PA_MAX // máxima potência

// Identificação do robô
const RobotID CURRENT_ROBOT = SIMON;
Robot robot(CURRENT_ROBOT);
const RobotConfig &robot_pin = SIMON_CONFIG;

SPIClass spiNRF(HSPI);
RF24 radio(robot_pin.radioPins.ce_pin, robot_pin.radioPins.csn_pin);
const byte RADIO_ADDRESS[5] = {'R', 'o', 'b', 'o', '1'};

CommandPacket packet;
unsigned long lastPacketTime = 0;
const unsigned long PACKET_TIMEOUT = 200; // milliseconds

void processPacket(CommandPacket &pkt);
bool verifyChecksum(CommandPacket &pkt);

void setup() {
  Serial.begin(19200);

  // Inicializa SPI nos pinos escolhidos
  spiNRF.begin(robot_pin.radioPins.sck_pin, robot_pin.radioPins.miso_pin,
               robot_pin.radioPins.mosi_pin, robot_pin.radioPins.csn_pin);
  if (!radio.begin(&spiNRF)) {
    Serial.println("Falha ao iniciar o NRF24L01!");
  } else {
    Serial.println("NRF24L01 iniciado com sucesso.");
  }

  radio.setChannel(CHANNEL);
  radio.setDataRate(DATARATE);
  radio.setPALevel(POWER);
  radio.setAutoAck(true);
  radio.enableDynamicPayloads();
  radio.openReadingPipe(1, RADIO_ADDRESS);
  radio.startListening();

  Serial.println("Radio pronto para receber pacotes.");

  robot.initializeRobot();
  Serial.println("Robot pronto e aguardando comandos...");
  Serial.print("I am ");
  Serial.println(robot.getId());
  radio.printDetails();
}

void loop() {

  if (radio.available()) {
    radio.read(&packet, sizeof(packet));

    processPacket(packet);
    lastPacketTime = millis();
  }

  if (millis() - lastPacketTime > PACKET_TIMEOUT) {
    robot.setMotorFL(0, 0);
    robot.setMotorBL(0, 0);
    robot.setMotorFR(0, 0);
    robot.setMotorBR(0, 0);
    // Optional: ensure kicker is safe
  }
}

void processPacket(CommandPacket &pkt) {
  if (pkt.header1 != HEADER[0] || pkt.header2 != HEADER[1])
    return;
  if (pkt.tail != TAIL)
    return;
  if (pkt.robot_id != robot.getId())
    return;
  if (!verifyChecksum(pkt))
    return;

  Serial.println("Checksum válido");
  Serial.println("Pacote recebido:");
  // comandos aos motores
  robot.setMotorFL(pkt.m1_speed, pkt.m1_dir);
  robot.setMotorFR(pkt.m2_speed, pkt.m2_dir);
  robot.setMotorBL(pkt.m3_speed, pkt.m3_dir);
  robot.setMotorBR(pkt.m4_speed, pkt.m4_dir);

  if (pkt.kicker)
    robot.kick();
}

bool verifyChecksum(CommandPacket &pkt) {
  uint8_t sum = 0;

  sum += pkt.m1_speed;
  sum += pkt.m1_dir;
  sum += pkt.m2_speed;
  sum += pkt.m2_dir;
  sum += pkt.m3_speed;
  sum += pkt.m3_dir;
  sum += pkt.m4_speed;
  sum += pkt.m4_dir;
  sum += pkt.kicker;

  // compara com checksum recebido
  return (sum % 256 == pkt.checksum);
}
