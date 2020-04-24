import enum
import json
from datetime import datetime
from types import GeneratorType


# from api.models import db, Case


def know_level(value, low, moderate, danger, emergency):
    if value in range(low, moderate):
        return 1
    elif value in range(moderate + 1, danger):
        return 2
    elif value in range(danger + 1, emergency):
        return 3
    elif value > emergency:
        return 4
    else:
        return 0


def check_gas_level(lpg_value, co_value, smoke_value):
    lpg_level = know_level(value=lpg_value, low=5500, moderate=6900, danger=10000, emergency=18000)
    co_level = know_level(value=co_value, low=10, moderate=24, danger=50, emergency=400)
    smoke_level = know_level(value=smoke_value, low=10, moderate=24, danger=50, emergency=400)
    general_level = max(lpg_level, co_level, smoke_level)
    return general_level


class LevelType(enum.Enum):
    low = 1
    moderate = 2
    dangerous = 3
    emergency = 4

    def __str__(self):
        return self.name


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.__str__()
        if isinstance(obj, LevelType):
            return obj.__str__()
        if isinstance(obj, GeneratorType):
            return str(obj.__next__())
        return json.JSONEncoder.default(self, obj)
