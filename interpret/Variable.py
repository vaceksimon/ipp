import re
import sys
from errorCodes import ERR_RUNTIME
from errorCodes import ERR_FRAME
from errorCodes import ERR_VARIABLE
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

    def defvar(self):
        var_ids = re.split('@', self.name)
        if len(var_ids) != 2:
            sys.stderr.write('Invalid variable identifier in DEFVAR: %s\n' % self.name)
            exit(ERR_RUNTIME)
        if not re.match('^[GLT]F$', var_ids[0]):
            sys.stderr.write('Invalid frame identifier in DEFVAR: %s.\n' % var_ids[0])
            exit(ERR_RUNTIME)
        if not re.search('^[_\\-$&%*!?a-zA-Z][_\\-$&%*!?a-zA-Z\d]*$', var_ids[1]):
            sys.stderr.write('Invalid variable identifier in DEFVAR: %s\n' % self.name)
            exit(ERR_RUNTIME)

        self.name = var_ids[1]
        if var_ids[0] == 'GF':
            Fr.Frame.get_global().add_variable(self)
        elif var_ids[0] == 'LF':
            Fr.Frame.check_local_frame()
            Fr.Frame.top_local_frame().add_variable(self)
        else:
            Fr.Frame.check_tmp_frame()
            Fr.Frame.get_tmp().add_variable(self)

    def move(self):
        var_ids = re.split('@', self.name)
        if len(var_ids) != 2:
            sys.stderr.write('Invalid variable identifier in MOVE: %s\n' % self.name)
            exit(ERR_RUNTIME)
        if not re.match('^[GLT]F$', var_ids[0]):
            sys.stderr.write('Invalid frame identifier in MOVE: %s.\n' % var_ids[0])
            exit(ERR_RUNTIME)
        self.name = var_ids[1]
        if var_ids[0] == 'GF':
            var = Fr.Frame.get_global().find_variable(self.get_name())
        elif var_ids[0] == 'TF':
            var = Fr.Frame.get_tmp().find_variable(self.get_name())
        else:
            var = Fr.Frame.top_local_frame().find_variable(self.get_name())

        if var is None:
            sys.stderr.write('There is no variable %s.\n' % self.get_name())
            exit(ERR_VARIABLE)
        var.value = self.value
        var.typ = self.typ

