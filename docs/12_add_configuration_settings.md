# Add configuration settings

Add the configuration settings to the .env file. And use the pydantic_settings library to load the settings.

1. Create a `.env` file in the root directory and add the configuration settings.
2. Create a `config.py` file in the `app` directory and use the pydantic_settings library to load the settings.
3. Update the `database.py` file to use the settings.
4. Update the `oauth2.py` file to use the settings.

## 1. Create a `.env` file in the root directory and add the configuration settings

```env
DATABASE_HOSTNAME=localhost
DATABASE_PORT=5432
DATABASE_PASSWORD=root
DATABASE_NAME=fastapi
DATABASE_USERNAME=postgres
SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f40ad1f5701fe593c56
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 2. Create a `config.py` file in the `app` directory and use the pydantic_settings library to load the settings

```python
from os import path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        env_file = ".env"


settings = Settings()
```

- The `Settings` class is a subclass of `BaseSettings` and it is used to load the settings from the `.env` file.
- The `env_file` class attribute is used to specify the path to the `.env` file.
- The `settings` variable is used to access the settings.

## 3. Update the `database.py` file to use the settings

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# 'postgresql://<username>:<password>@<host>:<port>/<database_name>'
# We are using the PostgreSQL database
SQLALCHEMY_DATABASE_URL = (f'postgresql+psycopg2://{settings.database_username}:'
                           f'{settings.database_password}@{settings.database_hostname}'
                           f':{settings.database_port}/{settings.database_name}')

# Create the engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create the session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db  # This will yield the database session
    finally:
        db.close()  # This will close the database session
```

## 4. Update the `oauth2.py` file to use the settings

Use the settings in the `oauth2.py` file. Import the settings from the `config.py` file and use the settings in the
`oauth2.py` file.

> Note: The `oauth2.py` file is used to authenticate the user and generate the access token.

```python
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
```
