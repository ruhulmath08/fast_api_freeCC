# Crud operations using ORM (Object Relational Mapping)

1. What is ORM?
2. Using SQLAlchemy
3. Connecting to the database
4. Defining the tables as Python models
5. Define the schemas
6. The project structure
7. The API endpoints

ORM is a technique that allows us to interact with the database using objects.

- Layer of abstraction that sets a bridge between the database and the code
- We can perform database operations using Python code instead of writing raw SQL queries
- We can use the ORM to create, read, update and delete data from the database
- ORM is not a library, it is a technique and it is database independent
- Instade of manually defining the tables in postgres, we can define our tables as Python models
- Queries can be made exclusively through Python code. No SQL is necessary.

## 2. Using SQLAlchemy

- SQLAlchemy is one of the most popular ORMs for Python
- It is a standalone library and has no association with FastAPI. It can be used with any other Python web frameworks or
  any Python based applications.
- Link to the SQLAlchemy documentation: [SQLAlchemy](https://www.sqlalchemy.org/)

**Install SQLAlchemy:**

```bash
pip install sqlalchemy
```

## 3. Connecting to the database

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 'postgresql://<username>:<password>@<host>:<port>/<database_name>'
# We are using the PostgreSQL database
SQLALCHEMY_DATABASE_URL = 'postgresql+psycopg2://postgres:root@localhost:5432/fastapi'

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

## 4. Defining the tables as Python models

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

```

## 5. Define the schemas

```python
from pydantic import BaseModel, ConfigDict
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
```

- **Schemas are used to validate the data that is sent to the API.**
- **Schemas are also used to define the response models.**
- **`PostBase`** holds the shared fields (`title`, `content`, `published`).
- **`PostCreate`** extends `PostBase` — used for incoming request bodies (no `id` or `created_at` yet).
- **`Post`** extends `PostBase` — used for responses; includes `id` and `created_at` from the database.
- **`model_config = ConfigDict(from_attributes=True)`** is the Pydantic V2 replacement for the
  deprecated `class Config: orm_mode = True`. It allows Pydantic to read data directly from
  SQLAlchemy ORM objects instead of only from plain dicts.

## 6. The project structure

```text
app/
    __init__.py  # This is used to make the app directory a Python package.
    database.py  # Used to connect to the database.
    models.py    # Used to define the tables as Python models and create the tables in the database.
    schemas.py   # Used to define the schemas for the API.
    main.py      # Used to define the API endpoints and the logic for the API.
```

- **app/ is the main directory for the project.**

- **database.py is used to connect to the database.**
- **models.py is used to define the tables as Python models.**
- **schemas.py is used to define the schemas.**
- **main.py is used to define the API endpoints.**

## 7. The API endpoints

`response_model` tells FastAPI which Pydantic schema to use when serialising the response. FastAPI
will filter out any fields not declared in that schema and validate the output automatically.

```python
from fastapi import Depends, FastAPI, HTTPException, Response, status
from sqlalchemy.orm import Session

from . import models, schemas
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
    # Refresh the new post to get the id and created_at from the database
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
```

### Key points about `update_post`

- `db.query(...).update(...)` returns the **number of rows affected** (an `int`), not the updated
  ORM object. Returning that integer directly causes a `ResponseValidationError` because FastAPI
  tries to serialise it as a `Post`.
- The fix is to store the query in `post_query`, check existence first, run the update, commit,
  then call `post_query.first()` again to re-fetch the now-updated row from the database.
