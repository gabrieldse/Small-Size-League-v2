#include <Arduino.h>
#include <esp32-hal-ledc.h>
#include <motor.h>

#define LEDC_BASE_FREQ 5000
#define LEDC_TIMER_BITS 8

Motor::Motor(uint8_t pin1, uint8_t pin2, uint8_t channel1, uint8_t channel2)
    : _pin1(pin1), _pin2(pin2), _channel1(channel1), _channel2(channel2) {}

void Motor::begin() {
  pinMode(_pin1, OUTPUT);
  pinMode(_pin2, OUTPUT);

  // Step 1: Configure the PWM channels with a frequency and resolution
  ledcSetup(_channel1, LEDC_BASE_FREQ, LEDC_TIMER_BITS);
  ledcSetup(_channel2, LEDC_BASE_FREQ, LEDC_TIMER_BITS);

  // Step 2: Attach the GPIO pins to their respective configured channels
  ledcAttachPin(_pin1, _channel1);
  ledcAttachPin(_pin2, _channel2);

  stop();
  Serial.printf("Motor initialized on pins %d and %d\n", _pin1, _pin2);
}

void Motor::move(int speed, int direction) {
  speed = constrain(speed, 0, 255);

  if (direction == 0) {
    ledcWrite(_channel1, speed);
    ledcWrite(_channel2, 0);
  } else {
    ledcWrite(_channel1, 0);
    ledcWrite(_channel2, speed);
  }
}

void Motor::stop() {
  ledcWrite(_channel1, 0);
  ledcWrite(_channel2, 0);
}
