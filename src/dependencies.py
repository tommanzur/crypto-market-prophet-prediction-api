import jwt
from datetime import datetime, timedelta
from models import User
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import config

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

fake_users_db = {
    "johndoe": User(username="johndoe", full_name="John Doe", email="johndoe@example.com", hashed_password="fakehashedsecret", disabled=False)
}

def fake_hash_password(password: str):
    return "fakehashed" + password

def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user or not fake_hash_password(password) == user.hashed_password:
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token or token != str(config.TOKEN):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token