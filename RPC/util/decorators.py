from functools import wraps

from flask import Response

from RPC.util.errors import InvalidInputError, RPCException


def throws(*etypes):
    """Indicates that the wrapped function may throw certain exceptions.

    etypes: Set of Exception types that should be handled. These should be subclasses of RPCException, but may not be.
    Returns a Response object.
    """

    def wrapper(func):
        @wraps(func)
        def call(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except etypes as e:
                if not isinstance(e, RPCException):
                    return Response(response=f"Unknown exception {e}", status=503)
                return Response(status=e.hstatus, response=str(e))

        return call

    return wrapper


def validator(vfunc):
    def wrapper(func):
        @wraps(func)
        def call(*args, **kwargs):
            if not vfunc(args[0]):
                raise InvalidInputError(args[0])
            return func(*args, **kwargs)

        return call

    return wrapper
