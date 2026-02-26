#include "RadioCommunication.h"
#include <Arduino.h>
#include <RF24.h>
#include <communication.h>
#include <config.h>
#include <network_protocol.h>
#include <robot.h>
#include <robot_controller.h>

// --- Configuração dos pinos do NRF24L01 ---
#define CE_PIN 2
#define CSN_PIN 5
#define SCK_PIN 14
#define MISO_PIN 12
#define MOSI_PIN 13

// Cria uma instância de SPI no barramento HSPI
SPIClass spiNRF(HSPI);

// Instância do rádio usando CE e CSN
RF24 radio(CE_PIN, CSN_PIN);

// Endereço do rádio
const byte RADIO_ADDRESS[5] = {'R', 'o', 'b', 'o', '1'};
RadioCommunication messenger(radio, RADIO_ADDRESS);

// Identificação do robô
const RobotID CURRENT_ROBOT = SIMON;
Robot robot(CURRENT_ROBOT);

// --- Estrutura do pacote ---
struct CommandPacket {
  uint8_t robot_id;
  uint8_t fl_s, fl_d;
  uint8_t bl_s, bl_d;
  uint8_t fr_s, fr_d;
  uint8_t br_s, br_d;
  uint8_t kicker;
};

const size_t PACKET_SIZE = sizeof(CommandPacket);
CommandPacket packet;

unsigned long lastPacketTime = 0;

void setup() {
  Serial.begin(19200);

  // Inicializa SPI nos pinos escolhidos
  spiNRF.begin(SCK_PIN, MISO_PIN, MOSI_PIN, CSN_PIN);

  // Inicializa rádio usando esse SPI
  if (!radio.begin(&spiNRF)) {
    Serial.println("Falha ao iniciar o NRF24L01!");
    while (1)
      ;
  }

  robot.initializeRobot();
  messenger.beginRX();

  Serial.println("Robot pronto e aguardando comandos...");
  Serial.print("I am ");
  Serial.println(robot.getId());
}

void processPacket(const CommandPacket &pkt) {
  lastPacketTime = millis();

  // Debug detalhado
  Serial.print("Pacote recebido. Robo: ");
  Serial.println(pkt.robot_id);
  Serial.print("FL: ");
  Serial.print(pkt.fl_s);
  Serial.print(" dir=");
  Serial.print(pkt.fl_d);
  Serial.print(" | BL: ");
  Serial.print(pkt.bl_s);
  Serial.print(" dir=");
  Serial.print(pkt.bl_d);
  Serial.print(" | FR: ");
  Serial.print(pkt.fr_s);
  Serial.print(" dir=");
  Serial.print(pkt.fr_d);
  Serial.print(" | BR: ");
  Serial.print(pkt.br_s);
  Serial.print(" dir=");
  Serial.println(pkt.br_d);
  Serial.print("Kicker: ");
  Serial.println(pkt.kicker);

  // Comandos aos motores
  robot.setMotorFL(pkt.fl_s, pkt.fl_d);
  robot.setMotorBL(pkt.bl_s, pkt.bl_d);
  robot.setMotorFR(pkt.fr_s, pkt.fr_d);
  robot.setMotorBR(pkt.br_s, pkt.br_d);
  if (pkt.kicker)
    robot.kick();
}

void loop() {

  lastPacketTime = millis();

  if (radio.available()) {
    radio.read(&packet, PACKET_SIZE);

    if (packet.robot_id != robot.getId()) {
      Serial.print("Pacote ignorado: ");
      Serial.println(packet.robot_id);
      return;
    }
    processPacket(packet);
  }
  // Timeout para parar o robô se não receber comandos
  if (millis() - lastPacketTime > 500) {
    robot.stopAllMotors();
  }
}
