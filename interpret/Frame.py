import sys
from typing import Dict
import Frame
import Variable as Var
from errorCodes import *


class Frame:
    """Class representing a frame in the memory model.

    Contains a stack of local frames, the temporary frame, global frame and operations over them.

    """
    __frames: Frame = []
    """Stack of frames"""
    __tmp_frame: Frame = None
    """Temporary frame"""

    def __init__(self):
        self.__variables: Dict[str] = {}

    @classmethod
    def create_frame(cls):
        """Creates a new temporary frame, losing the current one.

        :return:
        """
        Frame.__tmp_frame = Frame()

    @classmethod
    def push_frame(cls):
        """Pushes a temporary frame to the stack of frames.

        This action makes the temporary frame undefined.
        If temporary frame is not defined, script gets terminated.

        :return:
        """
        if Frame.__tmp_frame is None:
            sys.stderr.write('Temporary frame must be first defined before pushing to stack.\n')
            exit(ERR_FRAME)
        Frame.__frames.append(Frame.__tmp_frame)
        Frame.__tmp_frame = None

    @classmethod
    def pop_frame(cls):
        """Removes frame from top of the frame stack and stores it inside temporary frame.

        If there are no local frames on the stack, interpret gets terminated.

        :return:
        """
        if Frame.top_local_frame() is None:
            sys.stderr.write('There are no local frames on the stack to pop.\n')
            exit(ERR_FRAME)
        Frame.__tmp_frame = Frame.__frames.pop()

    @classmethod
    def top_local_frame(cls) -> Frame.Frame:
        """Retrieves a frame from the top of the frame stack.

        :return: Local frame from the top of the stack, or None if there are no local frames.
        """
        top = cls.__frames[-1]
        return None if top is cls.get_global() else top

    @classmethod
    def check_local_frame(cls):
        """Terminates interpret if there are no local frames on the frame stack.

        :return:
        """
        if cls.top_local_frame() is None:
            sys.stderr.write('There is no local frame on the stack\n')
            exit(ERR_FRAME)

    @classmethod
    def create_global(cls):
        """Creates a global frame on the frame stack.

        If there already is a global frame, nothing happens.

        :return:
        """
        if len(Frame.__frames) == 0:
            cls.__frames.append(Frame())

    def is_global(self) -> bool:
        """

        :return: True, if a frame is the global frame.
        """
        return Frame.__frames.index(self) == 0

    @classmethod
    def frame_for_name(cls, frame_name: str):
        """

        :param frame_name: Name (type) of a frame i.e. TF, GF or LF
        :return: Frame corresponding to a given name.
        """
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
        """

        :return: Global frame
        """
        return cls.__frames[0]

    @classmethod
    def get_tmp(cls) -> Frame.Frame:
        """

        :return: Temporary frame
        """
        return cls.__tmp_frame

    @classmethod
    def check_tmp_frame(cls):
        """Terminates interpret if a temporary frame is not defined.

        :return:
        """
        if cls.get_tmp() is None:
            sys.stderr.write('The temporary frame must be first created')
            exit(ERR_FRAME)

    def get_variables(self):
        """

        :return: A list of all variables inside a frame
        """
        return self.__variables

    def find_variable(self, var_name: str) -> Var.Variable:
        """Retrieves a variable from the list.

        :param var_name: Name of a variable
        :return: Object of a variable from a given frame
        """
        if var_name not in self.get_variables():
            return None
        else:
            return self.__variables[var_name]

    def add_variable(self, var: Var.Variable):
        """Adds a variable to a frame.

        If a variable with the same name has been defined, iterpret gets terminated.

        :param var: Instance of Variable
        :return:
        """
        if var.get_name() in self.__variables:
            sys.stderr.write('Variable %s has already been defined.\n' % var.get_name())
            exit(ERR_SEMANTICS)

        self.__variables[var.get_name()] = var
