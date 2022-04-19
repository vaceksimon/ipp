import xml.etree.ElementTree as ET
import sys
import re
from typing import List, Dict
from errorCodes import *
import Frame as Fr
import Variable as Var


class Instruction:
    """Represents a single instruction."""

    _valid_Opcodes = (
        'MOVE', 'CREATEFRAME', 'PUSHFRAME', 'POPFRAME', 'DEFVAR', 'CALL', 'RETURN', 'PUSHS', 'POPS', 'ADD', 'SUB',
        'MUL', 'IDIV', 'LT', 'GT', 'EQ', 'AND', 'OR', 'NOT', 'INT2CHAR', 'STRI2INT', 'READ', 'WRITE', 'CONCAT',
        'STRLEN', 'GETCHAR', 'SETCHAR', 'TYPE', 'LABEL', 'JUMP', 'JUMPIFEQ', 'JUMPIFNEQ', 'EXIT', 'DPRINT', 'BREAK')

    def __init__(self, opcode: str, args: List):
        self._args: List = []
        for arg in args:
            self._args.append(arg)
        self._opcode = opcode

    @staticmethod
    def create_arith_ins(opcode: str, arguments: List[ET.Element]):
        """Factory method for an arithmetic instruction and its arguments.

        Performs check on instruction arguments and stores their value in the object.

        :param opcode: Name (operation code) of instruction
        :param arguments: List of arguments still in XML representation
        :return: Object of a type Instruction
        """
        if arguments[0].get('type') != 'var':
            sys.stderr.write('Arg1 must be the type var for arithmetic instruction: %s\n')
            exit(ERR_OPERAND)

        # Finds instruction in a given frame
        var = arguments[0].text
        var = Var.Variable(var)
        var_frame = var.get_var_ids()
        var_frame = Fr.Frame.frame_for_name(var_frame)
        var = var_frame.find_variable(var.get_name())

        # Checks for valid argument types
        if var is None:
            sys.stderr.write('Variable does not exist\n')
            exit(ERR_VARIABLE)
        if arguments[1].get('type') != arguments[2].get('type'):
            sys.stderr.write('Operands must be the same type\n')
            exit(ERR_OPERAND)
        if arguments[1].get('type') not in 'int':
            sys.stderr.write('Operands must be type int\n')
            exit(ERR_OPERAND)

        # Checks that the value is (negative) integer
        value1 = arguments[1].text
        value2 = arguments[2].text
        if value1[0] == '-':
            value1 = arguments[1].text[1:]
        if value2[0] == '-':
            value2 = arguments[2].text[1:]
        if not value1.isnumeric() or not value2.isnumeric():
            sys.stderr.write('Operands must have int value\n')
            exit(ERR_OPERAND)

        return Instruction(opcode, [var, arguments[1].text, arguments[2].text])

    def exec_arithmetic_ins(self):
        """Performs the arithmetic operation.

        :return: None
        """
        if self._opcode == 'ADD':
            self._args[0].value = int(self._args[1]) + int(self._args[2])
        elif self._opcode == 'SUB':
            self._args[0].value = int(self._args[1]) - int(self._args[2])
        elif self._opcode == 'MUL':
            self._args[0].value = int(self._args[1]) * int(self._args[2])
        elif self._opcode == 'IDIV':
            if self._args[2] == '0':
                sys.stderr.write('Cannot divide by zero.\n')
                exit(ERR_INVALID_OPERAND)
            self._args[0].value = int(self._args[1]) // int(self._args[2])

    @staticmethod
    def check_data_types(typ: str, value: str):
        """Terminates the script if value is not of a given type.

        :param typ: Type, which the value should be of
        :param value: Value that should be checked
        :return: None
        """
        if typ == 'nil':
            if value != 'nil':
                sys.stderr.write('Type nil can hold only value nil.\n')
                exit(ERR_INVALID_OPERAND)
        elif typ == 'int':
            if value[0] == '-':
                value = value[1:]
            if not value.isnumeric():
                sys.stderr.write('Type int can hold only integer values.\n')
                exit(ERR_INVALID_OPERAND)
        elif typ == 'bool':
            if value not in ['true', 'false']:
                sys.stderr.write('Type bool can hold only values true or false.\n')
                exit(ERR_INVALID_OPERAND)

    @staticmethod
    def is_instruction_valid(instruction: ET.Element) -> None:
        """Checks if the instruction has all attributes and correct values.

        If a problem is found, interpret is terminated with a proper error message.

        :param instruction: A single instruction from the xml file
        :return:
        """
        if instruction.tag != 'instruction':
            sys.stderr.write('Program con contain only instructions, not: %s\n' % instruction.tag)
            exit(ERR_XML_STRUC)
        if 'order' not in instruction.keys() or 'opcode' not in instruction.keys():
            sys.stderr.write('Instruction %s is missing order or opcode argument.\n' % instruction.get('opcode'))
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
        """Checks if the instruction argument has all attributes and their correct values.

        If a problem is found, interpret is terminated with a proper error message.

        :param argument: Argument of an instruction
        :return:
        """
        if not re.search('\Aarg[1-3]\Z', argument.tag):
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
    def check_args(args: List[ET.Element], arg_count: int, instruction_name: str = 'Instruction') -> List[ET.Element]:
        """Performs a check on a list of arguments.

        Checks that the list of arguments is correctly tagged, contains all mandatory attributes and does not have any
        subelements. If a problem is found, interpret is terminated.

        :param args: List of arguments in their Element representation
        :param arg_count: Number of arguments the instruction is supposed to have
        :param instruction_name: Name of the instruction for error messages
        :return: Unmodified list of args obtained as a parameter
        """
        if len(args) != arg_count:
            sys.stderr.write('Instruction %s must have %d arguments.\n' % (instruction_name, arg_count))
            exit(ERR_XML_STRUC)
        i = 1
        for arg in args:
            if arg is None:
                sys.stderr.write('%s must have argument %d arguments.\n' % (instruction_name, arg_count))
                exit(ERR_XML_STRUC)
            if arg.tag != 'arg%d' % i:
                sys.stderr.write('Got %s whe arg%d was expected.\n' % (arg.tag, i))
                exit(ERR_XML_STRUC)
            Instruction.check_arg_valid(arg)
            i = i + 1
        return args
