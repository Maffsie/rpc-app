from inspect import getmro


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


class RPCAuthException(RPCInputException):
    extype = "Authentication exception"
    hstatus = 403


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


class InternalOperationalError(RPCOperationalException):
    extype = "Error while fulfilling request"
    hstatus = 502


class AuthRequiredError(RPCAuthException):
    extype = "Endpoint requires authentication"
    hstatus = 401


class AuthExpiredError(RPCAuthException):
    extype = "Authentication token expired"
    hstatus = 401


class AuthInvalidError(RPCAuthException):
    extype = "Authentication credentials are invalid"
    hstatus = 403


class AuthInsufficientError(RPCAuthException):
    extype = "Endpoint requires a permission you do not have"
    hstatus = 403
