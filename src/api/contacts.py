from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas import ContactModel, ContactResponse
from src.services.contacts import ContactService

router = APIRouter(prefix="/contacts", tags=["contacts"])


def not_found():
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Contact not found"
    )


def get_contact_service(db: AsyncSession = Depends(get_db)) -> ContactService:
    return ContactService(db)


@router.get("/birthdays", response_model=List[ContactResponse])
async def get_upcoming_birthdays(
    days: int = Query(default=7, ge=1),
    service: ContactService = Depends(get_contact_service),
):
    return await service.get_upcoming_birthdays(days)


@router.get("/", response_model=List[ContactResponse])
async def get_contacts(
    name: str = "",
    surname: str = "",
    email: str = "",
    skip: int = 0,
    limit: int = 100,
    service: ContactService = Depends(get_contact_service),
):
    return await service.get_contacts(name, surname, email, skip, limit)


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int,
    service: ContactService = Depends(get_contact_service),
):
    contact = await service.get_contact(contact_id)
    if contact is None:
        not_found()
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactModel,
    service: ContactService = Depends(get_contact_service),
):
    return await service.create_contact(body)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    body: ContactModel,
    service: ContactService = Depends(get_contact_service),
):
    contact = await service.update_contact(contact_id, body)
    if contact is None:
        not_found()
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(
    contact_id: int,
    service: ContactService = Depends(get_contact_service),
):
    contact = await service.remove_contact(contact_id)
    if contact is None:
        not_found()
    return contact