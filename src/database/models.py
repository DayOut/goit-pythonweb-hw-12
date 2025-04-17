from enum import Enum
from sqlalchemy import (
    Integer,
    String,
    DateTime,
    Date,
    Column,
    func,
    ForeignKey,
    Boolean,
    Enum as SqlEnum,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class UserRole(str, Enum):
    """
    List of user roles.

    Values:
    - USER: The normal user.
    - ADMIN: Administrator.
    """

    USER = "user"
    ADMIN = "admin"


class Contact(Base):
    """
    Model for the 'contacts' table.

    Attributes:
    - id: Primary key.
    - name: The name of the contact (required).
    - surname: Last name of the contact (required).
    - email: Email of the contact (unique, required).
    - phone: Phone number of the contact (unique, required).
    - birthday: Date of birth of the contact (required).
    - created_at: Date the record was created (automatic).
    - updated_at: The date the record was last updated (automatic).
    - info: Additional information about the contact.
    - user_id: Foreign key for binding to the user.
    - user: The relationship to the User model.
    """

    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    surname = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    phone = Column(String(20), nullable=False, unique=True)
    birthday = Column(Date, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    info = Column(String(500), nullable=True)
    user_id = Column(
        "user_id", ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user = relationship("User", backref="contacts")


class User(Base):
    """
    Model for the 'users' table.

    Attributes:
    - id: Primary key.
    - username: Unique username of the user.
    - email: Unique email address.
    - hashed_password: The encrypted password.
    - created_at: Date the record was created (automatically).
    - avatar: URL of the user's avatar.
    - confirmed: Whether the user is confirmed.
    - role: The role of the user (USER or ADMIN).
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    role = Column(SqlEnum(UserRole), default=UserRole.USER, nullable=False)
