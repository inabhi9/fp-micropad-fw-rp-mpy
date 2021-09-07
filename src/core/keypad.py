import time

from libs.adafruit_matrixkeypad import Matrix_Keypad
from .logger import l


class Keypad(Matrix_Keypad):
    _tick_down = None
    _tick_up = None
    _pk = None
    _sent = False

    def __init__(self, *args, **kwargs):
        self._lng_delay = kwargs.get('long_press_delay') or 250  # ms
        super().__init__(*args, **kwargs)

    @property
    def pressed_key(self):
        pressed_key = (self.pressed_keys or [None])[0]

        if not pressed_key and self._tick_down and not self._tick_up:
            self._tick_up = time.ticks_ms()

        if pressed_key and not self._tick_down:
            self._pk = pressed_key
            self._tick_down = time.ticks_ms()

        if self._tick_down:
            diff = time.ticks_diff(time.ticks_ms(), self._tick_down)
            if diff == 10:
                self._sent = False
                l.debug('Key down:', self._pk)
            if diff == self._lng_delay:
                l.debug('Key longpress:', self._pk)
                self._sent = True
                time.sleep_ms(10)  # otherwise freezes for some reason
                return self._pk, True

        if self._tick_up:
            diff = time.ticks_diff(time.ticks_ms(), self._tick_up)
            if diff == 10:
                l.debug('Key up:', self._pk)

                self._tick_up = None
                self._tick_down = None

                if not self._sent:
                    time.sleep_ms(10)  # otherwise freezes for some reason
                    return self._pk, False

        return None, False
