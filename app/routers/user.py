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