import argparse
import os.path
import sys
from typing import Tuple
import xml.etree.ElementTree as ET
import Instruction as ins
import InstructionLabel as insLa
from errorCodes import *


class Interpret:

    @staticmethod
    def is_file_ok(file_name: str) -> bool:
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

        # sortnu podle order
        root = tree.getroot()
        for instruction in root.findall('./'):
            ins.Instruction.is_instruction_valid(instruction)
        root[:] = sorted(root, key=lambda child: child.get('order'))
        return tree

    @staticmethod
    def get_labels(tree: ET.ElementTree) -> None:
        instructions = tree.findall('./instruction')
        oldorder = -1

        for ins in instructions:
            if oldorder == int(ins.get('order')):
                sys.stderr.write('Instructions with duplicate order value were found: %d\n' % oldorder)
                exit(ERR_XML_STRUC)
            oldorder = int(ins.get('order'))

            if ins.get('opcode').upper() == 'LABEL':
                insLa.InstructionLabel.check_instruction(ins)
                insLa.InstructionLabel.add_label(int(ins.get('order')), ins.find('arg1').text)
                tree.getroot().remove(ins)


if __name__ == '__main__':
    source, inpt = Interpret.proc_args()
    tree = Interpret.get_sorted_xml(source)
    Interpret.get_labels(tree)
    for el in tree.iter():
        print(el.tag, el.items())
    print('labels: ', insLa.InstructionLabel.get_labels())

    # parser = ET.parse(source)
    # print(parser.getroot().find("./instruction[@order='2']").attrib)
    # for i in range(1, 10):
    #     instruction = parser.getroot().find("./instruction[@order='%s']" % i)
    #     if instruction is None:
    #         continue
    #     for child in instruction.iter():
    #         print(child)

        # todo prochazet <instruction> podle order - iterovat v order, dokud nejsem na konci souboru
