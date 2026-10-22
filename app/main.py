from fastapi import FastAPI

from . import models
from .database import engine
from .routers import user, post, auth, vote
from fastapi.middleware.cors import CORSMiddleware

# Create all database tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = ["*"] # Allow all origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Allow all origins
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods
    allow_headers=["*"], # Allow all headers
)

# Include the routers in the main file
app.include_router(user.router)
app.include_router(post.router)
app.include_router(auth.router)
app.include_router(vote.router)