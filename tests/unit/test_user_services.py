import pytest
from domain.messages import CreateUser, DeleteUser, UpdateUser
from domain.models import UserId
from domain.exceptions import UserIsAlreadyExistsError, UserDoesNotExists
from dtos import UserDTO, UserType
from adapters.repository import FakeUserRepository
from service_layer.handlers.user import (
    create_user,
    update_user,
    delete_user,
)
from service_layer.unit_of_work import FakeUnitOfWork


# Фикстура репозитория для единицы работы
@pytest.fixture
def uow():
    return FakeUnitOfWork()


# --- Тесты создания (create_user) ---


def test_create_user_success(uow):
    message = CreateUser(
        email="test@example.com", password="secret_password", full_name="Test User"
    )

    user_id = create_user(message, uow)

    assert user_id is not None
    assert uow.users.is_user_exists(user_id)

    created_user = uow.users.get_user(user_id)
    assert created_user.email == "test@example.com"
    assert created_user.full_name == "Test User"
    # Проверяем, что пароль не хранится в открытом виде
    assert created_user.password_hash != "secret_password"


def test_create_user_fails_if_email_exists(uow):
    email = "duplicate@test.com"
    # Предварительно сохраняем пользователя
    uow.users.save_user(
        UserDTO(
            email=email, full_name="User", user_type=UserType.USER, password_hash="..."
        )
    )

    message = CreateUser(email=email, password="password", full_name="User")

    with pytest.raises(UserIsAlreadyExistsError, match="уже существует"):
        create_user(message, uow)


# --- Тесты обновления (update_user) ---


def test_update_user_success(uow):
    # 1. Создаем исходного пользователя
    old_id = uow.users.save_user(
        UserDTO(
            email="old@test.com",
            full_name="Old Name",
            user_type=UserType.USER,
            password_hash="old_hash",
        )
    )

    # 2. Обновляем
    message = UpdateUser(
        user_id=old_id,
        email="new@test.com",
        full_name="New Name",
        password="new_password",
    )

    update_user(message, uow)

    updated = uow.users.get_user(old_id)
    assert updated.email == "new@test.com"
    assert updated.full_name == "New Name"


def test_update_user_fails_if_not_found(uow):
    message = UpdateUser(
        user_id=UserId(999), email="any@test.com", full_name="Any", password="..."
    )

    with pytest.raises(UserDoesNotExists):
        update_user(message, uow)


def test_update_user_fails_if_new_email_taken_by_another(uow):
    # Создаем двоих пользователей
    user1_id = uow.users.save_user(UserDTO("u1@t.com", "U1", UserType.USER, "h1"))
    user2_id = uow.users.save_user(UserDTO("u2@t.com", "U2", UserType.USER, "h2"))

    # Пытаемся первому пользователю поставить email второго
    message = UpdateUser(
        user_id=user1_id, email="u2@t.com", full_name="U1 New", password="p"
    )

    with pytest.raises(
        UserIsAlreadyExistsError, match="Существует другой пользователь"
    ):
        update_user(message, uow)


# --- Тесты удаления (delete_user) ---


def test_delete_user_success(uow):
    user_id = uow.users.save_user(UserDTO("del@t.com", "Del", UserType.USER, "h"))

    message = DeleteUser(user_id=user_id)
    delete_user(message, uow)

    assert uow.users.is_user_exists(user_id) is False


def test_delete_user_fails_if_not_found(uow):
    message = DeleteUser(user_id=UserId(404))

    with pytest.raises(UserDoesNotExists):
        delete_user(message, uow)
