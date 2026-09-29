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
