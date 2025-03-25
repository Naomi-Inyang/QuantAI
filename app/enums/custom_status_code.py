from enum import Enum, unique

@unique
class CustomStatusCode(Enum):
    SUCCESS = '00'
    FAILURE = '01'
    BAD_REQUEST = '02'