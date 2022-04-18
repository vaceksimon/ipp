import re
import sys
from errorCodes import ERR_RUNTIME
from errorCodes import ERR_FRAME
import Frame as Fr


class Variable:
    def __init__(self, name: str, typ: str = None, value: str = None):
        self.name = name
        self.typ = typ
        self.value = value

    def get_name(self) -> str:
        return self.name

    def defvar(self):
        tmp = re.split('@', self.name)
        if len(tmp) != 2:
            sys.stderr.write('Invalid variable identifier in DEFVAR: %s\n' % self.name)
            exit(ERR_RUNTIME)
        if not re.match('^[GLT]F$', tmp[0]):
            sys.stderr.write('Invalid frame identifier in DEFVAR: %s.\n' % tmp[0])
            exit(ERR_RUNTIME)
        if not re.search('^[_\\-$&%*!?a-zA-Z][_\\-$&%*!?a-zA-Z\d]*$', tmp[1]):
            sys.stderr.write('Invalid variable identifier in DEFVAR: %s\n' % self.name)
            exit(ERR_RUNTIME)

        if tmp[0] == 'GF':
            Fr.Frame.get_global().add_variable(self)
        elif tmp[0] == 'LF':
            if Fr.Frame.top_local_frame() is None:
                sys.stderr.write('There is no local frame on stack to define variable: %s' % self.get_name())
                exit(ERR_FRAME)
            Fr.Frame.top_local_frame().add_variable(self)
        else:
            if Fr.Frame.get_tmp() is None:
                sys.stderr.write('The temporary frame must be first created to define variable: %s' % self.get_name())
                exit(ERR_FRAME)
            Fr.Frame.get_tmp().add_variable(self)
