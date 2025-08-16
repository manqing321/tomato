from fastapi import APIRouter, HTTPException, Depends, status
from sql import SessionDep
from sqlmodel import select, Session
from models.user import User, UserPublic
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import jwt
from config import ALGORITHM, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def find_user(username: str, session: Session) -> User | None:
    statement = select(User).where(User.name == username)
    user = session.exec(statement).first()
    return user


@router.post("/create_user/", response_model=UserPublic)
async def create_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):
    try:
        name = form_data.username
        pwd = form_data.password
        existing_user = find_user(name, session)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
        hashed_password = get_password_hash(pwd)
        db_user = User(name=name, hashed_pwd=hashed_password)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


def create_jwt_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    mp = {
        "sub": username,
        "exp": expire,
    }
    return jwt.encode(mp, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/token/")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    name = form_data.username
    pwd = form_data.password
    user = find_user(name, session)
    if not user:
        raise exception
    if not pwd_context.verify(pwd, user.hashed_pwd):
        raise exception
    jwt_token = create_jwt_token(name)
    return {"access_token": jwt_token, "token_type": "bearer"}



