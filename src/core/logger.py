import time


class Logger:
    DEBUG = 0
    INFO = 1
    WARN = 2
    ERROR = 3

    def __init__(self, level):
        self.level = level

    def info(self, *msg):
        if self.level <= self.INFO:
            self.print_with_time('info:', *msg)

    def warn(self, *msg):
        if self.level <= self.WARN:
            self.print_with_time('warn:', *msg)

    def debug(self, *msg):
        if self.level <= self.DEBUG:
            self.print_with_time('debug:', *msg)

    def error(self, *msg):
        if self.level <= self.ERROR:
            self.print_with_time('err:', *msg)

    def serial_info(self, event, status='', **kwargs):
        self._serial_print('info', event, status=status, **kwargs)

    def serial_err(self, event, status='', **kwargs):
        self._serial_print('err', event, status=status, **kwargs)

    def _serial_print(self, t, event, status='', **kwargs):
        p = '%s:/res/%s' % (t, event)
        if status:
            p += '/' + status

        if kwargs:
            args = ['%s:%s' % (k, v) for k, v in kwargs.items()]
            p += ',' + ','.join(args)

        self.print(p)

    def print(self, *msgs):
        print(*msgs)

    def print_with_time(self, *msgs):
        print(time.time(), *msgs)


l = Logger(Logger.DEBUG)
