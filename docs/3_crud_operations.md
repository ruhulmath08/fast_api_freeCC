# FastAPI CRUD Operations

1. Create a post
2. Read a post
3. Update a post
4. Delete a post
5. The full code

## 1. Create a post

We can use the `POST` method to create a post. We must specify the type of the parameter and return the created post.

```python
# 201 Created: this request created a new post.
@app.post("/createpost", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    # Convert the post object to a dictionary.
    post_dict = post.model_dump()
    # Generate a random id for the post.
    post_dict["id"] = randrange(0, 1000000)
    # Add the post to the list of posts.
    my_post.append(post_dict)
    # Return the response.
    return {"message": "post created successfully", "data": post_dict}
```

## 2. Read a post

FastAPI matches routes in the order they are registered. A path parameter such as `{id}` matches any single segment,
including the word `latest`.

Register the fixed path first:

## Get all posts

```python
@app.get("/posts")
def get_posts():
    return {"data": my_post}
```

## Get latest posts

```python
# Register this before /posts/{id}, or FastAPI treats "latest" as an id.
@app.get("/posts/latest")
def get_latest_post():
    post = my_post[len(my_post) - 1]
    return {"Latest Post": post}
```

## Get post by ID

```python
@app.get("/getpost/{id}")
def get_post(id: int):
    return {"message": "post read successfully", "data": my_post[id]}
```

## Get posts by ID

```python
@app.get("/posts/{id}")
# We can also use the Response object to return a response with a status code and a message
def get_post(id: int, response: Response):
    # Find the post index from the list of postes
    index = find_index_post(id)
    # If index not found, display status code 404 and message
    if index is None:
        # If index not found, display status code 404 and message
        raise HTTPException(status_code=404, detail=f"post with id: {id} was not found")
    # If index found, return the post detail
    return {"post_detail": my_post[index]}
```

If `/posts/{id}` is registered first, a request to `/posts/latest` is treated as an id and never reaches
`get_latest_post`.

## 3. Update a post

We can use the `PUT` method to update a post. We must specify the type of the parameter and return the updated post.

```python
@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    # Find the post index from the list of posts
    index = find_index_post(id)
    # If index not found, display status code 404 and message
    if index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    # Convert the Post model into a dictionary
    post_dict = post.model_dump()
    # Assign the provided post ID to the post
    post_dict["id"] = id
    # Based on the index update the post in the list
    my_post[index] = post_dict
    return {"message": "post updated successfully", "data": post_dict}
```

## 4. Delete a post

We can use the `DELETE` method to delete a post. We must specify the type of the parameter and return a 204 status code.

```python
# 204 No Content: this request deleted a post.
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):  # id must be typed so FastAPI validates it as an integer
    # Find the post index from the list of posts
    index = find_index_post(id)
    # If index not found, raise a 404 error
    if index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    # Remove the post at the found index
    my_post.pop(index)
    # Return an empty 204 No Content response
    return Response(status_code=status.HTTP_204_NO_CONTENT)
```

## 5. The full code

```python
from typing import Optional
from fastapi import Body, FastAPI, HTTPException, Response, status
from pydantic import BaseModel
from random import randrange

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


my_post = [{"id": 1, "title": "title of post 1", "content": "content of post 1", "published": True, "rating": 5},
           {"id": 2, "title": "title of post 2", "content": "content of post 2", "published": False, "rating": 3}]


def find_index_post(id):
    for i, p in enumerate(my_post):
        if p["id"] == id:
            return i
    return None


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}


@app.get("/posts")
def get_posts():
    return {"data": my_post}


# 201 Created: this request created a new post.
@app.post("/createpost", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    post_dict = post.model_dump()
    post_dict["id"] = randrange(0, 1000000)
    my_post.append(post_dict)
    return {"message": "post created successfully", "data": post_dict}


# Register this before /posts/{id}, or FastAPI treats "latest" as an id.
@app.get("/posts/latest")
def get_latest_post():
    post = my_post[len(my_post) - 1]
    return {"Latest Post": post}


@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    index = find_index_post(id)
    if index is None:
        raise HTTPException(status_code=404, detail=f"post with id: {id} was not found")
    return {"post_detail": my_post[index]}


# 204 No Content: this request deleted a post.
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):  # We must specify the type of the parameter
    index = find_index_post(id)
    if index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    my_post.pop(index)
    # We don't need to return anything, so we return a 204 status code
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    index = find_index_post(id)
    if index is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    post_dict = post.model_dump()
    post_dict["id"] = id
    my_post[index] = post_dict
    return {"message": "post updated successfully", "data": post_dict}
```
