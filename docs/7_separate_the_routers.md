# Separate the routers

In this tutorial we will separate the routers into different files.

1. Project structure

2. Separate the routers into different files

3. Group the swagger documentation for the routers

## 1. Project structure

The project structure is:

```text
├── app/
│   ├── routers/            # Routers directory
│   │   ├── posts.py        # Router for the posts
│   │   ├── users.py        # Router for the users
│   │   └── __init__.py     # Initialization file of the routers directory
│   │   
│   ├── __init__.py         # Initialization file of the application
│   ├── main.py             # Main file of the application
│   ├── models.py           # Database models file
│   ├── schemas.py          # Schemas file
│   └── utils.py            # Utilities functions file
```

## 2. Separate the routers into different files

We will create a new file for each router.

**post.py:**

```python
from fastapi import Depends, HTTPException, Response, status, APIRouter 
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(
    # The prefix is the common path for the router: /posts
    prefix="/posts",
    # The tags is the group of the router: Posts
    tags=["Posts"]
)


@router.get("/", response_model=list[schemas.Post])
def get_posts(db: Session = Depends(get_db)):
    # Get all posts from the database
    posts = db.query(models.Post).all()
    # Return the posts
    return posts


# 201 Created: this request created a new post.
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
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
@router.get("/latest", response_model=schemas.Post)
def get_latest_post(db: Session = Depends(get_db)):
    # Get the latest post from the database
    latest_post = db.query(models.Post).order_by(models.Post.id.desc()).first()
    # If no posts exist, raise a 404 error
    if latest_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No posts found")
    # Return the latest post
    return latest_post


@router.get("/{id}", response_model=schemas.Post)
def get_post(id: int, db: Session = Depends(get_db)):
    # Get the post from the database by id
    post = db.query(models.Post).filter(models.Post.id == id).first()
    # If the post is not found, raise a 404 error
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    # Return the post
    return post


# 204 No Content: this request deleted a post.
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
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


@router.put("/{id}", response_model=schemas.Post)
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

**user.py:**

```python
from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session
from .. import models, schemas, utils
from ..database import get_db

router = APIRouter(
    # The prefix is the common path for the router: /users
    prefix="/users",
    # The tags is the group of the router: Users
    tags=["Users"]
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
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

@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db),):
    # Get the user from the database by id
    user = db.query(models.User).filter(models.User.id == id).first()
    # If the user is not found, raise a 404 error
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id: {id} does not exist")
    # Return the user
    return user
```

**main.py:**

```python
from fastapi import FastAPI

from .routers import user, post

app = FastAPI()

# Include the routers in the main file
app.include_router(user.router)
app.include_router(post.router)
```

## 3. Group the swagger documentation for the routers

For grouping the swagger documentation for the routers, we will use the `tags` parameter in the router.

```python
# Router for the posts
router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)

# Router for the users
router = APIRouter(
    prefix="/users",
    tags=["users"]
)
```
