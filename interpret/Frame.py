import Frame
import Variable as Var
import sys
from typing import Dict
from errorCodes import *

class Frame:
    __frames: Frame = []
    __tmp_frame: Frame = None

    def __init__(self):
        self.__variables: Dict[str] = {}

    @classmethod
    def create_frame(cls):
        Frame.__tmp_frame = Frame()

    @classmethod
    def push_frame(cls):
        if Frame.__tmp_frame is None:
            sys.stderr.write('Temporary frame must be first defined before pushing to stack.\n')
            exit(ERR_FRAME)
        Frame.__frames.append(Frame.__tmp_frame)
        Frame.__tmp_frame = None

    @classmethod
    def pop_frame(cls):
        if Frame.top_local_frame() is None:
            sys.stderr.write('There are no local frames on the stack to pop.\n')
            exit(ERR_FRAME)
        Frame.__tmp_frame = Frame.__frames.pop()

    @classmethod
    def top_local_frame(cls) -> Frame.Frame:
        top = cls.__frames[-1]
        return None if top is cls.get_global() else top

    @classmethod
    def check_local_frame(cls):
        if cls.top_local_frame() is None:
            sys.stderr.write('There is no local frame on the stack\n')
            exit(ERR_FRAME)

    @classmethod
    def create_global(cls):
        if len(Frame.__frames) != 0:
            sys.stderr.write('Global frame has already been created.\n')
            exit(ERR_INTERPRET)
        cls.__frames.append(Frame())

    def is_global(self) -> bool:
        return Frame.__frames.index(self) == 0

    @classmethod
    def frame_for_name(cls, frame_name: str):
        if frame_name == 'GF':
            return cls.get_global()
        elif frame_name == 'TF':
            cls.check_tmp_frame()
            return cls.get_tmp()
        else:
            cls.check_local_frame()
            return cls.top_local_frame()

    @classmethod
    def get_global(cls) -> Frame.Frame:
        return cls.__frames[0]

    @classmethod
    def get_tmp(cls) -> Frame.Frame:
        return cls.__tmp_frame

    @classmethod
    def check_tmp_frame(cls):
        if cls.get_tmp() is None:
            sys.stderr.write('The temporary frame must be first created')
            exit(ERR_FRAME)

    def get_variables(self):
        return self.__variables

    def find_variable(self, var_name: str) -> Var.Variable:
        if var_name not in self.get_variables():
            return None
        else:
            return self.__variables[var_name]

    def add_variable(self, var: Var.Variable):
        if var.get_name() in self.__variables:
            sys.stderr.write('Variable %s has already been defined.\n' % var.get_name())
            exit(ERR_SEMANTICS)

        self.__variables[var.get_name()] = var
