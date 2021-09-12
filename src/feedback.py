import uasyncio
from machine import Pin, PWM

from core import state


class Feedback:
    _running = False
    LED_PIN_BLUE = 13
    LED_PIN_RED = 14

    def __init__(self, visual=True, haptic=False):
        self._visual = visual
        self._haptic = haptic

    async def task(self):
        self._running = True
        while self._running:
            self._schedule_task(state.BOOT_AUTH, False, self._task_boot_auth)
            self._clear_task(state.BOOT_AUTH, True, self._task_boot_auth)

            self._schedule_task(state.BOOT_AUTH_INVALID, True, self._task_boot_auth_invalid)
            self._clear_task(state.BOOT_AUTH_INVALID, False, self._task_boot_auth_invalid)

            self._schedule_task(state.FP_VERIFIED, True, self._task_fp_verified)
            self._clear_task(state.FP_VERIFIED, False, self._task_fp_verified)

            self._schedule_task(state.FP_VERIFIED_INVALID, True, self._task_fp_verified_invalid)
            self._clear_task(state.FP_VERIFIED_INVALID, False, self._task_fp_verified_invalid)

            await uasyncio.sleep_ms(10)

    async def _task_boot_auth(self):
        # Construct PWM object, with LED on Pin(25).
        pwm = PWM(Pin(self.LED_PIN_BLUE))

        # Set the PWM frequency.
        pwm.freq(1000)

        while state.BOOT_AUTH is False:
            # Fade the LED in and out a few times.
            duty = 0
            direction = 1
            for _ in range(2 * 256):

                if state.BOOT_AUTH:
                    Pin(self.LED_PIN_BLUE, mode=Pin.OUT).low()
                    break

                duty += direction
                if duty > 255:
                    duty = 255
                    direction = -1
                elif duty < 0:
                    duty = 0
                    direction = 1
                pwm.duty_u16(duty * duty)
                await uasyncio.sleep_ms(5)

    async def _task_boot_auth_invalid(self):
        pin = Pin(self.LED_PIN_RED, mode=Pin.OUT)
        pin.high()
        await uasyncio.sleep(2)
        pin.low()

    async def _task_fp_verified_invalid(self):
        await self._task_boot_auth_invalid()

    async def _task_fp_verified(self):
        # Construct PWM object, with LED on Pin(25).
        pwm = PWM(Pin(self.LED_PIN_BLUE))

        # Set the PWM frequency.
        pwm.freq(50)

        while state.FP_VERIFIED:
            # Fade the LED in and out a few times.
            duty = 0
            direction = 1
            for _ in range(2 * 256):
                duty += direction
                if duty > 255:
                    duty = 255
                    direction = -1
                elif duty < 0:
                    duty = 0
                    direction = 1
                pwm.duty_u16(duty * duty)
                await uasyncio.sleep_ms(1)

    def _clear_all(self):
        Pin(self.LED_PIN_BLUE, mode=Pin.OUT).low()
        Pin(self.LED_PIN_RED, mode=Pin.OUT).low()

    def _schedule_task(self, state_val, eq_val, task):
        task_inst_name = 'taskinst_%s' % task.__name__
        task_inst = getattr(self, task_inst_name, None)
        if state_val == eq_val and not task_inst:
            task_inst = uasyncio.create_task(task())
            setattr(self, task_inst_name, task_inst)

    def _clear_task(self, state_val, eq_val, task):
        task_inst_name = 'taskinst_%s' % task.__name__
        task_inst = getattr(self, task_inst_name, None)
        if state_val == eq_val and task_inst:
            del task_inst
            setattr(self, task_inst_name, None)
