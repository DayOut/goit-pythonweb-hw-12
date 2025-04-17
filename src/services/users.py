from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar
from src.repository.users import UserRepository
from src.schemas import UserCreate


class UserService:
    def __init__(self, db: AsyncSession):
        """
        Initialize the UserService with a database session.

        Parameters:
        - db: AsyncSession – the async database session to use.
        """
        self.repository = UserRepository(db)

    async def create_user(self, body: UserCreate):
        """
        Create a new user and generate a Gravatar avatar if possible.

        Parameters:
        - body: UserCreate – user registration data.

        Returns:
        - User: The newly created user.
        """
        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)

        return await self.repository.create_user(body, avatar)

    async def get_user_by_id(self, user_id: int):
        """
        Retrieve a user by their unique ID.

        Parameters:
        - user_id: int – the ID of the user.

        Returns:
        - User | None: The user if found, otherwise None.
        """
        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str):
        """
        Retrieve a user by their username.

        Parameters:
        - username: str – the username of the user.

        Returns:
        - User | None: The user if found, otherwise None.
        """
        return await self.repository.get_user_by_username(username)

    async def get_user_by_email(self, email: str):
        """
        Retrieve a user by their email address.

        Parameters:
        - email: str – the email of the user.

        Returns:
        - User | None: The user if found, otherwise None.
        """
        return await self.repository.get_user_by_email(email)

    async def confirmed_email(self, email: str):
        """
        Mark a user's email as confirmed.

        Parameters:
        - email: str – the email to confirm.

        Returns:
        - None
        """
        return await self.repository.confirmed_email(email)

    async def update_avatar_url(self, email: str, url: str):
        """
        Update the avatar URL of the user.

        Parameters:
        - email: str – the email of the user to update.
        - url: str – the new avatar URL.

        Returns:
        - User: The updated user.
        """
        return await self.repository.update_avatar_url(email, url)