import os  # noqa
import jwt  # noqa
from fastapi import Depends, HTTPException, status, Form #noqa
from datetime import datetime, timedelta, timezone  
from pydantic import BaseModel 
from sqlmodel import Session,select
from passlib.context import CryptContext  
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from snacks.db import get_session, User, Review #noqa 
from fastapi.responses import RedirectResponse #noqa


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="signin")
SECRET_KEY = "af842c14eb50cd7009202a3cdf0948122a325bed0f8fc4596035f8208fe57d9c"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30



class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None




# for has passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# hashed pwd
def get_hashpwd(password):
    return pwd_context.hash(password)


#find user
def get_user(db: Session = Depends(get_session), username: str = None):
    return db.exec(select(User).where(User.username == username)).first()

#verify pwd = hashed pwd
def verify_password(plain_password, hashed_pwd):
    return pwd_context.verify(plain_password, hashed_pwd)


def authenticate_user(
    db: Session = Depends(get_session), username: str = None, password: str = None
):
    user = get_user(db, username)
    if not user:
        return False  # error or something of the sort.
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta = None):
    encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    encode.update({"exp": expire})
    encoded_jwt = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

