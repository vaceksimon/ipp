import re
import sys
from typing import List
from errorCodes import *
import Frame as Fr


class Variable:
    def __init__(self, name: str, value: str = None):
        self.name = name
        self.value = value
        if value is None:
            return
        if value.isnumeric():
            self.typ = 'int'
        elif value == 'true' or value == 'false':
            self.typ = 'bool'
        elif value == 'nil':
            self.typ = 'nil'
        else:
            self.typ = "string"

    def get_name(self) -> str:
        return self.name

    def get_var_ids(self) -> str:
        var_ids = re.split('@', self.name)
        if len(var_ids) != 2:
            sys.stderr.write('Invalid variable identifier: %s\n' % self.name)
            exit(ERR_MISSING_VALUE)
        if not re.match('^[GLT]F$', var_ids[0]):
            sys.stderr.write('Invalid frame identifier: %s.\n' % var_ids[0])
            exit(ERR_MISSING_VALUE)
        if not re.search('^[_\\-$&%*!?a-zA-Z][_\\-$&%*!?a-zA-Z\d]*$', var_ids[1]):
            sys.stderr.write('Invalid variable identifier: %s\n' % self.name)
            exit(ERR_MISSING_VALUE)
        self.name = var_ids[1]
        return var_ids[0]

    def defvar(self):
        frame_id = self.get_var_ids()
        Fr.Frame.frame_for_name(frame_id).add_variable(self)

    def move(self):
        frame_id = self.get_var_ids()
        var = Fr.Frame.frame_for_name(frame_id).find_variable(self.get_name())

        if var is None:
            sys.stderr.write('There is no variable %s%s.\n' % (frame_id, self.get_name()))
            exit(ERR_VARIABLE)
        var.value = self.value
        var.typ = self.typ

    def is_init(self) -> bool:
        return self.value is not None and self.typ is not None

