import pytest
from tests.mocks.user_repo_mock import UserRepositoryMock


@pytest.mark.asyncio
async def test_create_user_adds_user():
    repo = UserRepositoryMock()

    user = type('User', (), {})()
    user.telegram_id = "12345"
    user.telegram_name = "test_user"

    await repo.create_user(user)

    found_user = await repo.get_user_by_telegram_id("12345")
    assert found_user is not None
    assert found_user.telegram_name == "test_user"


@pytest.fixture
def repo():
    """Фикстура, которая создаёт чистый мок перед каждым тестом."""
    return UserRepositoryMock()


def make_user(telegram_id: str, username: str):
    """Вспомогательная функция для создания тестового пользователя."""
    user = type('User', (), {})()
    user.id = None
    user.telegram_id = telegram_id
    user.telegram_name = username
    return user


@pytest.mark.asyncio
async def test_create_user_adds_user(repo):
    user = make_user("123", "test_user")
    await repo.create_user(user)

    found = await repo.get_user_by_telegram_id("123")
    assert found is not None
    assert found.telegram_name == "test_user"


@pytest.mark.asyncio
async def test_create_user_assigns_id(repo):
    user = make_user("123", "test_user")
    await repo.create_user(user)

    assert user.id is not None


@pytest.mark.asyncio
async def test_get_all_users_returns_all(repo):
    user1 = make_user("111", "user1")
    user2 = make_user("222", "user2")
    await repo.create_user(user1)
    await repo.create_user(user2)

    all_users = await repo.get_all_users()
    assert len(all_users) == 2


@pytest.mark.asyncio
async def test_get_user_by_id_finds_user(repo):
    user = make_user("123", "test_user")
    await repo.create_user(user)

    found = await repo.get_user_by_id(user.id)
    assert found is not None
    assert found.telegram_id == "123"


@pytest.mark.asyncio
async def test_get_user_by_id_returns_none_for_missing(repo):
    found = await repo.get_user_by_id(999)
    assert found is None


@pytest.mark.asyncio
async def test_get_user_by_telegram_id_finds_user(repo):
    user = make_user("123", "test_user")
    await repo.create_user(user)

    found = await repo.get_user_by_telegram_id("123")
    assert found is not None


@pytest.mark.asyncio
async def test_get_user_by_telegram_id_returns_none_for_missing(repo):
    found = await repo.get_user_by_telegram_id("nonexistent")
    assert found is None


@pytest.mark.asyncio
async def test_add_stock_to_user_adds_position(repo):
    user = make_user("123", "test_user")
    await repo.create_user(user)

    await repo.add_stock_to_user_by_telegram_id("123", {
        "ticket": "VTBR",
        "buy_price": 93.5,
        "count": 10,
        "take_profit": 0.5,
        "stop_loss": 1.0
    })

    stocks = await repo.get_user_stocks_by_telegram_id("123")
    assert stocks is not None
    assert len(stocks) == 1
    assert stocks[0].ticket == "VTBR"
    assert stocks[0].count == 10


@pytest.mark.asyncio
async def test_add_stock_to_user_raises_for_missing_user(repo):
    with pytest.raises(Exception):
        await repo.add_stock_to_user_by_telegram_id("nonexistent", {})


@pytest.mark.asyncio
async def test_remove_stock_removes_position(repo):
    user = make_user("123", "test_user")
    await repo.create_user(user)
    await repo.add_stock_to_user_by_telegram_id("123", {
        "ticket": "VTBR",
        "buy_price": 93.5,
        "count": 10,
        "take_profit": 0.5,
        "stop_loss": 1.0
    })
    stocks = await repo.get_user_stocks_by_telegram_id("123")
    stock_id = stocks[0].id

    await repo.remove_stock_from_user_by_telegram_id("123", stock_id)

    stocks_after = await repo.get_user_stocks_by_telegram_id("123")
    assert stocks_after is None or len(stocks_after) == 0


@pytest.mark.asyncio
async def test_remove_stock_raises_for_missing_stock(repo):
    user = make_user("123", "test_user")
    await repo.create_user(user)

    with pytest.raises(Exception):
        await repo.remove_stock_from_user_by_telegram_id("123", 999)