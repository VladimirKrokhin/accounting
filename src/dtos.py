from dataclasses import dataclass, field
from enum import StrEnum

from domain.types import UserId


class UserType(StrEnum):
    ADMIN = "admin"
    USER = "user"


@dataclass
class UserDTO:
    email: str
    full_name: str
    user_type: UserType
    password_hash: str = field(repr=False)

    user_id: UserId | None = None


@dataclass(frozen=True)
class CreateOrUpdateUserDTO:
    email: str
    full_name: str
    password: str = field(repr=False)
