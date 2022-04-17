import xml.etree.ElementTree as ET
import sys
from interpret import ERR_XML_STRUC


class Instruction:
    _valid_Opcodes = (
        'MOVE', 'CREATEFRAME', 'PUSHFRAME', 'POPFRAME', 'DEFVAR', 'CALL', 'RETURN', 'PUSHS', 'POPS', 'ADD', 'SUB',
        'MUL', 'IDIV', 'LT', 'GT', 'EQ', 'AND', 'OR', 'NOT', 'INT2CHAR', 'STRI2INT', 'READ', 'WRITE', 'CONCAT',
        'STRLEN', 'GETCHAR', 'SETCHAR', 'TYPE', 'LABEL', 'JUMP', 'JUMPIFEQ', 'JUMPIFNEQ', 'EXIT', 'DPRINT', 'BREAK')

    def __init__(self, order, opcode):
        self.order = order
        self.opcode = opcode

    @staticmethod
    def is_instruction_valid(instruction: ET.Element):
        if 'order' not in instruction.keys() or 'opcode' not in instruction.keys():
            sys.stderr.write('Instruction %s is missing order or opcode argument.\n' % instruction.tag)
            exit(ERR_XML_STRUC)
        if not instruction.get('order').isnumeric():
            sys.stderr.write('Instruction does not have integer value for attribute order: %s.\n' % instruction.get('order'))
            exit(ERR_XML_STRUC)
        if int(instruction.get('order')) < 0:
            sys.stderr.write(
                'Instruction cannot have negative order value :%s.\n' % instruction.get('order'))
            exit(ERR_XML_STRUC)
        if instruction.get('opcode').upper() not in Instruction._valid_Opcodes:
            sys.stderr.write('Instruction does not have valid opcode: %s.\n' % instruction.get('opcode'))
            exit(ERR_XML_STRUC)
