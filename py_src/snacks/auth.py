#to be used in the future.
import os  # noqa
from fastapi import Depends, HTTPException, status, Form, APIRouter #noqa
from datetime import datetime, timedelta, timezone
from sqlmodel import Session,select, SQLModel
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from snacks.db import get_session, User, Review #noqa
from fastapi.responses import RedirectResponse #noqa
from jose import jwt, JWTError



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
async def create_user(user: User, db: Session = Depends(get_session)):
    user_info = User(username = user.username,
                     password = bcrypt_context.hash(user.password))
    
    db.add(user_info)
    db.commit()

    return {"message": "User created successfully", "user": user_info}


'''# hashed pwd
def get_hashpwd(password):
    return bcrypt_context.hash(password)

#verify pwd = hashed pwd
def verify_password(plain_password, hashed_pwd):
    return bcrypt_context.verify(plain_password, hashed_pwd)
'''
'''def generate_token(username: str)

#find user
def get_user(db: Session = Depends(get_session), username: str = None):
    return db.exec(select(User).where(User.username == username)).first()




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


'''