import hid
import machine
from machine import Pin

import config
from db import DB

# Fix key codes, original was set to EU keyboards
hid.SetKeyCode(0x1E, '!@#$%^&*()', hid.MOD_LSHIFT)

# Why not!
machine.freq(240000000)

# It's needed to make it easier
db = DB()
if not db.is_initialized:
    db.init(config.default_password)

Pin(config.VIBRATOR_PIN, mode=Pin.OUT).high()
