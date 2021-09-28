from micropython import const

# Keypad config

keypad_cols = (0, 1, 2, 3)
keypad_rows = (4, 5, 7, 6)

keypad_keymap = [('1', '2', '3', 'A'),
                 ('4', '5', '6', 'B'),
                 ('*', '0', '#', 'D'),
                 ('7', '8', '9', 'C')]

# HID Macro config

hid_macro_short_modifier = 'CTRL'
hid_macro_long_modifier = 'ALT-CTRL'

default_password = '123456'

DELAY_AFTER_INVALID_BOOT_AUTH = const(3)  # seconds

FP_IRQ_PIN = const(11)
FP_UART_ID = const(1)
FP_TX_PIN = const(8)
FP_RX_PIN = const(9)
FP_BAUD_RATE = const(57600)
FP_TBASE = const(15)  # Transistor Base

VIBRATOR_PIN = const(16)
LED_RGB_PINS = 21, 20, 19

FP_AUTH_KP_INPUT_TIMEOUT = const(3)  # seconds

HAPTIC_FEEDBACK = True
VISUAL_FEEDBACK = True
