"""
Interpret of XML representation of a code.

Brno University of Technology
Faculty of Information Technology

Principles of Programming Languages

Author: Šimon Vacek - xvacek10@stud.fit.vutbr.cz

"""
import argparse
import os.path
import sys
from typing import Tuple, List
import xml.etree.ElementTree as ET
import Instruction as Ins
import InstructionLabel as InsLa
import Frame as Fr
import Variable as Var
from errorCodes import *


class Interpret:
    """Class contains methods regarding checking input files and xml parsing."""
    __call_stack: List[int] = []
    """Stack for storing instruction order when jump or call instructions are used"""

    @classmethod
    def push_call_stack(cls, order: int) -> None:
        """Adds value to the top of the stack.

        :param order: Order of jump or call instruction.
        :return: None
        """
        cls.__call_stack.append(order)

    @classmethod
    def is_empty_call_stack(cls) -> bool:
        """Finds if the stack is empty.

        :return: True if there is nothing on top of the stack
        """
        return len(cls.__call_stack) == 0

    @classmethod
    def pop_call_stack(cls) -> int:
        """Removes value from the top of the stack. If the stack is empty script is terminated.

        :return: Order value on top of the stack.
        """
        if cls.is_empty_call_stack():
            sys.stderr.write('Cannot return - call stack is empty.\n')
            exit(ERR_INTERPRET)
        return cls.__call_stack.pop()

    @staticmethod
    def is_file_ok(file_name: str) -> bool:
        """Checks if file exists and is readable.

        :param file_name: Name of the file
        :return: True if exists and is readable, False otherwise
        """
        if file_name is not None:
            if not os.path.exists(file_name):
                return False
            file = open(file_name)
            if not file.readable():
                return False
            file.close()
            return True
        return False

    @staticmethod
    def proc_args() -> Tuple[str, str]:
        """Handles script arguments and retrieves source and input file.

        Source file contains the source code to be interpreted. Input file contains inputs, which the source code uses.

        :return: Filenames of source and input file
        """
        parser = argparse.ArgumentParser(
            description='Script loads XML representation of a program and interprets it and generates its output.')
        parser.add_argument('--source', help='input file with XML representation of a source code', type=str,
                            dest='source')
        parser.add_argument('--input', help='file with inputs for the interpretation of a given source code', type=str,
                            dest='input')
        args = parser.parse_args()

        if args.source is None and args.input is None:
            sys.stderr.write('At least one input file must be specified.\n')
            exit(ERR_MISSING_ARG)

        if args.source is not None and not Interpret.is_file_ok(args.source):
            sys.stderr.write('Source file either does not exist or is not readable.\n')
            exit(ERR_READ_INPUT)
        if args.input is not None and not Interpret.is_file_ok(args.input):
            sys.stderr.write('Source file either does not exist or is not readable.\n')
            exit(ERR_READ_INPUT)

        return args.source, args.input

    @staticmethod
    def get_sorted_xml(source: str) -> ET.ElementTree:
        """Sorts and returns the source xml file by order attribute.

        At the same time, this method checks all the child elements in <program> whether they are all instructions and
        are correctly put.

        :param source: Filename of xml with source code
        :return: Sorted representation of xml source code
        """
        source = sys.stdin if source is None else source

        try:
            tree = ET.parse(source)
        except ET.ParseError:
            sys.stderr.write('Source code xml file is not well-formed.\n')
            exit(ERR_XML_FORMAT)

        root = tree.getroot()
        if root.tag != 'program' or 'language' not in root.attrib.keys() or 'IPPcode22' not in root.attrib.values():
            sys.stderr.write('Source code does not have the root <program language="IPPcode22"> element.\n')
            exit()

        # sort by order
        root = tree.getroot()
        for instruction in root.findall('./'):
            Ins.Instruction.is_instruction_valid(instruction)
        root[:] = sorted(root, key=lambda child: int(child.get('order')))
        return tree

    @staticmethod
    def get_labels(tree: ET.ElementTree) -> None:
        """Saves all labels inside InstructionLabel dict, checks their syntax and removes them from the xml representation.

        :param tree: XML representation of source code file
        :return: None
        """
        instructions = tree.findall('./instruction')
        oldorder = -1

        for ins in instructions:
            if oldorder == int(ins.get('order')):
                sys.stderr.write('Instructions with duplicate order value were found: %d\n' % oldorder)
                exit(ERR_XML_STRUC)
            oldorder = int(ins.get('order'))

            if ins.get('opcode').upper() == 'LABEL':
                InsLa.InstructionLabel.check_instruction(ins)
                InsLa.InstructionLabel.add_label(ins.find('arg1').text, int(ins.get('order')))
                tree.getroot().remove(ins)


