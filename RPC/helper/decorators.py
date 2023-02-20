from functools import wraps

from flask import Response, current_app, request

from RPC.models.auth import RPCGrantType
from RPC.util.coercion import coerce_type
from RPC.util.errors import (
    AuthRequiredError,
    InternalOperationalError,
    InvalidInputError,
    RPCException,
)


def coerce_args(pair: list[tuple[int | str, type]]):
    """Attempts to enforce type coercion for arguments to the wrapped function.
    Possible enhancement: autodetection of types based on typehints of wrapped function

    :arg pair: a pairing of argument number and type
    :type pair: list[tuple[int | str, type]]
    """

    def wrapper(func):
        @wraps(func)
        def call(*args, **kwargs):
            for arg, c_to in pair:
                if isinstance(arg, int):
                    if arg > len(args):
                        raise InternalOperationalError("arg!")
                    args = list(args)
                    args[arg] = coerce_type(args[arg], c_to)
                    args = tuple(args)
                if isinstance(arg, str):
                    if kwargs.get(arg, None) is None:
                        raise InternalOperationalError("kwarg!")
                    kwargs[arg] = coerce_type(kwargs.get(arg, None), c_to)
            return func(*args, **kwargs)

        return call

    return wrapper


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
            except Exception as e:
                try:
                    current_app.log.error(f"UNHANDLED EXCEPTION, THIS IS A BUG: {e}")
                except RuntimeError:
                    print(
                        f"UNHANDLED EXCEPTION RUNNING OUTSIDE OF FLASK, THIS IS A BUG: {e}"
                    )
                raise e

        return call

    return wrapper


def validator(vfunc):
    """Indicates the wrapped function may not be invoked without passing
        a validation function.

    vfunc: Function or other callable object which performs validation
            against the first argument to the wrapped function. Must
            return a boolean.
            Raises an InvalidInputError exception if validation fails.
    """

    def wrapper(func):
        @wraps(func)
        def call(*args, **kwargs):
            if not vfunc(args[1]):
                raise InvalidInputError(args[1])
            return func(*args, **kwargs)

        return call

    return wrapper


def require_token(grant: RPCGrantType = None):
    """Indicates the wrapped function may not be invoked without passing
    caller token checks.

    grant: RPCGrantType | None: Optional parameter indicating the token is expected to have the given grant type
    """

    def wrapper(func):
        @wraps(func)
        def call(*args, **kwargs):
            hkey = request.headers.get("x-api-key", None)
            if hkey is None:
                raise AuthRequiredError("Endpoint requires x-api-key")
            # Raises AuthExpiredError, AuthInsufficientError & AuthInvalidError
            current_app.acl.validate(hkey, with_grant=grant)
            return func(*args, **kwargs)

        return call

    return wrapper
