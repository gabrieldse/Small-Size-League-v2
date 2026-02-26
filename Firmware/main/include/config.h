#ifndef CONFIG_H
#define CONFIG_H

const uint8_t HEADER[2] = {0xAA, 0x55};
const uint8_t TAIL = 0xFF;

struct MotorPins {
  int in1_pin;
  int in2_pin;
  int channel1;
  int channel2;
};

struct RadioPins {
  uint8_t ce_pin;
  uint8_t csn_pin;
  uint8_t sck_pin;
  uint8_t miso_pin;
  uint8_t mosi_pin;
};

struct RobotConfig {
  MotorPins frontLeft;
  MotorPins backLeft;
  MotorPins frontRight;
  MotorPins backRight;
  uint8_t kickerPin;
  RadioPins radioPins;
};

enum RobotID { ALVIN = 6, SIMON = 3, THEODORE = 7 };

// PINS FOR ALVIN
const RobotConfig ALVIN_CONFIG = {
    .frontLeft = {26, 25, 0, 1}, // {IN1, IN2, CHAN1, CHAN2}
    .backLeft = {21, 19, 2, 3},
    .frontRight = {32, 33, 4, 5},
    .backRight = {4, 18, 6, 7},
    .kickerPin = 27,
    .radioPins = {2, 5, 14, 12, 13} // {CE, CSN, SCK, MISO, MOSI}
};

// PINS FOR SIMON
const RobotConfig SIMON_CONFIG = {
    .frontLeft = {4, 18, 6, 7},   // Era backLeft (posição física 2)
    .backLeft = {26, 25, 0, 1},   // Era frontRight (posição física 3)
    .frontRight = {21, 19, 2, 3}, // Era backRight (posição física 4)
    .backRight = {32, 33, 4, 5},  // Era frontLeft (posição física 1)
    .kickerPin = 27,
    .radioPins = {2, 5, 14, 12, 13} // {CE, CSN, SCK, MISO, MOSI}

};

// PINS FOR THEODORE
const RobotConfig THEODORE_CONFIG = {
    .frontLeft = {26, 25, 0, 1}, // {IN1, IN2, CHAN1, CHAN2}
    .backLeft = {21, 19, 2, 3},
    .frontRight = {32, 33, 4, 5},
    .backRight = {4, 18, 6, 7},
    .kickerPin = 27,
    .radioPins = {2, 5, 14, 12, 13} // {CE, CSN, SCK, MISO, MOSI}

};

struct NetworkConfig {
  const char *ssid;
  const char *password;
  int port;
};

// --- AVAILABLE NETWORK CONFIGURATIONS ---
const NetworkConfig LABMICRO_WIFI_CONFIG = {"labmicro", "l@bm!cro2023", 8080};
// ...
// Add a new one? Just add it here! No other files need to change. (Except
// main.ino to choose which one to use)
const NetworkConfig LARSIS_ROBOS_CONFIG = {"LARSIS_ROBOS", "larsis@larsis",
                                           8080}; // Example

#define WHEEL_DIAMETER_MM 60

#endif
