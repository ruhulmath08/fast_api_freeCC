from fastapi import Depends, HTTPException, Response, status, APIRouter
from sqlalchemy.orm import Session

from app import models, schemas, oauth2
from app.database import get_db

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


@router.get("/", response_model=list[schemas.Post])
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # Get all posts from the database
    posts = db.query(models.Post).all()
    # Return the posts
    return posts


# 201 Created: this request created a new post.
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
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
def get_latest_post(db: Session = Depends(get_db),
                    current_user: int = Depends(oauth2.get_current_user)):
    # Get the latest post from the database
    latest_post = db.query(models.Post).order_by(models.Post.id.desc()).first()
    # If no posts exist, raise a 404 error
    if latest_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No posts found")
    # Return the latest post
    return latest_post


@router.get("/{id}", response_model=schemas.Post)
def get_post(id: int, db: Session = Depends(get_db),
             current_user: int = Depends(oauth2.get_current_user)):
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
def delete_post(id: int, db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
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
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
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
