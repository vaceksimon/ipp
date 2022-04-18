import re
from typing import Dict
import sys
import xml.etree.ElementTree as ET

import Instruction as ins
from errorCodes import ERR_OPERAND
from errorCodes import ERR_XML_STRUC
from errorCodes import ERR_SEMANTICS


class InstructionLabel(ins.Instruction):
    """InstructionLabel has all methods regarding label, including a dictionary of all labels in the program."""
    __labels = {}

    def __init__(self):
        # todo bude se nekdy delat instance?
        super()

    @classmethod
    def get_labels(cls) -> Dict:
        """

        :return: Returns the labels dictionary
        """
        return cls.__labels

    @classmethod
    def add_label(cls, order: int, lbl: str) -> None:
        """Adds a label to the dictionary.

        If a label name is not unique, the interpret is terminated.

        :param order: Order value of the label
        :param lbl: Name of the label
        :return:
        """
        if lbl in cls.__labels.values():
            sys.stderr.write('Label: "%s" is already defined.\n' % lbl)
            exit(ERR_OPERAND)
        cls.__labels[order] = lbl

    @staticmethod
    def check_instruction(instruction: ET.Element) -> None:
        """Checks, that the instruction has all the attributes and appropriate values.

        :param instruction: An instruction todo
        :return:
        """
        i = 0
        for arg in instruction.findall('./'):
            # todo error codes
            ins.Instruction.is_arg_valid(arg)
            if arg.tag != 'arg1':
                sys.stderr.write('Instruction label must have only argument arg1.\n')
                exit(ERR_XML_STRUC)
            if arg.get('type') != 'label':
                sys.stderr.write('Label can have argument only of a type label, not: %s\n' % arg.get('type'))
                exit(ERR_OPERAND)
            if arg.text is None or not re.search('^[_\\-$&%*!?a-zA-Z][_\\-$&%*!?a-zA-Z\d]*$', arg.text):
                sys.stderr.write('Invalid name for label: %s.\n' % arg.text)
                exit(ERR_SEMANTICS)
            i = i + 1

        if i != 1:
            sys.stderr.write('Instruction label must have one argument.\n')
            exit(ERR_XML_STRUC)
