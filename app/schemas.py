from pydantic import BaseModel


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    # pass means that the class is empty and will be inherited from the PostBase class
    pass

class Post(BaseModel):
    title: str
    content: str
    published: bool
    class Config:
        orm_mode = True