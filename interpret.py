import argparse
import os.path
import sys

ERR_MISSING_ARG = 10
ERR_READ_INPUT = 11


class Interpret:

    @staticmethod
    def is_file_ok(file_name: str):
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
    def proc_args():
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

        if args.input is not None and not Interpret.is_file_ok(args.input):
            sys.stderr.write('Source file either does not exist or is not readable.\n')
            exit(ERR_READ_INPUT)
        if args.source is not None and not Interpret.is_file_ok(args.source):
            sys.stderr.write('Source file either does not exist or is not readable.\n')
            exit(ERR_READ_INPUT)

        return args.source, args.input


if __name__ == '__main__':
    Interpret.proc_args()
