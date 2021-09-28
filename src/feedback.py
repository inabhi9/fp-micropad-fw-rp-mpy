import uasyncio

import config
from core import events, feedback_utils
from core import state, l
from core.feedback_utils import vibrator_on, vibrator_off


class Feedback:
    _running = False

    async def task(self):
        self._running = True

        boot_auth_prev_state = None
        boot_auth_invalid_prev_state = state.BOOT_AUTH_INVALID
        fp_auth_prev_state = state.FP_VERIFIED
        fp_auth_invalid_prev_state = state.FP_VERIFIED_INVALID

        while self._running:
            awaitables = []

            if boot_auth_prev_state != state.BOOT_AUTH:
                awaitables.append(events.post_boot_auth_change.send(boot_auth=state.BOOT_AUTH))

            if fp_auth_prev_state != state.FP_VERIFIED and state.FP_VERIFIED:
                awaitables.append(events.fp_auth.send())

            if (fp_auth_invalid_prev_state != state.FP_VERIFIED_INVALID
                    and state.FP_VERIFIED_INVALID):
                awaitables.append(events.fp_auth_invalid.send())

            if boot_auth_invalid_prev_state != state.BOOT_AUTH_INVALID and state.BOOT_AUTH_INVALID:
                awaitables.append(events.boot_auth_invalid.send())

            boot_auth_prev_state = state.BOOT_AUTH
            boot_auth_invalid_prev_state = state.BOOT_AUTH_INVALID
            fp_auth_prev_state = state.FP_VERIFIED
            fp_auth_invalid_prev_state = state.FP_VERIFIED_INVALID

            [uasyncio.create_task(t) for t in awaitables]
            await uasyncio.sleep_ms(10)


@events.on(events.post_boot_auth_change)
async def haptic_on_boot_auth(**kwargs):
    if kwargs.get('boot_auth') is True:
        l.debug('haptic_on_boot_auth')
        vibrator_on()
        await uasyncio.sleep_ms(200)
        vibrator_off()


@events.on(events.fp_auth)
async def haptic_on_fp_auth(**kwargs):
    l.debug('haptic_on_fp_auth')
    vibrator_off()
    await uasyncio.sleep_ms(10)
    vibrator_on()
    await uasyncio.sleep_ms(150)
    vibrator_off()


@events.on([events.fp_auth_invalid, events.boot_auth_invalid])
async def haptic_on_fp_auth_invalid(**kwargs):
    for i in range(2):
        l.debug('haptic_on_fp_auth_invalid')
        vibrator_on()
        await uasyncio.sleep_ms(100)
        vibrator_off()
        await uasyncio.sleep_ms(200)


@events.on(events.post_boot_auth_change)
async def visual_on_boot_auth(**kwargs):
    if kwargs.get('boot_auth') is False:
        return

    feedback_utils.led_on(feedback_utils.LED_PIN_GREEN)
    await uasyncio.sleep_ms(500)
    feedback_utils.led_off(feedback_utils.LED_PIN_GREEN)


@events.on(events.post_boot_auth_change)
async def visual_on_boot_not_auth(**kwargs):
    if kwargs.get('boot_auth') is True:
        return

    while state.BOOT_AUTH is False:
        await feedback_utils.pwm(feedback_utils.LED_PIN_BLUE, peak=100, delay_cycle=5,
                                 break_on=lambda: state.BOOT_AUTH)


@events.on(events.fp_auth)
async def visual_on_fp_auth(**kwargs):
    while state.FP_VERIFIED:
        await feedback_utils.pwm(feedback_utils.LED_PIN_GREEN, peak=100, delay_cycle=2,
                                 break_on=lambda: not state.FP_VERIFIED)


@events.on(events.fp_auth_invalid)
async def visual_on_fp_auth_invalid(**kwargs):
    feedback_utils.led_on(feedback_utils.LED_PIN_RED)
    await uasyncio.sleep(1)
    feedback_utils.led_off(feedback_utils.LED_PIN_RED)


@events.on(events.keypress)
async def visual_on_keypress(**kwargs):
    feedback_utils.led_on(feedback_utils.LED_PIN_BLUE)
    await uasyncio.sleep_ms(10)
    feedback_utils.led_off(feedback_utils.LED_PIN_BLUE)


@events.on(events.boot_auth_invalid)
async def visual_on_boot_auth_invalid(**kwargs):
    feedback_utils.led_on(feedback_utils.LED_PIN_RED)
    await uasyncio.sleep(config.DELAY_AFTER_INVALID_BOOT_AUTH)
    feedback_utils.led_off(feedback_utils.LED_PIN_RED)
