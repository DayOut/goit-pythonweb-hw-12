from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    BackgroundTasks,
    Request,
)
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from src.schemas import UserCreate, Token, User, RequestEmail
from src.services.email import send_confirm_email, send_reset_password_email
from src.services.auth import (
    create_access_token,
    Hash,
    get_email_from_token,
    get_password_from_token,
)
from src.services.users import UserService
from src.database.db import get_db
from src.schemas import ResetPassword

router = APIRouter(prefix="/auth", tags=["auth"])


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(db)


USER_EXISTS_EMAIL = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="User with this email already exists",
)

USER_EXISTS_USERNAME = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="User with this username already exists",
)

INVALID_CREDENTIALS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid username or password",
    headers={"WWW-Authenticate": "Bearer"},
)

EMAIL_NOT_CONFIRMED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Email address not confirmed",
)

VERIFICATION_ERROR = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Verification error",
)


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Registering a new user.

    Parameters:
    - user_data (UserCreate): The data of the new user.
    - background_tasks (BackgroundTasks): The object to run the background tasks.
    - request: A request to get the base URL.
    - db (AsyncSession): A session to work with the database.

    Returns:
    - User: Data of the registered user.

    Throws:
    - HTTP exception (409): If a user with this address or name already exists.
    """
    user_service = UserService(db)
    if await user_service.get_user_by_email(user_data.email):
        raise USER_EXISTS_EMAIL

    if await user_service.get_user_by_username(user_data.username):
        raise USER_EXISTS_USERNAME

    user_data.password = Hash().get_password_hash(user_data.password)
    new_user = await user_service.create_user(user_data)

    background_tasks.add_task(
        send_confirm_email, new_user.email, new_user.username, request.base_url
    )

    return new_user


@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    User authorization.

    Parameters:
    - form_data (OAuth2PasswordRequestForm): Data for authorization.
    - db (AsyncSession): The database session.

    Returns:
    - Token: JWT access token.

    Throws:
    - HTTPException (401): If the login or password is incorrect or the email is not verified.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_username(form_data.username)

    if not user or not Hash().verify_password(form_data.password, user.hashed_password):
        raise INVALID_CREDENTIALS

    if not user.confirmed:
        raise EMAIL_NOT_CONFIRMED

    access_token = await create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirmed_email/{token}")
async def confirmed_email(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Confirmation of the user's email.

    Parameters:
    - token (str): The confirmation token.
    - db (AsyncSession): The database session.

    Returns:
    - dict: A message indicating successful confirmation.

    Throws:
    - HTTPException (400): If the token is invalid or the user is not found.
    """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)

    if not user:
        raise VERIFICATION_ERROR

    if user.confirmed:
        return {"message": "Your email address is already confirmed"}

    await user_service.confirmed_email(email)
    return {"message": "Email successfully confirmed"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Send a confirmation email to the user.

    Parameters:
    - body (RequestEmail): Data for the request (user's email).
    - background_tasks (BackgroundTasks): The object to run the background tasks.
    - request (Request): The request to get the base URL.
    - db (AsyncSession): The database session.

    Returns:
    - dict: A message about the request sent.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user and user.confirmed:
        return {"message": "Your email address is already confirmed"}

    if user:
        background_tasks.add_task(
            send_confirm_email, user.email, user.username, request.base_url
        )

    return {"message": "Check your email for confirmation instructions"}


@router.post("/reset_password")
async def reset_password_request(
    body: ResetPassword,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Request for password reset.

    Parameters:
    - body (ResetPassword): Data for the request (email and new password).
    - background_tasks (BackgroundTasks): The object to run the background tasks.
    - request (Request): The request to get the base URL.
    - db (AsyncSession): The database session.

    Returns:
    - dict: A message about the request sent.

    Throws:
    - HTTPException (400): If the email is not verified.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)
    if not user:
        return {"message": "Check your email for password reset instructions"}
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your email address is not confirmed",
        )
    hashed_password = Hash().get_password_hash(body.password)
    reset_token = await create_access_token(
        data={"sub": user.email, "password": hashed_password}
    )
    background_tasks.add_task(
        send_reset_password_email,
        to_email=body.email,
        username=user.username,
        host=str(request.base_url),
        reset_token=reset_token,
    )
    return {"message": "Check your email for password reset instructions"}


@router.get("/confirm_reset_password/{token}")
async def confirm_reset_password(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Confirmation of password reset.

    Parameters:
    - token (str): The password reset confirmation token.
    - db (AsyncSession): The database session.

    Returns:
    - dict: A message indicating successful password reset.

    Throws:
    - HTTPException (400): If the token is invalid.
    - HTTPException (404): If the user was not found.
    """
    email = await get_email_from_token(token)
    hashed_password = await get_password_from_token(token)
    if not email or not hashed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email was not found",
        )
    await user_service.reset_password(user, hashed_password)
    return {"message": "Password has been successfully changed"}