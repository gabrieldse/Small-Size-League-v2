#include <Arduino.h>
#include <RF24.h>

const uint8_t HEADER[2] = {0xAA, 0x55};
const uint8_t TAIL = 0xFF;
const uint8_t PACKET_LEN = 14; //  Header 1 e 2 + ID(1)+9 dados+checksum(1)+tail(1)
const uint8_t BUFFER_SIZE = 64;

uint8_t buffer[BUFFER_SIZE];
uint8_t head = 0;     // próximo byte a escrever
uint8_t tail_idx = 0; // próximo byte a processar

#define CE_PIN PB0
#define CSN_PIN PA4
#define CHANNEL   76                
#define DATARATE  RF24_250KBPS
#define POWER     RF24_PA_MAX

RF24 radio(CE_PIN, CSN_PIN);
const byte RADIO_ADDRESS[5] = {'R','o','b','o','1'};

void processBuffer();
uint8_t calc_sum();
uint8_t buffer_len();
void sendToRobot(uint8_t* buffer);

void setup() {
    Serial.begin(115200);
    Serial.println("Iniciando...");

    if (!radio.begin()) {
        Serial.println("Falha ao iniciar o NRF24L01!");
    }
    else {
        Serial.println("NRF24L01 iniciado com sucesso.");
    }
    radio.setChannel(CHANNEL);
    radio.setDataRate(DATARATE);
    radio.setPALevel(POWER, true);      // força override
    radio.setRetries(5, 15);
    radio.setAutoAck(true);
    radio.enableAckPayload();
    radio.enableDynamicPayloads();

    // Mesmo endereço para RX e TX
    radio.openWritingPipe(RADIO_ADDRESS);
    radio.openReadingPipe(1, RADIO_ADDRESS); // habilita ACK no mesmo pipe

    radio.stopListening();

    //Serial.println("Radio pronto para transmitir pacotes.");
    //adio.printDetails();
}

void loop() {
    // lê bytes da Serial e coloca no buffer circular
    while (Serial.available()) {
        buffer[head] = Serial.read();
        head = (head + 1) % BUFFER_SIZE; 
        // se o buffer circular estiver cheio, avança tail para não sobrescrever dados
        if (head == tail_idx) {
            tail_idx = (tail_idx + 1) % BUFFER_SIZE;
        }
    }

    processBuffer();
}

void sendToRobot(uint8_t* buffer) {
    bool ok = radio.write(buffer, PACKET_LEN);

    if (!ok) {
        Serial.println("[ERRO] Falha ao enviar via rádio!");
    } else {
        Serial.println("[OK] Pacote enviado com sucesso via rádio!");
    }
}

uint8_t calc_sum(uint8_t* data, uint8_t len) {
    uint16_t sum = 0;
    for (uint8_t i = 0; i < len; i++) sum += data[i];
    return sum % 256;
}

// retorna número de bytes válidos no buffer
uint8_t buffer_len() {
    if (head >= tail_idx) return head - tail_idx;
    return BUFFER_SIZE - tail_idx + head;
}

void processBuffer() {
    while (buffer_len() >= PACKET_LEN) {
        uint8_t idx0 = tail_idx;
        uint8_t idx1 = (tail_idx + 1) % BUFFER_SIZE;

        if (buffer[idx0] == HEADER[0] && buffer[idx1] == HEADER[1]) {
            Serial.println("Header válido");
            uint8_t checksum_idx = (tail_idx + PACKET_LEN - 2) % BUFFER_SIZE;
            uint8_t tail_packet_idx = (tail_idx + PACKET_LEN - 1) % BUFFER_SIZE;

            if (buffer[tail_packet_idx] == TAIL) {
            Serial.println("Tail válido");
            uint8_t final_packet[PACKET_LEN]; // Buffer para enviar

            // Copia o pacote do buffer circular para o buffer de envio
            for (int i = 0; i < PACKET_LEN; i++) {
                final_packet[i] = buffer[(tail_idx + i) % BUFFER_SIZE];
            }

            uint8_t checksum_idx = PACKET_LEN - 2; 
            uint8_t data_start_idx = 3;

            uint8_t checksum_recebido = final_packet[checksum_idx];
            
            uint8_t checksum_calculado = calc_sum(&final_packet[data_start_idx], 9); // Calcula sobre 9 bytes de dados

            Serial.print("\nChecksum recebido: ");
            Serial.println(checksum_recebido);
            Serial.print(" Calculado: ");
            Serial.println(checksum_calculado);

            if (checksum_recebido == checksum_calculado) {
                uint8_t robot_id = final_packet[2]; // Pega o ID do pacote
                Serial.print("Pacote válido! ID=");
                Serial.println(robot_id);
                
                sendToRobot(final_packet);
            } else {
                Serial.println("Checksum inválido");
            }

                tail_idx = (tail_idx + PACKET_LEN) % BUFFER_SIZE;
            } else {
                tail_idx = (tail_idx + 1) % BUFFER_SIZE;
            }
        } else {
            tail_idx = (tail_idx + 1) % BUFFER_SIZE;
        }
    }
}