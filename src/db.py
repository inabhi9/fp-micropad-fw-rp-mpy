import json
import os

import ubinascii

from libs import maes


class DB:
    _db_dir = '/.db'
    _password = None  # encryption key

    def __init__(self):
        try:
            os.mkdir(self._db_dir)
        except OSError:
            pass

    @property
    def is_initialized(self):
        filename = self._get_filename('.init')

        return self._file_exists(filename)

    def init(self, passwd: str):
        pwd = self._passwd_to_bytes(passwd)

        content = os.urandom(64)

        filename = self._init_filename
        with open(filename, 'w') as f:
            f.write(ubinascii.hexlify(content) + '\n')

            ciphered = ubinascii.hexlify(self._cryptor(pwd).encrypt(content))
            f.write(ciphered + '\n')

    def verify_password(self, passwd: str):
        pwd = self._passwd_to_bytes(passwd)

        filename = self._init_filename
        with open(filename, 'r') as f:
            content = f.readline().replace('\n', '')

            ciphered = ubinascii.unhexlify(f.readline().replace('\n', ''))
            deciphered = ubinascii.hexlify(self._cryptor(pwd).decrypt(ciphered)).decode()

            del ciphered

        if content == deciphered:
            self._password = pwd

        return content == deciphered

    def set(self, index: str, passwd: str, **kwargs):
        filename = self._get_filename(index)

        kwargs['passwd'] = self._encrypt(passwd)

        f = open(filename, 'w')
        json.dump(kwargs, f)

        f.close()

    def get(self, index: str):
        filename = self._get_filename(index)

        try:
            f = open(filename, 'r')
        except OSError:
            return None

        data = json.load(f)
        f.close()

        data['passwd'] = self._decrypt(data['passwd'])

        return data

    def _decrypt(self, s: str) -> str:
        assert self._password

        return self._array_tostring(self._cryptor().decrypt(ubinascii.unhexlify(s)))

    def _encrypt(self, s: str) -> bytes:
        assert self._password

        dummy = bytearray()
        s_len = len(s)
        s_mod = s_len % 16
        if s_mod:
            dummy = bytearray(16 - s_mod)

        s = bytearray(s) + dummy

        return ubinascii.hexlify(self._cryptor().encrypt(s))

    def erase(self):
        for f in os.listdir(self._db_dir):
            os.rmdir(self._db_dir + '/%s' % f)

    def _get_filename(self, index: str) -> str:
        if len(index) > 10:
            raise Exception('Index must be less than 10 characters')

        return self._db_dir + '/%s' % index

    @property
    def _init_filename(self):
        return self._get_filename('.init')

    def _file_exists(self, filename):
        try:
            f = open(filename, 'r+b')
            f.close()
            return True
        except OSError:
            return False

    def _array_tostring(self, array_data):
        _string = ""
        for _array in array_data:
            _string = _string + chr(_array)
        return _string.strip('\x00')

    def _passwd_to_bytes(self, passwd: str):
        if len(passwd) > 16:
            raise ValueError('Password must be less than 16 characters in length')

        pwd = bytearray(passwd) + bytearray(15)

        return pwd[:16]

    def _cryptor(self, pwd=None):
        return maes.new(pwd or self._password, maes.MODE_ECB)
