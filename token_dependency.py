from fastapi import status, HTTPException, Depends
from typing import Annotated
from config import SECRET_KEY, ALGORITHM
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from sql import SessionDep
from models.user import UserPublic
from routers.user_route import find_user
from fastapi.security import OAuth2PasswordBearer
import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep) -> UserPublic:
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        mp = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if mp is None:
            raise exception
        username = mp.get("sub")
        if username is None:
            raise exception
        userinfo_db = find_user(username, session)
        if userinfo_db is None:
            raise exception
        return UserPublic(**userinfo_db.model_dump())
    except ExpiredSignatureError:
        raise HTTPException(
            detail="Token has expired",
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )
    except InvalidTokenError:
        raise exception


user_token_dependency = get_current_user
