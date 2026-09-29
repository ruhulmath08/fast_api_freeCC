# Add User Authentication

1. Add models to the database
2. Add a schema for the user
3. Use email validator library for email validation (email-validator)
4. Working with passwords
5. Full code

## 1. Add models to the database

Add a model for the user in the `app/models.py` file.

```python
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
```

## 2. Add a schema for the user

Add a schema for the user in the `app/schemas.py` file.

```python
from pydantic import EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
```

## 3. Use email validator library for email validation (email-validator)

We have to check that the email validator library (email-validator) is installed in the project. For checking this, we
can use the `freeze` command.

```bash
pip freeze | grep email-validator
```

If the email validator library is installed we will see like: `email-validator==2.3.0`. If nothing is printed, the
package is not installed. We can install it using the `pip install email-validator` command.

```bash
pip install email-validator
```

We can use the email validator library in the project to validate the email.

```python
from pydantic import EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str
```

Now, if we are trying to create a user with an invalid email, we will get a validation error.

**Request Body:**

```json
{
  "email": "mima@example.",
  "password": "abc123456"
}
```

**Response:**

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "email"],
      "msg": "value is not a valid email address: An email address cannot end with a period.",
      "input": "mima@example.",
      "ctx": {
        "reason": "An email address cannot end with a period."
      }
    }
  ]
}
```

## 4. Working with passwords

Now when working with user passwords, we have to be careful about the security of the passwords. We should not store the
passwords in the database in plain text, give back to the user the plain text password. We should hash the passwords
before storing them in the database.

1. **Removing the password from the response**
2. **Hashing the passwords**
3. **Separate the password hashing from the user creation**

### 1. Removing the password from the response

To remove the password from the response we add a new schema for the user in the `app/schemas.py` file and update the
create_user function in the `app/main.py` file.

**Update the Schema:**

```python
from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime


class UserOut(BaseModel):
   id: int
   email: EmailStr
   created_at: datetime
   # This is used to convert the SQLAlchemy model to a Pydantic model
   model_config = ConfigDict(from_attributes=True)
```

**Update the Function:**

```python
@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Create a new user
    new_user = models.User(**user.model_dump())
    # Add the new user to the database
    db.add(new_user)
    # Commit the changes to the database
    db.commit()
    # Refresh the new user to get the id
    db.refresh(new_user)
    # Return the new user
    return new_user
```

### 2. Hashing the passwords

For hashing the passwords we hava to install the following libraries:

```bash
pip install bcrypt
pip install passlib
```

We can use the passlib library to hash the passwords.

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Hash the password before storing it
    hashed_password = pwd_context.hash(user.password)
    user.password = hashed_password
    # Create a new user
    new_user = models.User(**user.model_dump())
    # Add the new user to the database
    db.add(new_user)
    # Commit the changes to the database
    db.commit()
    # Refresh the new user to get the id
    db.refresh(new_user)
    # Return the new user
    return new_user
```

### 3. Separating the password hashing from the user creation

To separate the password hashing from the user creation we add a new function to the `app/utils.py` file.

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(password: str):
    return pwd_context.hash(password)

def verify(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)
```

Now, we can use the `hash` and `verify` functions in the `app/main.py` file.

```python
@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Hash the password before storing it
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    # Create a new user
    new_user = models.User(**user.model_dump())
    # Add the new user to the database
    db.add(new_user)
    # Commit the changes to the database
    db.commit()
    # Refresh the new user to get the id
    db.refresh(new_user)
    # Return the new user
    return new_user
```

```python
@app.get("/users/{id}", response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db),):
    # Get the user from the database by id
    user = db.query(models.User).filter(models.User.id == id).first()
    # If the user is not found, raise a 404 error
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id: {id} does not exist")
    # Return the user
    return user
```

## 5. Now the full code is

The file architecture is:

```text
app/
├── main.py         # This is the main file of the application
├── database.py     # This is the file of the database connection
├── models.py       # This is the file of the database models
├── schemas.py      # This is the file of the schemas
└── utils.py        # This is the file of the utilities functions
```

**main.py:**

```python
from fastapi import Depends, FastAPI, HTTPException, Response, status
from sqlalchemy.orm import Session

from . import models, schemas, utils
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


@app.get("/posts", response_model=list[schemas.Post])
def get_posts(db: Session = Depends(get_db)):
    # Get all posts from the database
    posts = db.query(models.Post).all()
    # Return the posts
    return posts


# 201 Created: this request created a new post.
@app.post("/createpost", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db)):
    # Create a new post
    new_post = models.Post(**post.model_dump())
    # Add the new post to the database
    db.add(new_post)
    # Commit the changes to the database
    db.commit()
    # Refresh the new post to get the id
    db.refresh(new_post)
    # Return the new post
    return new_post


# Register this before /posts/{id}, or FastAPI treats "latest" as an id.
@app.get("/posts/latest", response_model=schemas.Post)
def get_latest_post(db: Session = Depends(get_db)):
    # Get the latest post from the database
    latest_post = db.query(models.Post).order_by(models.Post.id.desc()).first()
    # If no posts exist, raise a 404 error
    if latest_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No posts found")
    # Return the latest post
    return latest_post


@app.get("/posts/{id}", response_model=schemas.Post)
def get_post(id: int, db: Session = Depends(get_db)):
    # Get the post from the database by id
    post = db.query(models.Post).filter(models.Post.id == id).first()
    # If the post is not found, raise a 404 error
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    # Return the post
    return post


# 204 No Content: this request deleted a post.
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
# We must specify the type of the parameter to avoid type errors
def delete_post(id: int, db: Session = Depends(get_db)):
    # Delete the post from the database by id
    deleted_post = db.query(models.Post).filter(models.Post.id == id).delete(synchronize_session=False)
    # If the post is not found, raise a 404 error (before committing)
    if deleted_post == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    # Commit the changes to the database
    db.commit()
    # 204 No Content must return an empty body
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}", response_model=schemas.Post)
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db)):
    # Build the query once so we can reuse it
    post_query = db.query(models.Post).filter(models.Post.id == id)
    # If the post is not found, raise a 404 error (before committing)
    if post_query.first() is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    # Update the post in the database
    post_query.update(post.model_dump(), synchronize_session=False)
    # Commit the changes to the database
    db.commit()
    # Re-fetch and return the updated post (update() returns row count, not the object)
    return post_query.first()


@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Hash the password before storing it
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    # Create a new user
    new_user = models.User(**user.model_dump())
    # Add the new user to the database
    db.add(new_user)
    # Commit the changes to the database
    db.commit()
    # Refresh the new user to get the id
    db.refresh(new_user)
    # Return the new user
    return new_user

@app.get("/users/{id}", response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db),):
    # Get the user from the database by id
    user = db.query(models.User).filter(models.User.id == id).first()
    # If the user is not found, raise a 404 error
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id: {id} does not exist")
    # Return the user
    return user
```

**models.py:**

```python
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from .database import Base


class Post(Base):
    # Define the table name
    __tablename__ = "posts"

    # Define all the fields/columns in the table
    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, server_default='true', nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
```

**schemas.py:**

```python
from pydantic import BaseModel, ConfigDict, EmailStr
from datetime import datetime


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):
    # pass means that the class is empty and will be inherited from the PostBase class
    pass


class Post(PostBase):
    id: int
    created_at: datetime
    # This is used to convert the SQLAlchemy model to a Pydantic model
    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    # This is used to convert the SQLAlchemy model to a Pydantic model
    model_config = ConfigDict(from_attributes=True)
```

**utils.py:**

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(password: str):
    return pwd_context.hash(password)

def verify(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)
```
