#to be used in the future.
import os  # noqa
from fastapi import Depends, Request, HTTPException, status, APIRouter, Form
from datetime import datetime, timedelta, timezone
from sqlmodel import Session,select, SQLModel
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from snacks.db import get_session, User, Review, templates #noqa
from fastapi.responses import RedirectResponse #noqa
from jose import jwt, JWTError
from typing import Annotated #noqa
from fastapi.responses import HTMLResponse
SECRET_KEY = 'af842c14eb50cd7009202a3cdf0948122a325bed0f8fc4596035f8208fe57d9c'
ALGORITHM = 'HS256'


authrouter = APIRouter(
    prefix='/auth',
    tags=['auth']
)

bcrypt_context= CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer= OAuth2PasswordBearer(tokenUrl='auth/token')


class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    username: str | None = None



@authrouter.post("/register", status_code= status.HTTP_201_CREATED, response_model=User)
async def create_user(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_session)
):
    
    existing_user = db.exec(select(User).where(User.username == username)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )
    
    
    user_info = User(username=username, password=bcrypt_context.hash(password))
    db.add(user_info)
    db.commit()
    db.refresh(user_info)

    
    return RedirectResponse(url="/auth/login", status_code=303)


@authrouter.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate user.")
    
    token = create_access_token(user.username, user.user_id, timedelta(minutes=20))

    # Return the token in the response
    return {"access_token": token, "token_type": "bearer"}

def authenticate_user(username: str, password: str, db: Session):
    user = db.exec(select(User).where(User.username == username)).first()
    if not user: 
        return False
    if not bcrypt_context.verify(password, user.password):
        return False
    return user

def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {"sub": username, "id": user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM) 


def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
    

def get_current_user(token: str = Depends(oauth2_bearer), db: Session = Depends(get_session)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is invalid or expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = db.exec(User).filter(User.username == username).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or expired",
            headers={"WWW-Authenticate": "Bearer"},
        )