from datetime import date, timedelta
from typing import List, Optional

from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact
from src.schemas import ContactModel


class ContactRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_contacts(
        self, name: str, surname: str, email: str, skip: int, limit: int
    ) -> List[Contact]:
        stmt = (
            select(Contact)
            .where(Contact.name.contains(name))
            .where(Contact.surname.contains(surname))
            .where(Contact.email.contains(email))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_contact_by_id(self, contact_id: int) -> Optional[Contact]:
        stmt = select(Contact).filter_by(id=contact_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_contact(self, body: ContactModel) -> Contact:
        data = (
            body.model_dump(exclude_unset=True)
            if hasattr(body, "model_dump")
            else body.dict(exclude_unset=True)
        )
        contact = Contact(**data)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def update_contact(
        self, contact_id: int, body: ContactModel
    ) -> Optional[Contact]:
        contact = await self.get_contact_by_id(contact_id)
        if contact:
            data = (
                body.model_dump(exclude_unset=True)
                if hasattr(body, "model_dump")
                else body.dict(exclude_unset=True)
            )
            for key, value in data.items():
                setattr(contact, key, value)
            await self.db.commit()
            await self.db.refresh(contact)
        return contact

    async def remove_contact(self, contact_id: int) -> Optional[Contact]:
        contact = await self.get_contact_by_id(contact_id)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def is_contact_exists(self, email: str, phone: str) -> bool:
        stmt = select(Contact).where(
            or_(
                Contact.email == email,
                Contact.phone == phone
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().first() is not None

    async def get_upcoming_birthdays(self, days: int) -> List[Contact]:
        today = date.today()
        end_date = today + timedelta(days=days)

        # Порівняння лише місяця і дня народження
        query = select(Contact).where(
            or_(
                and_(
                    func.date_part("month", Contact.birthday) == today.month,
                    func.date_part("day", Contact.birthday) >= today.day,
                ),
                and_(
                    func.date_part("month", Contact.birthday) == end_date.month,
                    func.date_part("day", Contact.birthday) <= end_date.day,
                ),
            )
        ).order_by(func.date_part("month", Contact.birthday), func.date_part("day", Contact.birthday))

        result = await self.db.execute(query)
        return result.scalars().all()