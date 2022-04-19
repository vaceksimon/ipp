import xml.etree.ElementTree as ET
import sys
from errorCodes import ERR_XML_STRUC
import re
from typing import List


class Instruction:
    """Represents an instruction."""

    _valid_Opcodes = (
        'MOVE', 'CREATEFRAME', 'PUSHFRAME', 'POPFRAME', 'DEFVAR', 'CALL', 'RETURN', 'PUSHS', 'POPS', 'ADD', 'SUB',
        'MUL', 'IDIV', 'LT', 'GT', 'EQ', 'AND', 'OR', 'NOT', 'INT2CHAR', 'STRI2INT', 'READ', 'WRITE', 'CONCAT',
        'STRLEN', 'GETCHAR', 'SETCHAR', 'TYPE', 'LABEL', 'JUMP', 'JUMPIFEQ', 'JUMPIFNEQ', 'EXIT', 'DPRINT', 'BREAK')

    def __init__(self, order, opcode):
        self.order = order
        self.opcode = opcode

    @staticmethod
    def is_instruction_valid(instruction: ET.Element) -> None:
        """Checks if the instruction has all attirbutes and correct values.

        If a problem is found, interpret is terminated with a proper error message.

        :param instruction: A single instruction from the xml file
        :return:
        """
        if 'order' not in instruction.keys() or 'opcode' not in instruction.keys():
            sys.stderr.write('Instruction %s is missing order or opcode argument.\n' % instruction.tag)
            exit(ERR_XML_STRUC)
        if not instruction.get('order').isnumeric():
            sys.stderr.write(
                'Instruction does not have integer value for attribute order: %s.\n' % instruction.get('order'))
            exit(ERR_XML_STRUC)
        if int(instruction.get('order')) < 0:
            sys.stderr.write(
                'Instruction cannot have negative order value :%s.\n' % instruction.get('order'))
            exit(ERR_XML_STRUC)
        if instruction.get('opcode').upper() not in Instruction._valid_Opcodes:
            sys.stderr.write('Instruction does not have valid opcode: %s.\n' % instruction.get('opcode'))
            exit(ERR_XML_STRUC)

    @staticmethod
    def check_arg_valid(argument: ET.Element) -> None:
        """Checks if the instruction argument has all attirbutes and correct values.

        If a problem is found, interpret is terminated with a proper error message.

        :param argument: Argument of an instruction
        :return:
        """
        if not re.search('\Aarg[0-2]\Z', argument.tag):
            sys.stderr.write('Instructions can contain only arg elements.\n')
            exit(ERR_XML_STRUC)
        for attr in argument.findall('./'):
            sys.stderr.write('Instruction argument cannot contain any sub-elements.\n')
            exit(ERR_XML_STRUC)
        if len(argument.keys()) != 1:
            sys.stderr.write('Instruction argument must specify only a type.\n')
            exit(ERR_XML_STRUC)
        if 'type' not in argument.attrib:
            sys.stderr.write('Instruction argument must specify a type.\n')
            exit(ERR_XML_STRUC)
        if not re.search('int|bool|string|nil|label|type|var', argument.get('type')):
            sys.stderr.write('Invalid instruction argument type.\n')
            exit(ERR_XML_STRUC)

    @staticmethod
    def check_args(args: List[ET.Element], arg_count: int, instruction_name: str) -> List[ET.Element]:
        if len(args) != arg_count:
            sys.stderr.write('Instruction %s must have %d arguments.\n' % (instruction_name, arg_count))
            exit(ERR_XML_STRUC)
        for arg in args:
            if arg is None:
                sys.stderr.write('%s must have argument %d arguments\n' % (instruction_name, arg_count))
                exit(ERR_XML_STRUC)
            Instruction.check_arg_valid(arg)
        return args
