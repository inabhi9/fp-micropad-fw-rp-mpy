import uasyncio

import config
from cmd import CMD
from core import l, state
from db import DB
from feedback import Feedback
from fingerprint import Fingerprint
from keypad_hid import KeypadHID

db = DB()
feedback = Feedback()
cmd = CMD(db)
keypad_hid = KeypadHID(db)
fingerprint = Fingerprint()

l.info('Started...')


async def auth_on_start():
    l.info('Please auth')
    the_password = ''

    while True:
        key, _ = keypad_hid._keypad.pressed_key

        if key == '#':
            if db.verify_password(the_password):
                l.serial_info('fp-auth', 'done')
                state.BOOT_AUTH = True
                state.BOOT_AUTH_INVALID = False
                break
            else:
                l.serial_err('fp-auth', 'invalid')
                the_password = ''
                state.BOOT_AUTH_INVALID = True
                await uasyncio.sleep(config.DELAY_AFTER_INVALID_BOOT_AUTH)
                state.BOOT_AUTH_INVALID = False
        elif key == 'C':
            the_password = ''
            l.debug('fp-auth', 'clear')
        elif key:
            the_password += key

        await uasyncio.sleep_ms(10)

    return True


async def main():
    uasyncio.create_task(feedback.task())
    uasyncio.create_task(cmd.task())

    auth_task = uasyncio.create_task(auth_on_start())
    await auth_task

    uasyncio.create_task(fingerprint.task())
    uasyncio.create_task(keypad_hid.task())

    while True:
        await uasyncio.sleep(10)

uasyncio.run(main())

