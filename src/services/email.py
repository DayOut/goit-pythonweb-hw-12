from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import create_email_token
from src.conf.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)


async def send_confirm_email(to_email: EmailStr, username: str, host: str) -> None:
    """
    Sends an email to verify the email address.

    Creates an email verification token and sends an email to the user
    with a link to verify the email.

    Arguments:
        to_email: The recipient's email address.
        username: Username to personalize the email.
        host: The host (home address) used to build the link.

    Throws:
        ConnectionErrors: If an error occurs while connecting to the email server.
    """
    try:
        # Створення токену для підтвердження електронної пошти
        token_verification = create_email_token({"sub": to_email})
        # Формування повідомлення для відправки
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[to_email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        # Ініціалізація FastMail та відправка повідомлення
        fm = FastMail(conf)
        await fm.send_message(message, template_name="verify_email.html")
    except ConnectionErrors as err:
        print(err)


async def send_reset_password_email(
    to_email: EmailStr, username: str, host: str, reset_token: str
) -> None:
    """
    Sends an email to reset the password.

    Generates a link to reset the password and sends an email with instructions
    to change the password.

    Arguments:
        to_email: The recipient's email address.
        username: Username to personalize the email.
        host: The host (home address) used to build the link.
        reset_token: Token for resetting the password attached to the link.

    Throws:
        ConnectionErrors: If an error occurs while connecting to the email server.
    """
    try:
        # Формування посилання для скидання пароля
        reset_link = f"{host}api/auth/confirm_reset_password/{reset_token}"

        # Формування повідомлення для відправки
        message = MessageSchema(
            subject="Important: Update your account information",
            recipients=[to_email],
            template_body={"reset_link": reset_link, "username": username},
            subtype=MessageType.html,
        )

        # Ініціалізація FastMail та відправка повідомлення
        fm = FastMail(conf)
        await fm.send_message(message, template_name="reset_password.html")
    except ConnectionErrors as err:
        print(err)