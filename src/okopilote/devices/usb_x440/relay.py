from .board import Board
from .exceptions import RelayError

from okopilote.devices.common.abstract import AbstractRelay


class Relay(AbstractRelay):

    def __init__(self, board_url, relay_number, normally_open):
        self.board = Board.get_board(board_url)
        if relay_number < 1 or relay_number > self.board.NB_RELAYS:
            raise RelayError(
                "Relay number out of range (1-{}): {}".format(
                    self.board.NB_RELAYS, relay_number
                )
            )
        self.relay_num = relay_number
        self.normally_open = normally_open

    def is_on(self):
        return self.board.is_activated(self.relay_num) == self.normally_open

    def switch_off(self):
        if self.normally_open:
            self.board.deactivate(self.relay_num)
        else:
            self.board.activate(self.relay_num)

    def switch_on(self):
        if self.normally_open:
            self.board.activate(self.relay_num)
        else:
            self.board.deactivate(self.relay_num)
