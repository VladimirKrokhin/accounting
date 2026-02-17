import pytest

from accounts.core.use_cases.users import CreateUser, DeleteUser, UpdateUser
from accounts.dtos import CreateUserDTO, DeleteUserDTO, UpdateUserDTO, UserDTO, UserType
from accounts.core.entities import UserId
from accounts.core.exceptions import UserIsAlreadyExistsError, UserDoesNotExists

from fakes import FakeUnitOfWork


# Фикстура репозитория для единицы работы
@pytest.fixture
def uow():
    return FakeUnitOfWork()


# --- Тесты создания (create_user) ---


@pytest.mark.asyncio
async def test_create_user_success(uow):
    dto = CreateUserDTO(
        email="test@example.com", password="secret_password", full_name="Test User"
    )
    use_case = CreateUser(uow=uow)
    user_id = await use_case.execute(dto)

    assert user_id is not None
    assert await uow.users.does_user_exist(user_id)

    created_user = await uow.users.get_user(user_id)
    assert created_user.email == "test@example.com"
    assert created_user.full_name == "Test User"
    # Проверяем, что пароль не хранится в открытом виде
    assert created_user.password_hash != "secret_password"


@pytest.mark.asyncio
async def test_create_user_fails_if_email_exists(uow):
    email = "duplicate@test.com"
    # Предварительно сохраняем пользователя
    async with uow:
        await uow.users.save_user(
            UserDTO(
                email=email,
                full_name="User",
                user_type=UserType.USER,
                password_hash="...",
            )
        )
        await uow.commit()

    dto = CreateUserDTO(email=email, password="password", full_name="User")

    use_case = CreateUser(uow=uow)

    with pytest.raises(UserIsAlreadyExistsError, match="уже существует"):
        user_id = await use_case.execute(dto)


# --- Тесты обновления (update_user) ---


@pytest.mark.asyncio
async def test_update_user_success(uow):
    # 1. Создаем исходного пользователя
    old_id = await uow.users.save_user(
        UserDTO(
            email="old@test.com",
            full_name="Old Name",
            user_type=UserType.USER,
            password_hash="old_hash",
        )
    )

    # 2. Обновляем
    dto = UpdateUserDTO(
        user_id=old_id,
        email="new@test.com",
        full_name="New Name",
        password="new_password",
    )

    use_case = UpdateUser(uow)
    await use_case.execute(dto)

    updated = await uow.users.get_user(old_id)
    assert updated.email == "new@test.com"
    assert updated.full_name == "New Name"


@pytest.mark.asyncio
async def test_update_user_fails_if_not_found(uow):
    dto = UpdateUserDTO(
        user_id=UserId(999), email="any@test.com", full_name="Any", password="..."
    )

    use_case = UpdateUser(uow)
    with pytest.raises(UserDoesNotExists):
        await use_case.execute(dto)


@pytest.mark.asyncio
async def test_update_user_fails_if_new_email_taken_by_another(uow):
    # Создаем двоих пользователей
    user1_id = await uow.users.save_user(UserDTO("u1@t.com", "U1", UserType.USER, "h1"))
    user2_id = await uow.users.save_user(UserDTO("u2@t.com", "U2", UserType.USER, "h2"))

    # Пытаемся первому пользователю поставить email второго
    dto = UpdateUserDTO(
        user_id=user1_id, email="u2@t.com", full_name="U1 New", password="p"
    )
    use_case = UpdateUser(uow)

    with pytest.raises(
        UserIsAlreadyExistsError, match="Существует другой пользователь"
    ):
        await use_case.execute(dto)


# --- Тесты удаления (delete_user) ---


@pytest.mark.asyncio
async def test_delete_user_success(uow):
    user_id = await uow.users.save_user(UserDTO("del@t.com", "Del", UserType.USER, "h"))

    dto = DeleteUserDTO(user_id=user_id)
    use_case = DeleteUser(uow)

    await use_case.execute(dto)

    assert await uow.users.does_user_exist(user_id) is False


@pytest.mark.asyncio
async def test_delete_user_fails_if_not_found(uow):
    dto = DeleteUserDTO(user_id=UserId(404))
    use_case = DeleteUser(uow)

    with pytest.raises(UserDoesNotExists):
        await use_case.execute(dto)
