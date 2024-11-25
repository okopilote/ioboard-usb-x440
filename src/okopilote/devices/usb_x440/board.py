import logging
from serial import serial_for_url, EIGHTBITS, STOPBITS_ONE
from threading import Lock

# from serial.serialutil import SerialException
from time import sleep

from .exceptions import RelayError

logger = logging.getLogger(__name__)


class Board:
    NB_RELAYS = 4
    SERIAL_P = {
        "baudrate": 9600,
        "bytesize": EIGHTBITS,
        "stopbits": STOPBITS_ONE,
        "timeout": 1,
    }
    _boards = {}
    _boards_lock = Lock()

    @classmethod
    def get_board(cls, url):
        with cls._boards_lock:
            try:
                return cls._boards[url]
            except KeyError:
                return Board(url)

    def __init__(self, url="/dev/ttyUSB0"):
        self.serial_p = self.SERIAL_P.copy()
        self.url = url
        self.devlck = Lock()
        type(self)._boards[url] = self

    def _relay_state(self, ser, relay_num):
        ans = None
        ser.write(b"?")
        sleep(0.3)
        for i in range(30):
            if ans and ans.startswith("S>"):
                return bool(int(ans[-relay_num]))
            elif ans == "":
                raise RelayError(
                    f"Device {self.url}: end of buffer reached before "
                    + 'finding a "S>"'
                )
            else:
                ans = ser.read_until(b"\r").decode().rstrip("\r")
        raise RelayError("Too many buffer reads (30). Give up now")

    def _set_relay(self, relay_num, value):
        logger.info("USB-X440: send S{}{}".format(relay_num, int(value)))
        with self.devlck:
            with serial_for_url(self.url, **self.serial_p) as ser:
                ser.write("S{}{}".format(relay_num, int(value)).encode())
                sleep(0.3)
                # if value != self._relay_state(ser, relay_num):
                #    raise RelayError('Relay {} is still {}activated'
                #                     .format(relay_num, 'de' if value else ''))

    def is_activated(self, relay_num):
        with self.devlck:
            with serial_for_url(self.url, **self.serial_p) as ser:
                return self._relay_state(ser, relay_num)

    def activate(self, relay_num):
        self._set_relay(relay_num, True)

    def deactivate(self, relay_num):
        self._set_relay(relay_num, False)

    def enable_memory(self, value=True):
        with self.devlck:
            with serial_for_url(self.url, **self.serial_p) as ser:
                ser.write("M{}".format(int(value)).encode())
