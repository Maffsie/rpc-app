from enum import Enum, auto


class RPCGrantType(Enum):
    DVLALookup = auto()
    DVSALookup = auto()
    TelegramImageGeneration = auto()
