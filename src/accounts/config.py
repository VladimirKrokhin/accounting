from dataclasses import dataclass, field
from datetime import timedelta
import os
import re

__all__ = [
    "Config",
    "PaymentSystemConfig",
    "AuthConfig",
    "PostgresConfig",
    "load_config",
]


@dataclass(frozen=True)
class PaymentSystemConfig:
    secret_key: str


@dataclass(frozen=True)
class AuthConfig:
    secret_key: str = field(repr=False)
    expiration_time: timedelta
    encryption_algorithm: str


@dataclass(frozen=True)
class PostgresConfig:
    user: str
    password: str
    host: str
    port: int
    db_name: str


@dataclass(frozen=True)
class Config:
    # Конфигурация Postgres
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_PASSWORD: str
    POSTGRES_USER: str
    POSTGRES_DB_NAME: str

    # Конфигурация обработки транзакций от платежной системы
    # Секретный ключ
    PAYMENT_SYSTEM_SECRET_KEY: str

    # Конфигурация авторизации
    # "Срок годности" токена
    AUTH_EXPIRATION_TIME: timedelta
    # Алгоритм шифрования токена
    AUTH_ENCRYPTION_ALGORITHM: str
    # секретный ключ к шифрованию токена
    AUTH_SECRET_KEY: str

    def get_postgres_config(self) -> PostgresConfig:
        return PostgresConfig(
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            password=self.POSTGRES_PASSWORD,
            user=self.POSTGRES_USER,
            db_name=self.POSTGRES_DB_NAME,
        )

    def get_auth_config(self) -> AuthConfig:
        return AuthConfig(
            expiration_time=self.AUTH_EXPIRATION_TIME,
            encryption_algorithm=self.AUTH_ENCRYPTION_ALGORITHM,
            secret_key=self.AUTH_SECRET_KEY,
        )

    def get_payment_system_config(self) -> PaymentSystemConfig:
        return PaymentSystemConfig(secret_key=self.PAYMENT_SYSTEM_SECRET_KEY)


def parse_time(time_str: str) -> timedelta:
    regex = re.compile(
        r"((?P<hours>\d+?)hr)?((?P<minutes>\d+?)m)?((?P<seconds>\d+?)s)?"
    )
    parts = regex.match(time_str)
    if not parts:
        raise ValueError

    parts = parts.groupdict()
    time_params = {}
    for name, param in parts.items():
        if param:
            time_params[name] = int(param)
    return timedelta(**time_params)


def load_config() -> Config:
    postgres_host = os.environ["POSTGRES_HOST"]
    postgres_port = int(os.environ["POSTGRES_PORT"])
    postgres_password = os.environ["POSTGRES_PASSWORD"]
    postgres_user = os.environ["POSTGRES_USER"]
    postgres_db_name = os.environ["POSTGRES_DB_NAME"]
    payment_system_secret_key = os.environ["PAYMENT_SYSTEM_SECRET_KEY"]
    auth_expiration_time = parse_time(os.environ["AUTH_EXPIRATION_TIME"])
    auth_encryption_algorithm = os.environ["AUTH_ENCRYPTION_ALGORITHM"]
    auth_secret_key = os.environ["AUTH_SECRET_KEY"]

    config = Config(
        POSTGRES_HOST=postgres_host,
        POSTGRES_PORT=postgres_port,
        POSTGRES_PASSWORD=postgres_password,
        POSTGRES_USER=postgres_user,
        POSTGRES_DB_NAME=postgres_db_name,
        PAYMENT_SYSTEM_SECRET_KEY=payment_system_secret_key,
        AUTH_EXPIRATION_TIME=auth_expiration_time,
        AUTH_ENCRYPTION_ALGORITHM=auth_encryption_algorithm,
        AUTH_SECRET_KEY=auth_secret_key,
    )

    return config
