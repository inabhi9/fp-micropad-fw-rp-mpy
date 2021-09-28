import uasyncio
from machine import Pin, PWM

import config
from core import l

LED_PIN_RED = Pin(config.LED_RGB_PINS[0])
LED_PIN_GREEN = Pin(config.LED_RGB_PINS[1])
LED_PIN_BLUE = Pin(config.LED_RGB_PINS[2])

VIBRATOR = Pin(config.VIBRATOR_PIN, mode=Pin.OUT)


def vibrator_on():
    if config.HAPTIC_FEEDBACK:
        l.debug('Turning on vibrator')
        VIBRATOR.low()


def vibrator_off():
    l.debug('Turning off vibrator')
    VIBRATOR.high()


def led_off(led):
    led.init(mode=Pin.OUT)
    led.low()


def led_on(led):
    led.init(mode=Pin.OUT)
    led.high()


async def pwm(pin, freq=50, peak=256, delay_cycle=1, break_on=lambda: False):
    pwm_ = PWM(pin)

    pwm_.freq(freq)
    duty = 0
    direction = 1

    for _ in range(2 * peak):
        duty += direction
        if duty > peak - 1:
            duty = peak - 1
            direction = -1
        elif duty < 0:
            duty = 0
            direction = 1

        pwm_.duty_u16(duty * duty)

        if break_on() is True:
            pwm_.duty_u16(0)
            pwm_.deinit()
            break

        await uasyncio.sleep_ms(delay_cycle)
