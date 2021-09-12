import uasyncio
from machine import UART, Pin

import config
from core import state, l
from core.fingerprint import FingerprintEx
from libs import adafruit_fingerprint


class Fingerprint:
    def __init__(self):
        uart = UART(
            config.fp_uart_id,
            config.fp_baud_rate,
            tx=Pin(config.fp_tx_pin),
            rx=Pin(config.fp_rx_pin),
            timeout=100,
            rxbuf=10240
        )
        self._finger = FingerprintEx(uart, passwd=[0x00, 0x03, 0xA5, 0x37])
        self._irq_pin = Pin(config.fp_touch_irq_pin, Pin.IN, pull=Pin.PULL_UP)

        l.info('FP initialized')

    async def task(self):
        while True:
            await uasyncio.sleep_ms(0)
            finger_irq = not self._irq_pin.value()
            if not finger_irq:
                continue

            state.FP_VERIFIED = await self.get_fingerprint()
            if state.FP_VERIFIED:
                await uasyncio.sleep(3)
                state.FP_VERIFIED = False

    async def get_fingerprint(self):
        """Get a finger print image, template it, and see if it matches!"""
        l.debug('FP', "Waiting for image...")

        if self._finger.get_image() != adafruit_fingerprint.OK:
            return False

        l.debug('FP', "Templating...")
        if self._finger.image_2_tz(1) != adafruit_fingerprint.OK:
            return False

        l.debug('FP', "Searching...")
        if self._finger.finger_search() != adafruit_fingerprint.OK:
            state.FP_VERIFIED_INVALID = True
            await uasyncio.sleep(1)
            state.FP_VERIFIED_INVALID = False
            return False

        l.debug('FP', "Found")

        return True
