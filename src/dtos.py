from dataclasses import dataclass
from enum import StrEnum

from domain.models import UserId


class UserType(StrEnum):
    ADMIN = "admin"
    USER = "user"


@dataclass(frozen=True)
class AuthDTO:
    email: str
    password: str


@dataclass(frozen=True)
class UserDTO:
    user_id: UserId
    email: str
    full_name: str
    user_type: UserType


@dataclass(frozen=True)
class AuthSuccessDTO:
    token: str
    data: UserDTO
