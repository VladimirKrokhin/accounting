import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from accounts.dtos import UserDTO, UserType
from accounts.core.entities import UserId
from accounts.core.exceptions import UserDoesNotExists
from accounts.adapters.repository import SQLAlchemyUserRepository
from accounts.adapters.sqlalchemy.models import Base


@pytest.fixture(scope="function")
def engine():
    # Используем SQLite в памяти для тестов
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def session(engine):
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="function")
def user_repository(session):
    return SQLAlchemyUserRepository(session)


def test_repository_can_save_and_retrieve_user(user_repository, session):
    # Создаем DTO пользователя
    user_dto = UserDTO(
        email="test@example.com",
        full_name="Иван Иванов",
        user_type=UserType.USER,
        password_hash="hash_123",
    )

    # Сохраняем
    user_id = user_repository.save_user(user_dto)
    session.commit()

    # Получаем обратно
    retrieved_user = user_repository.get_user(user_id)

    assert retrieved_user.user_id == user_id
    assert retrieved_user.email == "test@example.com"
    assert retrieved_user.full_name == "Иван Иванов"
    assert retrieved_user.user_type == UserType.USER


def test_repository_can_save_different_user_types(user_repository, session):
    # Тестируем полиморфизм (Administrator)
    admin_dto = UserDTO(
        email="admin@system.com",
        full_name="Главный Админ",
        user_type=UserType.ADMIN,
        password_hash="admin_hash",
    )

    admin_id = user_repository.save_user(admin_dto)
    session.commit()

    retrieved_admin = user_repository.get_user(admin_id)
    assert retrieved_admin.user_type == UserType.ADMIN
    assert retrieved_admin.full_name == "Главный Админ"


def test_is_user_exists_by_methods(user_repository, session):
    email = "unique@test.com"
    user_dto = UserDTO(
        email=email,
        full_name="Unique User",
        user_type=UserType.USER,
        password_hash="hash",
    )
    user_id = user_repository.save_user(user_dto)
    session.commit()

    # Проверка по ID
    assert user_repository.is_user_exists(user_id) is True
    assert user_repository.is_user_exists(UserId(999)) is False

    # Проверка по Email
    assert user_repository.is_user_exists_by_email(email) is True
    assert user_repository.is_user_exists_by_email("wrong@test.com") is False


def test_get_users_by_email(user_repository, session):
    email = "search@test.com"
    user_repository.save_user(UserDTO(email, "User 1", UserType.USER, "h1"))
    user_repository.save_user(UserDTO("other@test.com", "User 2", UserType.USER, "h2"))
    session.commit()

    users = user_repository.get_users_by_email(email)
    assert len(users) == 1
    assert users[0].email == email


def test_update_existing_user(user_repository, session):
    user_dto = UserDTO("old@test.com", "Old Name", UserType.USER, "h1")
    user_id = user_repository.save_user(user_dto)
    session.commit()

    # Обновляем данные в DTO
    user_dto.full_name = "New Name"
    user_dto.email = "new@test.com"

    user_repository.save_user(user_dto)
    session.commit()

    # Проверяем обновление
    session.expire_all()
    updated_user = user_repository.get_user(user_id)
    assert updated_user.full_name == "New Name"
    assert updated_user.email == "new@test.com"


def test_delete_user(user_repository, session):
    user_dto = UserDTO("delete@test.com", "To Delete", UserType.USER, "h1")
    user_id = user_repository.save_user(user_dto)
    session.commit()

    assert user_repository.is_user_exists(user_id) is True

    user_repository.delete_user(user_id)
    session.commit()

    assert user_repository.is_user_exists(user_id) is False


def test_get_user_raises_error_if_not_found(user_repository):
    with pytest.raises(UserDoesNotExists, match="not found"):
        user_repository.get_user(UserId(8888))


def test_delete_user_raises_error_if_not_found(user_repository):
    with pytest.raises(UserDoesNotExists, match="not found"):
        user_repository.delete_user(UserId(7777))


def test_get_all_users(user_repository, session):
    user_repository.save_user(UserDTO("u1@t.com", "U1", UserType.USER, "p1"))
    user_repository.save_user(UserDTO("u2@t.com", "U2", UserType.ADMIN, "p2"))
    session.commit()

    all_users = user_repository.get_users()
    assert len(all_users) == 2
