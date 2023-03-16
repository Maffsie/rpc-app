import builtins
from enum import Enum
from typing import Any, Generic, TypeVar

from RPC.util.errors import InvalidInputError

T = TypeVar("T")

TRUEABLE_WORDS = [
    "accept",
    "accepted",
    "affirm",
    "affirmative",
    "agree",
    "allow",
    "alright",
    "approve",
    "approved",
    "comply",
    "consent",
    "cool",
    "enable",
    "enabled",
    "e",
    "grant",
    "okay",
    "ok",
    "on",
    "permit",
    "taxed",
    "true",
    "tru",
    "t",
    "valid",
    "yeah",
    "yea",
    "yes",
    "y",
]


def coerce_type(have: Any, want: T, need: bool = False) -> T:
    """Function to coerce a given input to be of type T, optionally raising an exception if impossible.

    If the given input is already of type T, it is returned as-is.
    Otherwise, this function follows the given chain of logic:

    * If T is an Enum or a member thereof, attempt to coerce input into a member of T.
    * If input is a value known to the enum, the primary member with that value is returned
    * If input is the name of a member of the enum, that member is returned
    * If input, case insensitive, is the name or value of any member in the enum, that member is returned
    * If none of the above, return None (or exception)
    * If T is a bool, attempt to coerce input to a boolean value
    * If input, interpreted as a string, case-insensitively matches "1" or any words which can reasonably mean "true" in this context, return True
    * if none of the above, return False

    Args:
        have (Any): Arbitrary data to be coerced.
        want T: The desired type for `have`, or if `need` is False, a default value.
        need (bool, optional): Whether to raise an exception on coercion failure. Defaults to False.

    Returns:
        T | None: Returns either the input (have) coerced to type T (want)
                    or, if T is not directly a type, returns T.
    """

    def _coerce(have: Any, want: T, need: bool) -> T | None:
        # required because otherwise str(None) returns "None"
        if isinstance(want, type) and have is None:
            return have
        if not isinstance(want, type):
            want = type(want)
        if type(have) is want or isinstance(want, type(None)):
            return have
        if isinstance(want, type(Enum)):
            # Enum(Item) returns the enum member corresponding to the value
            #  ie. for Example(Enum): A=1, Example(1) will return Example.A
            #  and Example('A') will throw a ValueError
            try:
                return want(have)
            except ValueError:
                # Enum[Item] returns the enum member corresponding to the name
                #  ie. for Example(Enum): A=1, Example['A'] will return Example.A
                #  and Example[1] will throw a KeyError
                try:
                    return want[have]
                except KeyError:
                    # Hail Mary - case-insensitively search for an enum member which has either a
                    #  matching name or value, both with and without spaces
                    for name in want._member_map_.keys():
                        if name.upper() == str(have).upper():
                            return want[name]
                    for name in want._member_map_.keys():
                        if name.upper() == str(have).upper().replace(" ", "_"):
                            return want[name]
                    for member in want:
                        if member.name.upper() == str(have).upper():
                            return want[member.name]
                        if member.name.upper() == str(have).upper().replace(" ", "_"):
                            return want[member.name]
                        if str(member.value).upper() == str(have).upper():
                            return want(member.value)
                        if str(member.value).upper() == str(have).upper().replace(
                            " ", "_"
                        ):
                            return want(member.value)
                    # If we reach this point, there is no possibility of automatically turning `O`
                    #  into a member of the given Enum.
                    if need:
                        raise InvalidInputError(
                            "Unable to coerce input value to a member of desired enum"
                        )
                    return None
        match want:
            case builtins.bool:
                # Have to cast O to string, because O could be anything.
                #  Goodness, what if it were an int?
                return str(have).lower() in ("1", *TRUEABLE_WORDS)
            case _:
                returnval = None
                try:
                    returnval = want(have)
                except Exception:
                    if not need:
                        returnval = have
                finally:
                    return returnval

    output = _coerce(have, want, need)
    if need and output is None:
        if not isinstance(want, type):
            want = type(want)
        raise InvalidInputError(
            f"Coercion error: Coerce to type {want} required, but impossible."
        )
    return output
