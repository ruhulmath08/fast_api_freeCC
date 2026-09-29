from fastapi import FastAPI

from .routers import user, post

app = FastAPI()

# Include the routers in the main file
app.include_router(user.router)
app.include_router(post.router)