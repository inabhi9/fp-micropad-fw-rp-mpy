import time

from libs.adafruit_matrixkeypad import Matrix_Keypad
from .logger import l


class Keypad(Matrix_Keypad):
    _tick_down = None
    _tick_up = None
    _pk = None
    _sent = False
    _key_down = False

    def __init__(self, *args, **kwargs):
        self._lng_delay = kwargs.get('long_press_delay') or 250  # ms
        super().__init__(*args, **kwargs)

    @property
    def pressed_key(self):
        pressed_key = (self.pressed_keys or [None])[0]

        if pressed_key:
            l.debug('pressed key:', pressed_key, self._tick_down, self._tick_up)

        if not pressed_key and self._tick_down and not self._tick_up:
            self._tick_up = time.ticks_ms()

        if pressed_key and not self._tick_down and not self._tick_up:
            self._pk = pressed_key
            self._tick_down = time.ticks_ms()

        if self._tick_down:
            diff = time.ticks_diff(time.ticks_ms(), self._tick_down)
            if diff > 10 and not self._key_down:
                self._sent = False
                self._key_down = True
                l.debug('Key down:', self._pk)
            if diff > self._lng_delay and not self._sent:
                l.debug('Key longpress:', self._pk)
                self._sent = True
                return self._pk, True

        if self._tick_up:
            diff = time.ticks_diff(time.ticks_ms(), self._tick_up)
            if diff > 10:
                l.debug('Key up:', self._pk)

                self._tick_up = None
                self._tick_down = None
                self._key_down = False

                if not self._sent:
                    return self._pk, False

        return None, False
