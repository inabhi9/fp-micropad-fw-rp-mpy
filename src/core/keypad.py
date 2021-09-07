from machine import Timer

from libs.adafruit_matrixkeypad import Matrix_Keypad


class Keypad(Matrix_Keypad):
    _register_key = False
    _long_press = False
    _key_down = False
    _key_up = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tm_short = Timer()
        self._tm_long = Timer()

    @property
    def pressed_key(self):
        pressed_key = (self.pressed_keys or [None])[0]

        if pressed_key:
            self._key_down = True
            self._register_key = False
            self._long_press = False
            self._tm_short.init(period=10, mode=Timer.ONE_SHOT, callback=self._on_short_tm)
            self._tm_long.init(period=250, mode=Timer.ONE_SHOT, callback=self._on_long_tm)

        while self._key_down and pressed_key:
            self._key_down = len(self.pressed_keys) > 0

        if not self._register_key:
            pressed_key = None

        return pressed_key, self._long_press

    def _on_short_tm(self, *args):
        self._register_key = True

    def _on_long_tm(self, *args):
        self._long_press = True
