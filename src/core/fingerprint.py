import time

from .logger import l
from libs.adafruit_fingerprint import Adafruit_Fingerprint


class FingerprintEx(Adafruit_Fingerprint):
    _timout = 1000  # ms

    def __init__(self, uart, passwd=(0, 0, 0, 0)):
        self._uart = uart
        self._uart_flush()
        super().__init__(uart, passwd=passwd)

    def _uart_flush(self):
        l.debug('Flushing UART')

        while self._uart.any():
            self._uart.read(self._uart.any())

    def _get_packet(self, expected):
        start = time.ticks_ms()
        while self._uart.any() < expected:
            if time.ticks_diff(time.ticks_ms(), start) > self._timout:
                l.error('Data did not received in %sms. Check wiring.' % self._timout)
                return [None]

        try:
            return super()._get_packet(expected)
        except RuntimeError:
            return [None]
