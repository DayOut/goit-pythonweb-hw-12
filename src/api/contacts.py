from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas import ContactModel, ContactResponse, User
from src.services.auth import get_current_user
from src.services.contacts import ContactService

router = APIRouter(prefix="/contacts", tags=["contacts"])


NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Contact not found"
)


def get_contact_service(db: AsyncSession = Depends(get_db)) -> ContactService:
    return ContactService(db)


@router.get("/birthdays", response_model=List[ContactResponse])
async def get_upcoming_birthdays(
    days: int = Query(default=7, ge=1),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Get a list of contacts who have a birthday within the specified number of days.

    Parameters:
    - days (int): The number of days to search (minimum 1).
    - db (AsyncSession): The database session.
    - user (User): The current authorized user.

    Returns:
    - List[ContactResponse]: A list of contacts with upcoming birthdays.
    """
    contact_service = ContactService(db)
    return await contact_service.get_upcoming_birthdays(days, user)


@router.get("/", response_model=List[ContactResponse])
async def get_contacts(
    name: str = "",
    surname: str = "",
    email: str = "",
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Search for contacts by filters.

    Parameters:
    - name (str): The name of the contact (optional).
    - surname (str): Last name of the contact (optional).
    - email (str): Email of the contact (optional).
    - skip (int): The number of records to skip (default is 0).
    - limit (int): The maximum number of records to return (default is 100).
    - db (AsyncSession): The database session.
    - user (User): The current authorized user.

    Returns:
    - List[ContactResponse]: A list of contacts that match the search criteria.
    """
    contact_service = ContactService(db)
    return await contact_service.get_contacts(name, surname, email, skip, limit, user)


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Get information about a contact by its ID.

    Parameters:
    - contact_id (int): The ID of the contact.
    - db (AsyncSession): The database session.
    - user (User): The current authorized user.

    Returns:
    - ContactResponse: The data of the contact.

    Throws:
    - HTTPException (404): If the contact was not found.
    """
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id, user)
    if contact is None:
        raise NOT_FOUND
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactModel,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Create a new contact.

    Parameters:
    - body (ContactModel): The data of the new contact.
    - db (AsyncSession): The database session.
    - user (User): The current authorized user.

    Returns:
    - ContactResponse: The data of the created contact.
    """
    contact_service = ContactService(db)
    return await contact_service.create_contact(body, user)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    body: ContactModel,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Update contact details by contact ID.

    Parameters:
    - body (ContactModel): The new contact data.
    - contact_id (int): The contact ID.
    - db (AsyncSession): The database session.
    - user (User): The current authorized user.

    Returns:
    - ContactResponse: The updated contact data.

    Throws:
    - HTTPException (404): If the contact was not found.
    """
    contact_service = ContactService(db)
    contact = await contact_service.update_contact(contact_id, body, user)
    if contact is None:
        raise NOT_FOUND
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Delete a contact by its ID.

    Parameters:
    - contact_id (int): The ID of the contact.
    - db (AsyncSession): The database session.
    - user (User): The current authorized user.

    Returns:
    - ContactResponse: The data of the deleted contact.

    Throws:
    - HTTPException (404): If the contact was not found.
    """
    contact_service = ContactService(db)
    contact = await contact_service.remove_contact(contact_id, user)
    if contact is None:
        raise NOT_FOUND
    return contact