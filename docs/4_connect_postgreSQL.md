# Connect to PostgreSQL

1. Install psycopg2-binary
2. Connect to PostgreSQL
3. The full code

## 1. Install psycopg2-binary

```bash
pip install psycopg2-binary
```

For more information, see [psycopg2-binary](https://pypi.org/project/psycopg2/).

## 2. Connect to PostgreSQL

```python
import psycopg2
from psycopg2.extras import RealDictCursor
import time

while True:
    try:
        conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='root', port=5432,
                                cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successful!")
        break
    except Exception as error:
        print("Connecting to database failed")
        print(f"Error: {error}")
        # sleep for 2 seconds and try again
        time.sleep(2)
```

## 3. The full code

```python
from typing import Optional
from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


while True:
    try:
        conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='root', port=5432,
                                cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successful!")
        break
    except Exception as error:
        print("Connecting to database failed")
        print(f"Error: {error}")
        # sleep for 2 seconds and try again
        time.sleep(2)


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


@app.get("/posts")
def get_posts():
    # Get all posts from the database
    cursor.execute("SELECT * FROM posts")
    # Fetch all posts from the database
    posts = cursor.fetchall()
    # Return the posts
    return {"data": posts}


# 201 Created: this request created a new post.
@app.post("/createpost", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    # Insert the post into the database
    cursor.execute("INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * ",
                   (post.title, post.content, post.published))
    # Fetch the post from the database
    new_post = cursor.fetchone()
    # Commit the changes to the database
    conn.commit()
    return {"message": "post created successfully", "data": new_post}


# Register this before /posts/{id}, or FastAPI treats "latest" as an id.
@app.get("/posts/latest")
def get_latest_post():
    # Get the latest post from the database
    cursor.execute("SELECT * FROM posts ORDER BY id DESC LIMIT 1")
    # Fetch the post from the database
    post = cursor.fetchone()
    # If no posts exist, raise a 404 error
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No posts found")
    return {"Latest Post": post}


@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    # Get the post from the database
    cursor.execute("SELECT * FROM posts WHERE id = %s", (str(id),))
    # Fetch the post from the database
    post = cursor.fetchone()
    # If the post is not found, raise a 404 error
    if post is None:
        raise HTTPException(status_code=404, detail=f"post with id: {id} was not found")
    # Return the post
    return {"post_detail": post}


# 204 No Content: this request deleted a post.
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):  # We must specify the type of the parameter
    # Delete the post from the database
    cursor.execute("DELETE FROM posts WHERE id = %s RETURNING *", (str(id),))
    # Fetch the deleted post from the database
    deleted_post = cursor.fetchone()
    # If the post is not found, raise a 404 error (before committing)
    if deleted_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    # Commit the changes to the database only after confirming deletion
    conn.commit()
    # 204 No Content must return an empty body
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    # Update the post in the database
    cursor.execute("UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *",
                   (post.title, post.content, post.published, str(id)))
    # Fetch the updated post from the database
    updated_post = cursor.fetchone()
    # If the post is not found, raise a 404 error
    if updated_post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    # Commit the changes to the database
    conn.commit()
    # Return the updated post
    return {"message": "post updated successfully", "data": updated_post}
```
