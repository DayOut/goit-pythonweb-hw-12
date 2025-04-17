import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Contact, User
from src.repository.contacts import ContactRepository
from src.schemas import ContactModel


@pytest.fixture(scope="function")
def mock_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture(scope="function")
def contact_repository(mock_session):
    return ContactRepository(mock_session)


@pytest.fixture(scope="function")
def user():
    return User(id=1, username="testuser", role="user")


@pytest.fixture(scope="function")
def contact(user: User):
    return Contact(
        id=1,
        name="Evan",
        surname="Jedi",
        email="evan@example.com",
        phone="111-222-3333",
        birthday="2002-02-02",
        user=user,
    )


@pytest.fixture(scope="function")
def contact_body():
    return ContactModel(
        name="Evan",
        surname="Jedi",
        email="evan@example.com",
        phone="111-222-3333",
        birthday="2002-02-02",
    )


class TestContactRepository:
    @pytest.mark.asyncio
    async def test_get_contacts(self, contact_repository, mock_session, user, contact):
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [contact]
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        contacts = await contact_repository.get_contacts(
            skip=0, limit=10, user=user, name="", surname="", email=""
        )

        # Assert
        assert len(contacts) == 1
        assert contacts[0].name == "Evan"
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_contact_by_id(self, contact_repository, mock_session, user, contact):
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = contact
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        contact_record = await contact_repository.get_contact_by_id(contact_id=1, user=user)

        # Assert
        assert contact_record is not None
        assert contact_record.id == 1
        assert contact_record.name == "Evan"
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_contact_successful(self, contact_repository, mock_session, user, contact_body):
        # Act
        result = await contact_repository.create_contact(body=contact_body, user=user)

        # Assert
        assert isinstance(result, Contact)
        assert result.name == "Evan"
        mock_session.add.assert_called_once()
        mock_session.commit.assert_awaited_once()
        mock_session.refresh.assert_awaited_once_with(result)

    @pytest.mark.asyncio
    async def test_create_contact_failure(self, contact_repository, mock_session, user, contact_body):
        # Act
        result = await contact_repository.create_contact(body=contact_body, user=user)

        # Assert
        assert isinstance(result, Contact)
        assert result.name != "Evan2"
        mock_session.add.assert_called_once()
        mock_session.commit.assert_awaited_once()
        mock_session.refresh.assert_awaited_once_with(result)

    @pytest.mark.asyncio
    async def test_update_contact(self, contact_repository, mock_session, user, contact):
        # Arrange
        contact_data = ContactModel(**{k: v for k, v in contact.__dict__.items() if not k.startswith('_')})
        contact_data.name = "Evan2"
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = contact
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await contact_repository.update_contact(contact_id=1, body=contact_data, user=user)

        # Assert
        assert result is not None
        assert result.name == "Evan2"
        mock_session.commit.assert_awaited_once()
        mock_session.refresh.assert_awaited_once_with(contact)

    @pytest.mark.asyncio
    async def test_remove_contact(self, contact_repository, mock_session, user, contact):
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = contact
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        result = await contact_repository.remove_contact(contact_id=1, user=user)

        # Assert
        assert result is not None
        assert result.name == "Evan"
        mock_session.delete.assert_called_once_with(contact)
        mock_session.commit.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_is_contact_exists_success(self, contact_repository, mock_session, user, contact):
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = contact
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        is_contact_exist = await contact_repository.is_contact_exists(
            "qwerty@gmail.com", "111-22-33", user=user
        )

        # Assert
        assert is_contact_exist is True
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_is_contact_exists_failure(self, contact_repository, mock_session, user):
        # Arrange
        mock_result = MagicMock()
        mock_result.scalars.return_value.first.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        # Act
        is_contact_exist = await contact_repository.is_contact_exists(
            "qwerty@gmail.com", "111-22-33", user=user
        )

        # Assert
        assert is_contact_exist is False
        mock_session.execute.assert_called_once()