import Frame
import sys
from errorCodes import ERR_FRAME


class Frame:
    __frames: Frame = []
    __tmp_frame: Frame = None

    def __init__(self):
        self.__variables = {}

    @classmethod
    def create_frame(cls):
        Frame.__tmp_frame.get_variables().clear()
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
        if Frame.top_frame().is_global():
            sys.stderr.write('There are no local frames to pop.\n')
            exit(ERR_FRAME)
        Frame.__tmp_frame.get_variables().clear()
        Frame.__tmp_frame = Frame.__frames.pop()

    @classmethod
    def top_frame(cls):
        return cls.__frames[-1]

    def is_global(self):
        return Frame.__frames.index(self) == 0

    def get_variables(self):
        return self.__variables
