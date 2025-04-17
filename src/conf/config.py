from pydantic import ConfigDict, EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    A configuration class for application settings.

    This class automatically loads the settings from the environment or `.env' file using the Pydantic library.

    Attributes:
    - DB_URL (str): URL to connect to the database.
    - JWT_SECRET (str): The secret key for signing JWT tokens.
    - JWT_ALGORITHM (str): Algorithm for generating JWT tokens (default: HS256).
    - JWT_EXPIRATION_SECONDS (int): Token lifetime in seconds (default: 3600).

    - MAIL_USERNAME (EmailStr): Login for the SMTP server.
    - MAIL_PASSWORD (str): Password for the SMTP server.
    - MAIL_FROM (EmailStr): Email address from which the emails are sent.
    - MAIL_PORT (int): The port to connect to the SMTP server.
    - MAIL_SERVER (str): The domain name of the SMTP server.
    - MAIL_FROM_NAME (str): Sender name for emails (default: “API Service”).
    - MAIL_STARTTLS (bool): Whether to use STARTTLS for SMTP (default: False).
    - MAIL_SSL_TLS (bool): Whether to use SSL/TLS for SMTP (default: True).
    - USE_CREDENTIALS (bool): Whether to use credentials for SMTP (default: True).
    - VALIDATE_CERTS (bool): Whether to validate SSL certificates (default: True).

    - CLOUDINARY_NAME (str): The name of the Cloudinary account.
    - CLOUDINARY_API_KEY (int): The API key for Cloudinary.
    - CLOUDINARY_API_SECRET (str): The secret key for Cloudinary.

    Methods:
    - model_config: Configuration to load settings from the `.env' file.

    Example usage:
    ```
    from src.conf.config import settings
    print(settings.DB_URL)
    ```
    """
    DB_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 3600

    MAIL_USERNAME: EmailStr
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str = "API Service"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = False

    CLOUDINARY_NAME: str
    CLOUDINARY_API_KEY: int
    CLOUDINARY_API_SECRET: str

    model_config = ConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


settings = Settings()
