import select
import sys

import uasyncio

from core import l, state


class CMD:
    def __init__(self, db):
        self._db = db

    async def task(self):
        while True:
            await uasyncio.sleep_ms(100)

            s = ''
            while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                s += sys.stdin.read(1)

            if not s:
                continue

            parsed = self._parse(s)
            if not parsed:
                continue

            try:
                cmd = parsed['cmd']

                if cmd in ['pwd_store'] and not state.BOOT_AUTH:
                    self._invalid()
                    continue

                fn = getattr(self, cmd)
                fn(*parsed['args'])
            except AttributeError:
                self._invalid()

    def ping(self, *args):
        l.serial_info('ping', 'done', didComAuth=1, didFpAuth=int(state.BOOT_AUTH))

    def pwd_store(self, *args):
        try:
            index = args[0]
            pwd = args[1]
        except IndexError:
            self._invalid()
            return

        try:
            enter = args[2] == '1'
        except IndexError:
            enter = True

        if index == '-1':
            self._db.erase()
            self._db.init(pwd)
            self._db.verify_password(pwd)
        else:
            self._db.set(index, pwd, enter=enter)

        l.serial_info('pwd-store', 'done')

    def _invalid(self):
        l.serial_err('cmd', 'invalid', didComAuth=1)

    def _parse(self, s):
        parsed = s.split('/', 2)

        try:
            if parsed[1] != 'cmd':
                self._invalid()
                return
        except IndexError:
            return

        cmd, *args = parsed[2].split(',')

        return {
            'cmd': cmd.replace('-', '_'),
            'args': args
        }
