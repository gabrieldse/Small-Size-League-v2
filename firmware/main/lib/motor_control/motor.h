#ifndef Motor_h
#define Motor_h

#include <Arduino.h>
#include <config.h>

#ifdef ESP32
#define LEDC_TIMER_BITS 8
#define LEDC_BASE_FREQ 5000
#endif

class Motor {
public:
  Motor(uint8_t pin1, uint8_t pin2, uint8_t channel1, uint8_t channel2);

  void begin();

  void move(int speed, int direction);

  void stop();

private:
  uint8_t _pin1, _pin2;
  uint8_t _channel1, _channel2;
};

#endif
