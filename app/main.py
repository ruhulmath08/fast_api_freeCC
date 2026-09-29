from fastapi import FastAPI

from . import models
from .database import engine
from .routers import user, post

# Create all database tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Include the routers in the main file
app.include_router(user.router)
app.include_router(post.router)