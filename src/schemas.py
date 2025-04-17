from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict, EmailStr

from src.database.models import UserRole


class ContactModel(BaseModel):
    """
    A model for creating or updating a contact.

    Attributes:
        name: the name of the contact (minimum 2 characters, maximum 50 characters)
        surname: surname of the contact (minimum 2 characters, maximum 50 characters)
        email: email address of the contact (minimum 7 characters, maximum 100 characters)
        phone: phone number of the contact (minimum 7 characters, maximum 20 characters)
        birthday: date of birth of the contact
        info: additional information about the contact (optional)
    """
    name: str = Field(min_length=2, max_length=50)
    surname: str = Field(min_length=2, max_length=50)
    email: EmailStr
    phone: str = Field(min_length=7, max_length=20)
    birthday: date
    info: Optional[str] = None


class ContactResponse(ContactModel):
    """
    A model for responding when receiving a contact from the database.

    Attributes:
        id: unique identifier of the contact
        created_at: date and time when the contact was created
        updated_at: date and time when the contact was last updated (optional)
    """
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)


class User(BaseModel):
    """
    A model for representing a user.

    Attributes:
        id: unique user identifier
        username: user name
        email: user's email address
        avatar: URL to the user's avatar
        role: the role of the user (for example, administrator or user)
    """
    id: int
    username: str
    email: str
    avatar: str
    role: UserRole
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """
    A model for creating a new user.

    Attributes:
        username: user name
        email: user's email address
        password: user password (minimum 4 characters, maximum 128 characters)
        role: the role of the user (for example, administrator or user)
    """
    username: str
    email: str
    password: str
    role: UserRole


class Token(BaseModel):
    """
    A model for returning an access token.

    Attributes:
        access_token: access token
        token_type: type of token (for example, Bearer)
    """
    access_token: str
    token_type: str


class RequestEmail(BaseModel):
    """
    Model for requesting an email for password recovery.

    Attribute:
        email: user's email address
    """
    email: EmailStr

class ResetPassword(BaseModel):
    """
    Model for resetting the password.

    Attributes:
        email: user's email address
        password: new user password (minimum 4 characters, maximum 128 characters)
    """
    email: EmailStr
    password: str = Field(min_length=4, max_length=128, description="Новий пароль")