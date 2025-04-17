from typing import List

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import Contact
from src.database.models import User
from src.repository.contacts import ContactRepository
from src.schemas import ContactModel


class ContactService:
    def __init__(self, db: AsyncSession):
        """
        Initialize the ContactService with a database session.

        Parameters:
        - db: AsyncSession – the async database session to use.
        """
        self.repository = ContactRepository(db)

    async def create_contact(self, body: ContactModel, user: User):
        """
        Create a new contact for the given user.

        Parameters:
        - body: ContactModel – the contact data to create.
        - user: User – the current authorized user.

        Returns:
        - Contact: The created contact object.

        Raises:
        - HTTPException: If a contact with the same email or phone already exists.
        """
        if await self.repository.is_contact_exists(body.email, body.phone, user):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Contact with '{body.email}' email or '{body.phone}' phone number already exists.",
            )
        return await self.repository.create_contact(body, user)

    async def get_contacts(
        self, name: str, surname: str, email: str, skip: int, limit: int, user: User
    ):
        """
        Retrieve a list of contacts filtered by name, surname, or email.

        Parameters:
        - name: str – filter by name.
        - surname: str – filter by surname.
        - email: str – filter by email.
        - skip: int – number of records to skip (pagination).
        - limit: int – maximum number of records to return.
        - user: User – the current authorized user.

        Returns:
        - List[Contact]: A list of filtered contacts.
        """
        return await self.repository.get_contacts(name, surname, email, skip, limit, user)

    async def get_contact(self, contact_id: int, user: User):
        """
        Retrieve a single contact by its ID.

        Parameters:
        - contact_id: int – the ID of the contact to retrieve.
        - user: User – the current authorized user.

        Returns:
        - Contact: The contact object if found.
        """
        return await self.repository.get_contact_by_id(contact_id, user)

    async def update_contact(self, contact_id: int, body: ContactModel, user: User):
        """
        Update an existing contact with new data.

        Parameters:
        - contact_id: int – the ID of the contact to update.
        - body: ContactModel – the new data to update the contact.
        - user: User – the current authorized user.

        Returns:
        - Contact: The updated contact object.
        """
        return await self.repository.update_contact(contact_id, body, user)

    async def remove_contact(self, contact_id: int, user: User):
        """
        Remove a contact by its ID.

        Parameters:
        - contact_id: int – the ID of the contact to remove.
        - user: User – the current authorized user.

        Returns:
        - Contact: The removed contact object.
        """
        return await self.repository.remove_contact(contact_id, user)

    async def get_upcoming_birthdays(self, days: int, user: User) -> List[Contact]:
        """
        Get a list of contacts with upcoming birthdays within a number of days.

        Parameters:
        - days: int – number of days from today to look ahead.
        - user: User – the current authorized user.

        Returns:
        - List[Contact]: A list of contacts with upcoming birthdays.
        """
        return await self.repository.get_upcoming_birthdays(days, user)