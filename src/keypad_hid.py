import uasyncio

import hid
from machine import Pin, Timer

import config
from core import Keypad, l


class KeypadHID:
    AUTH = 0
    MACRO = 1

    _tm = Timer()
    _running = False

    def __init__(self):
        self._mode = self.MACRO

        cols = [Pin(x) for x in config.keypad_cols]
        rows = [Pin(x) for x in config.keypad_rows]

        self._keypad = Keypad(rows, cols, config.keypad_keymap)

    def start(self):
        self._running = True
        uasyncio.run(self._main())

    def stop(self):
        if not self._running:
            l.warn('Not running')

        self._running = False

    async def _main(self):
        while self._running:
            key, long_press = self._keypad.pressed_key

            if not key:
                continue

            if self._mode == self.MACRO:
                if long_press:
                    hid.Send(config.hid_macro_long_modifier, key)
                else:
                    hid.Send(config.hid_macro_short_modifier, key)
            else:
                raise NotImplementedError

    def set_mode(self, mode):
        self._mode = mode
