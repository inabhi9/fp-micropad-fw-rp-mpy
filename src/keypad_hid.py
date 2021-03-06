import hid
import uasyncio
from machine import Pin

import config
from core import Keypad, l, state, events


class KeypadHID:
    _running = False

    def __init__(self, db):
        self._db = db

        cols = [Pin(x) for x in config.keypad_cols]
        rows = [Pin(x) for x in config.keypad_rows]

        self._keypad = Keypad(rows, cols, config.keypad_keymap)

    async def task(self):
        while True:
            await self._main()
            await uasyncio.sleep_ms(0)

    def stop(self):
        if not self._running:
            l.warn('Not running')

        self._running = False

    async def _main(self, *args):
        key, long_press = self._keypad.pressed_key

        if not key:
            return

        uasyncio.create_task(events.keypress.send(long_press=long_press))

        if not state.FP_VERIFIED:
            if long_press:
                hid.Send(config.hid_macro_long_modifier, key)
            else:
                hid.Send(config.hid_macro_short_modifier, key)
        else:
            self._send_pwd(key)
            state.FP_VERIFIED = False

    def _send_pwd(self, key):
        pwd = self._db.get(key)

        if pwd:
            l.debug('Sending pwd', pwd['passwd'])
            hid.Send(pwd['passwd'], 'ENTER' if pwd.get('enter', True) else '')
        else:
            l.warn('No password found for %s' % key)
