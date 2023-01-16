from inspect import getmro
from typing import List


class RPCException(Exception):
    extype = "General exception"
    hstatus = 503

    def __init__(self, message, *args, **kwargs):
        self.message = message
        super().__init__(*args, **kwargs)

    def __repr__(self):
        clslist = [c.__name__ for c in getmro(self.__class__)]
        clslist.reverse()
        return f"({'->'.join(clslist)}) {self.extype}: {self.message}"

    def __str__(self):
        return self.__repr__()


class RPCInputException(RPCException):
    extype = "Input exception"


class RPCOperationalException(RPCException):
    extype = "Internal/operational exception"


class RPCInitialisationException(RPCException):
    extype = "Startup/initialisation exception"


class MissingFileError(RPCOperationalException):
    extype = "Missing expected file"


class InvalidInputError(RPCInputException):
    extype = "Input validation error"
    hstatus = 400


class ImageGenerationError(RPCOperationalException):
    extype = "Operational error while generating image"
