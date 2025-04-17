from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas import UserCreate


class UserRepository:
    def __init__(self, session: AsyncSession):
        """
        Initialize the UserRepository with a database session.

        Parameters:
        - session: AsyncSession – the async database session to use.
        """
        self.db = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Retrieve a user by their unique ID.

        Parameters:
        - user_id: int – the ID of the user to retrieve.

        Returns:
        - User | None: The user if found, otherwise None.
        """
        stmt = select(User).filter_by(id=user_id)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Retrieve a user by their username.

        Parameters:
        - username: str – the username of the user to retrieve.

        Returns:
        - User | None: The user if found, otherwise None.
        """
        stmt = select(User).filter_by(username=username)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Retrieve a user by their email address.

        Parameters:
        - email: str – the email of the user to retrieve.

        Returns:
        - User | None: The user if found, otherwise None.
        """
        stmt = select(User).filter_by(email=email)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def create_user(self, body: UserCreate, avatar: str = None) -> User:
        """
        Create a new user in the database.

        Parameters:
        - body: UserCreate – the data used to create the user.
        - avatar: str | None – optional URL of the user's avatar.

        Returns:
        - User: The newly created user.
        """
        user = User(
            **body.model_dump(exclude_unset=True, exclude={"password"}),
            hashed_password=body.password,
            avatar=avatar
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def confirmed_email(self, email: str) -> None:
        """
        Mark the user’s email as confirmed.

        Parameters:
        - email: str – the email address to mark as confirmed.

        Returns:
        - None
        """
        user = await self.get_user_by_email(email)
        user.confirmed = True
        await self.db.commit()

    async def update_avatar_url(self, email: str, url: str) -> User:
        """
        Update the avatar URL for the specified user.

        Parameters:
        - email: str – the email of the user whose avatar is to be updated.
        - url: str – the new avatar URL.

        Returns:
        - User: The updated user.
        """
        user = await self.get_user_by_email(email)
        user.avatar = url
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def reset_password(self, user_id: int, password: str) -> User:
        """
        Reset user's password.
        """
        user = await self.get_user_by_id(user_id)
        if user:
            user.hashed_password = password
            await self.db.commit()
            await self.db.refresh(user)
        return user