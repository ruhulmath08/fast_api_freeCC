from jose import jwt, JWTError
from sqlalchemy.orm import Session
from . import schemas, database, models
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# SECRET_KEY
# Algorithm
# Expiration time

# Secret key for JWT for learning purposes
SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


# Create the access token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Verify the access token
def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: int = payload.get("user_id")
        if not id:
            raise credentials_exception
        token_data = schemas.TokenData(id=id)
    except JWTError:
        raise credentials_exception
    return token_data


# Get the current user
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    # Create a credentials exception
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials",
                                          headers={"WWW-Authenticate": "Bearer"})

    # Verify the access token
    token = verify_access_token(token, credentials_exception)

    # Get the user from the database
    user = db.query(models.User).filter(models.User.id == token.id).first()
    # If the user is not found, raise a credentials exception
    if not user:
        raise credentials_exception
    # Return the user
    return user