if __name__ == '__main__':
    source, inpt = Interpret.proc_args()
    tree = Interpret.get_sorted_xml(source)
    Interpret.get_labels(tree)

    Fr.Frame.create_global()

    min_order = int(tree.find('./instruction').get('order'))
    max_order = int(tree.findall('./instruction')[-1].get('order'))

    order = min_order
    while order <= max_order:
        instruction = tree.find('./instruction[@order="%d"]' % order)
        if instruction is None:
            # instruction of this order is missing
            order = order + 1
            continue
        if instruction.tag == 'program':
            order = order + 1
            continue

        opcode = instruction.attrib.get('opcode')

        # main body of interpret executing instructions
        if opcode == 'CREATEFRAME':
            Ins.Instruction.check_args(instruction.findall('./'), 0, 'CREATEFRAME')
            Fr.Frame.create_frame()

        elif opcode == 'PUSHFRAME':
            Ins.Instruction.check_args(instruction.findall('./'), 0, 'PUSHFRAME')
            Fr.Frame.push_frame()

        elif opcode == 'POPFRAME':
            Ins.Instruction.check_args(instruction.findall('./'), 0, 'POPFRAME')
            Fr.Frame.pop_frame()

        elif opcode == 'DEFVAR':
            ET_args = Ins.Instruction.check_args(instruction.findall('./'), 1, 'DEFVAR')
            if ET_args[0].get('type') != 'var':
                sys.stderr.write('DEFVAR must have argument of type var, not: %s\n' % ET_args[0].get('type'))
                exit(ERR_OPERAND)
            var = Var.Variable(ET_args[0].text)
            var.defvar()

        elif opcode == 'MOVE':
            ET_args = Ins.Instruction.check_args(instruction.findall('./'), 2, 'MOVE')
            if ET_args[0].get('type') != 'var':
                sys.stderr.write('MOVE must have arg1 of type var, not: %s\n' % ET_args[0].get('type'))
                exit(ERR_OPERAND)
            arg2_type = ET_args[1].get('type')
            if arg2_type not in ['int', 'bool', 'string', 'nil']:
                sys.stderr.write('MOVE has invalid arg2 type: %s\n' % arg2_type)
                exit(ERR_OPERAND)
            Ins.Instruction.check_data_types(arg2_type, ET_args[1].text)
            var = Var.Variable(ET_args[0].text, ET_args[1].text)
            var.move()

        elif opcode == 'CALL':
            ET_args = Ins.Instruction.check_args(instruction.findall('./'), 1, 'CALL')
            if ET_args[0].get('type') != 'label':
                sys.stderr.write('CALL must have arg1 of type label, not: %s\n' % ET_args[0].get('type'))
                exit(ERR_OPERAND)
            if ET_args[0].text not in InsLa.InstructionLabel.get_labels():
                sys.stderr.write('Label %s is not defined.\n' % ET_args[0].text)
                exit(ERR_SEMANTICS)
            Interpret.push_call_stack(order)
            order = InsLa.InstructionLabel.order_for_label_name(ET_args[0].text)

        elif opcode == 'RETURN':
            Ins.Instruction.check_args(instruction.findall('./'), 0, 'RETURN')
            if Interpret.is_empty_call_stack():
                sys.stderr.write('Cannot return - call stack is empty.\n')
                exit(ERR_MISSING_VALUE)
            order = Interpret.pop_call_stack()

        elif opcode == 'WRITE':
            ET_args = Ins.Instruction.check_args(instruction.findall('./'), 1, 'WRITE')
            typ = ET_args[0].get('type')
            if typ not in ['var', 'int', 'string', 'bool', 'nil']:
                sys.stderr.write('Invalid type of argument for WRITE: %s\n' % ET_args[0].get('type'))
                exit(ERR_OPERAND)
            if typ == 'var':
                var = Var.Variable(instruction.find('./arg1').text)
                var_frame = var.get_var_ids()
                var_name = var.get_name()
                var = Fr.Frame.frame_for_name(var_frame).find_variable(var_name)

                if var is None:
                    sys.stderr.write('Cannot WRITE variable: %s@%s. It does not exist.\n' % (var_frame, var_name))
                    exit(ERR_VARIABLE)
                if not var.is_init():
                    sys.stderr.write('Cannot WRITE variable: %s@%s. It is not initialized.\n' % (var_frame, var_name))
                    exit(ERR_MISSING_VALUE)
                if var.typ == 'nil':
                    print('')
                else:
                    print(var.value)

            else:
                Ins.Instruction.check_data_types(typ, ET_args[0].text)
                if typ == 'nil':
                    print('')
                elif typ == 'int':
                    print(int(ET_args[0].text))
                elif typ == 'string':
                    print(ET_args[0].text.decode('escape_string'))

        elif opcode in ['ADD', 'SUB', 'MUL', 'IDIV', 'LT', 'GT', 'EQ', 'AND', 'OR']:
            ET_args = Ins.Instruction.check_args(instruction.findall('./'), 3, opcode)
            if opcode in ['ADD', 'SUB', 'MUL', 'IDIV']:
                arith_inst = Ins.Instruction.create_arith_ins(opcode, ET_args)
                arith_inst.exec_arithmetic_ins()

        elif opcode == 'JUMP':
            ET_args = Ins.Instruction.check_args(instruction.findall('./'), 1, opcode)
            InsLa.InstructionLabel.check_label_name(ET_args[0].text)
            if ET_args[0].get('type') != 'label':
                sys.stderr.write('Jump can only have attribute of type label\n')
                exit(ERR_OPERAND)
            lbl = InsLa.InstructionLabel.order_for_label_name(ET_args[0].text)
            if lbl is None:
                sys.stderr.write('Label %s does not exist.\n' % ET_args[0].text)
                exit(ERR_OPERAND)
            else:
                order = InsLa.InstructionLabel.order_for_label_name(ET_args[0].text)
        order = order + 1
