import time

import uasyncio
from machine import UART, Pin

import config
from core import state, l
from core.fingerprint import FingerprintEx
from libs import adafruit_fingerprint


class Fingerprint:
    # required to boot FP
    _delay_after_fp_on = 30  # ms

    def __init__(self):
        uart = UART(
            config.FP_UART_ID,
            config.FP_BAUD_RATE,
            tx=Pin(config.FP_TX_PIN),
            rx=Pin(config.FP_RX_PIN),
            timeout=100,
            rxbuf=10240
        )

        self._tbase = Pin(config.FP_TBASE, Pin.OUT)
        self._tbase.low()
        time.sleep(self._delay_after_fp_on / 1000)

        self._finger = FingerprintEx(uart)
        self._tbase.high()

        self._irq_pin = Pin(config.FP_IRQ_PIN, Pin.IN, pull=Pin.PULL_UP)

        l.info('FP initialized')

    async def task(self):
        uasyncio.create_task(self._sample_irq_val())

        while True:
            await uasyncio.sleep_ms(1)

            if self.finger_irq:
                await self._set_fp_power(True)

                try:
                    state.FP_VERIFIED = await self.get_fingerprint()
                except (RuntimeError, ValueError) as e:
                    # For some reason sometimes it happens, buffer falls short
                    # and throws value error
                    # there might be some random bytes
                    self._finger._uart_flush()
                    l.warn('Error while getting fingerprint: %s', e)
                    state.FP_VERIFIED = False
                    continue

                if state.FP_VERIFIED:
                    await self._set_fp_power(False)
                    await uasyncio.sleep(config.FP_AUTH_KP_INPUT_TIMEOUT)
                    state.FP_VERIFIED = False
            else:
                await self._set_fp_power(False)

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

    finger_irq = 0

    async def _sample_irq_val(self):
        """
        Task to sample value to eliminate the noise.
        """
        while True:
            await uasyncio.sleep_ms(0)
            val = self._irq_pin.value()

            if self.finger_irq and not val:
                # 1 second to eliminate noise + 2 seconds to allow
                # FP to sense touch if it's about to timeout
                await uasyncio.sleep(3)
                val = self._irq_pin.value()

            self.finger_irq = val

    __fp_power_state = False

    async def _set_fp_power(self, mode: bool):
        # Prevent writing again if already in the state
        if mode and not self.__fp_power_state:
            self.__fp_power_state = True
            self._tbase.low()
            await uasyncio.sleep_ms(self._delay_after_fp_on)
            # For some weird reason, occasionally some random bytes appear
            self._finger._uart_flush()
        elif not mode and self.__fp_power_state:
            self._tbase.high()
            self.__fp_power_state = False
