from dataclasses import dataclass
from datetime import timedelta
import os
import re


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
    postgres_host = os.environ.get("DB_HOST", "localhost")
    postgres_port = 54321 if postgres_host == "localhost" else 5432
    postgres_password = os.environ.get("DB_PASSWORD", "abc123")
    postgres_user, postgres_db_name = "accounts", "accounts"
    payment_system_secret_key = os.environ.get(
        "PAYMENT_SYSTEM_SECRET_KEY", "gfdmhghif38yrf9ew0jkf32"
    )
    auth_expiration_time = parse_time(os.environ.get("AUTH_EXPIRATION_TIME", "24h0m0s"))
    auth_encryption_algorithm = os.environ.get("AUTH_ENCRYPTION_ALGORITHM", "HS256")
    auth_secret_key = os.environ.get("AUTH_SECRET_KEY", "your-very-secret-key")

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
