import re
import sys
from typing import Dict
import xml.etree.ElementTree as ET
import Instruction as ins
from errorCodes import *


class InstructionLabel(ins.Instruction):
    """InstructionLabel has all methods regarding label, including a dictionary of all labels in the program."""
    __labels: Dict[str, int] = {}

    @classmethod
    def get_labels(cls) -> Dict:
        """

        :return: Returns dictionary of labels
        """
        return cls.__labels

    @classmethod
    def order_for_label_name(cls, name_label: str) -> int:
        """Retrieves order of a label.

        :param name_label: Name of a label
        :return: Order of a label
        """
        return cls.__labels[name_label]

    @classmethod
    def add_label(cls, lbl: str, order: int) -> None:
        """Adds a label to the dictionary.

        If a label name is not unique, the interpret is terminated.

        :param order: Order value of the label
        :param lbl: Name of the label
        :return:
        """
        if lbl in cls.__labels.values():
            sys.stderr.write('Label: "%s" is already defined.\n' % lbl)
            exit(ERR_OPERAND)
        cls.__labels[lbl] = order

    @staticmethod
    def check_label_name(name: str):
        if name is None or not re.search('^[_\\-$&%*!?a-zA-Z][_\\-$&%*!?a-zA-Z\d]*$', name):
            sys.stderr.write('Invalid name for label: %s.\n' % name)
            exit(ERR_SEMANTICS)

    @staticmethod
    def check_instruction(instruction: ET.Element) -> None:
        """Checks, that the instruction has all the attributes and appropriate values.

        :param instruction: An instruction todo
        :return:
        """
        i = 0
        for arg in instruction.findall('./'):
            # todo error codes
            ins.Instruction.check_arg_valid(arg)
            if arg.tag != 'arg1':
                sys.stderr.write('Instruction label must have only argument arg1.\n')
                exit(ERR_XML_STRUC)
            if arg.get('type') != 'label':
                sys.stderr.write('Label can have argument only of a type label, not: %s\n' % arg.get('type'))
                exit(ERR_OPERAND)
            InstructionLabel.check_label_name(arg.text)
            i = i + 1

        if i != 1:
            sys.stderr.write('Instruction label must have one argument.\n')
            exit(ERR_XML_STRUC)
