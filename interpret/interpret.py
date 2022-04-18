import argparse
import os.path
import sys
from typing import Tuple
import xml.etree.ElementTree as ET
import Instruction as Ins
import InstructionLabel as InsLa
import Frame as Fr
import Variable as Var
from errorCodes import *


class Interpret:
    """Class contains only static methods."""

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
        root[:] = sorted(root, key=lambda child: child.get('order'))
        return tree

    @staticmethod
    def get_labels(tree: ET.ElementTree) -> None:
        """Saves all labels inside InstructionLabel dict, checks their syntax and removes them from the xml representation.

        :param tree: XML representation of source code file
        :return:
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
                InsLa.InstructionLabel.add_label(int(ins.get('order')), ins.find('arg1').text)
                tree.getroot().remove(ins)


if __name__ == '__main__':
    source, inpt = Interpret.proc_args()
    tree = Interpret.get_sorted_xml(source)
    Interpret.get_labels(tree)

    Fr.Frame.create_global()

    # Fr.Frame.create_frame()
    # var = Var.Variable('TF@tmp')
    # var.defvar()
    # var = Var.Variable('TF@tmp', '5')
    # var.move()
    # print(Fr.Frame.get_tmp().get_variables())
    # Fr.Frame.push_frame()
    # var = Var.Variable('LF@tmp', 'as')
    # var.move()
    # print(Fr.Frame.top_local_frame().get_variables())
    # Fr.Frame.pop_frame()
    # var = Var.Variable('TF@tmp', 'true')
    # var.move()
    # print(Fr.Frame.get_tmp().get_variables())
    # Fr.Frame.create_frame()
    # print(Fr.Frame.get_tmp().get_variables())

    min_order = int(tree.find('./instruction').get('order'))
    max_order = int(tree.findall('./instruction')[-1].get('order'))

    for order in range(min_order, max_order+1):
        instruction = tree.find('./instruction[@order="%d"]' % order)
        if instruction is None:
            continue
        if instruction.tag == 'program':
            continue
        if instruction.attrib.get('opcode') == 'CREATEFRAME':
            if len(instruction.findall('./')) != 0:
                sys.stderr.write('Instruction CREATEFRAME cannot have any arguments.\n')
                exit(ERR_XML_STRUC)
            Fr.Frame.create_frame()
            continue
        if instruction.attrib.get('opcode') == 'PUSHFRAME':
            if len(instruction.findall('./')) != 0:
                sys.stderr.write('Instruction PUSHFRAME cannot have any arguments.\n')
                exit(ERR_XML_STRUC)
            Fr.Frame.push_frame()
            continue
        if instruction.attrib.get('opcode') == 'POPFRAME':
            if len(instruction.findall('./')) != 0:
                sys.stderr.write('Instruction POPFRAME cannot have any arguments.\n')
                exit(ERR_XML_STRUC)
            Fr.Frame.pop_frame()
            continue
        if instruction.attrib.get('opcode') == 'DEFVAR':
            if len(instruction.findall('./')) != 1:
                sys.stderr.write('Instruction DEFVAR must have one arguments.\n')
                exit(ERR_XML_STRUC)
            arg1 = instruction.find('./arg1')
            if arg1 is None:
                sys.stderr.write('DEFVAR must have argument arg1\n')
                exit(ERR_XML_STRUC)
            Ins.Instruction.check_arg_valid(arg1)
            if arg1.get('type') != 'var':
                sys.stderr.write('DEFVAR must have argument of type var, not: %s\n' % arg1.get('type'))
                exit(ERR_XML_STRUC)
            var = Var.Variable(arg1.text)
            var.defvar()
            continue
        if instruction.attrib.get('opcode') == 'MOVE':
            if len(instruction.findall('./')) != 2:
                sys.stderr.write('Instruction MOVE must have two arguments.\n')
                exit(ERR_XML_STRUC)
            arg1 = instruction.find('./arg1')
            arg2 = instruction.find('./arg2')
            if arg1 is None or arg2 is None:
                sys.stderr.write('MOVE must have argument arg1 and arg2\n')
                exit(ERR_XML_STRUC)
            Ins.Instruction.check_arg_valid(arg1)
            Ins.Instruction.check_arg_valid(arg2)
            if arg1.get('type') != 'var':
                sys.stderr.write('MOVE must have arg1 of type var, not: %s\n' % arg1.get('type'))
                exit(ERR_XML_STRUC)
            arg2_type = arg2.get('type')
            if arg2_type not in ['int', 'bool', 'string', 'nil']:
                sys.stderr.write('MOVE has invalid arg2 type: %s\n' % arg2_type)
                exit(ERR_XML_STRUC)
            var = Var.Variable(arg1.text, arg2.text)
            var.move()
            continue
        print(instruction)

    test = Fr.Frame.get_global().find_variable('test')
    print(test.get_name(), test.value, test.typ)

    # for i in range(1, 10):
    #     instruction = parser.getroot().find("./instruction[@order='%s']" % i)
    #     if instruction is None:
    #         continue
    #     for child in instruction.iter():
    #         print(child)

    # todo prochazet <instruction> podle order - iterovat v order, dokud nejsem na konci souboru
