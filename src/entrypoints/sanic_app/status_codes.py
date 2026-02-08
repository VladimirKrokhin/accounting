from enum import IntEnum


class StatusCodes(IntEnum):
    SUCCESS = 200
    SUCCESS_CREATED = 201
    ERROR_NOT_FOUND = 404
    ERROR_CONFLICT = 409
    ERROR_UNPROCESSABLE_ENTITY = 422
