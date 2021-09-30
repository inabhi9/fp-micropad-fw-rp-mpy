import hid
import machine
from machine import Pin

import config
from db import DB

# Fix key codes, original was set to EU keyboards
hid.SetKeyCode(0x1E, '!@#$%^&*()', hid.MOD_LSHIFT)

# Why not!
machine.freq(200000000)

# It's needed to make it easier
db = DB()
if not db.is_initialized:
    db.init(config.default_password)

Pin(config.VIBRATOR_PIN, mode=Pin.OUT).high()

Pin(25, mode=Pin.OUT).high()

# to reduce noise
unused_pins = [28, 27, 26, 22, 18, 17, 14, 10, 12, 13, 14]
[Pin(pin, mode=Pin.IN, pull=Pin.PULL_UP) for pin in unused_pins]
