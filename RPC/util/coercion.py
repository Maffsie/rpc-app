import builtins
from enum import Enum
from typing import Any, TypeVar, Union

from .errors import InvalidInputError

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
    "true",
    "tru",
    "t",
    "yeah",
    "yes",
    "y",
]


def coercenu(have: Any, expect: T, must: bool = False):
    """coerces the input value [have] to match the type [expect].

    Args:
        have (Any): Any arbitrary input value
        expect (Any): Any arbitrary type. May be a Type, an Enum of some kind, or None
        must (bool, optional): If True, raises an exception if coercion failed. Defaults to False.
    """
    if not isinstance(expect, type):
        expect = type(expect)
    if type(have) is expect or expect is type(None):
        return have


def coerce_type(input: Any, coerce: T, require: bool = False) -> Union[T, None]:
    """Function to coerce a given input to be of type T, optionally raising an exception if impossible.

    If the given input is already of type T, it is returned as-is.
    Otherwise, this function follows the given chain of logic:
    * If T is an Enum or a member thereof, attempt to coerce input into a member of T.
    ** If input is a value known to the enum, the primary member with that value is returned
    ** If input is the name of a member of the enum, that member is returned
    ** If input, case insensitive, is the name or value of any member in the enum, that member is returned
    ** If none of the above, return None (or exception)
    * If T is a bool, attempt to coerce input to a boolean value
    ** If input, interpreted as a string, case-insensitively matches "1" or any words which can reasonably mean "true" in this context, return True
    ** if none of the above, return False

    Args:
        input (Any): Arbitrary data to be coerced.
        coerce (T): _description_
        require (bool, optional): _description_. Defaults to False.

    Returns:
        Union[T, None]: _description_
    """

    def _coerce(input: Any, coerce: T, require: bool) -> Union[T, None]:
        if not isinstance(coerce, type):
            coerce = type(coerce)
        if type(input) is coerce or coerce is type(None):
            return input
        if isinstance(coerce, type(Enum)):
            # Enum(Item) returns the enum member corresponding to the value
            #  ie. for Example(Enum): A=1, Example(1) will return Example.A
            #  and Example('A') will throw a ValueError
            try:
                return coerce(input)
            except ValueError:

                # Enum[Item] returns the enum member corresponding to the name
                #  ie. for Example(Enum): A=1, Example['A'] will return Example.A
                #  and Example[1] will throw a KeyError
                try:
                    return coerce[input]
                except KeyError:
                    # Hail Mary - case-insensitively search for an enum member which has either a matching
                    #  name or value
                    for name in coerce._member_map_.keys():
                        if name.upper() == str(input).upper():
                            return coerce[name]
                    for member in coerce:
                        if member.name.upper() == str(input).upper():
                            return coerce[member.name]
                        if str(member.value).upper() == str(input).upper():
                            return coerce(member.value)
                    # If we reach this point, there is no possibility of automatically turning `O` into
                    # a member of the given Enum.
                    if require:
                        raise InvalidInputError(
                            "Unable to coerce input value to a member of desired enum"
                        )
                    return None
        match coerce:
            case builtins.bool:
                # Have to cast O to string, because O could be anything. Goodness, what if it were an int?
                return str(input).lower() in ("1", *TRUEABLE_WORDS)
            case _:
                returnval = None
                try:
                    returnval = coerce(input)
                except:
                    if not require:
                        returnval = input
                finally:
                    return returnval

    output = _coerce(input, coerce, require)
    if require and output is None:
        if not isinstance(coerce, type):
            coerce = type(coerce)
        raise InvalidInputError(
            f"Coercion error: Coerce to type {coerce} required, but impossible."
        )
    return output
