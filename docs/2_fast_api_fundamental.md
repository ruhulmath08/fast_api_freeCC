# FastAPI fundamental concepts

Here is a quick overview of the FastAPI fundamental concepts

1. Why we need `Schema`
2. How to create a `Schema`
3. Validate the input data
4. Path order: `/posts/latest` before `/posts/{id}`
5. Response with status code
6. FastAPI built in support for documentation
7. Structure the FastAPI project
8. Connect to a database
9. Schema models
10. The `requirements.txt` file

## 1. Why we need `Schema`

- Schema is a way to validate the data that is sent to the API
- It's a pain to get all the data from the request body
- The client can send whatever data they want
- The data isn't getting validated
- We ultimately want to force the client to send the data in a schema that we expect

## 2. How to create a `Schema`

```python
from pydantic import BaseModel


class Post(BaseModel):
    title: str
    content: str
    rating: int
```

This is a simple schema that we can use to validate the data that is sent to the API.

```python
@app.post("/createpost")
def create_postspl(post: Post):
    print(post)
    return {"data": "post created successfully"}
```

This is how we can use the schema to validate the data that is sent to the API.

```json
{
  "title": "A title",
  "content": "A content",
  "rating": 5
}
```

This is the data that we can send to the API.

```python
print(post)
```

This is the data that we will get in the response.

```json
{
  "data": "post created successfully"
}
```

```json
{
  "title": "My first post",
  "content": "Please create my first post",
  "rating": "y"
}
```

This is the data that we can't send to the API. We will get a validation error.

## 3. Validate the input data

FastAPI validates an `int` from the type you declare. Pydantic reads the incoming value and either converts it to an
`int` or rejects the request with **422 Unprocessable Entity**. The route function does not run when validation fails.

`rating` on `Post` is already typed as an int:

```python
class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None
```

`create_post` receives a `Post`, so the JSON body is checked before the function runs.

A JSON number is accepted. Inside the function, `post.rating` is the Python int `5`:

```json
{
  "title": "My first post",
  "content": "Please create my first post",
  "rating": 5
}
```

A non-numeric string is rejected. The handler never runs, and FastAPI returns 422:

```json
{
  "title": "My first post",
  "content": "Please create my first post",
  "rating": "y"
}
```

```json
{
  "detail": [
    {
      "type": "int_parsing",
      "loc": ["body", "rating"],
      "msg": "Input should be a valid integer, unable to parse string as an integer",
      "input": "y"
    }
  ]
}
```

A numeric string such as `"5"` is still accepted. In the default mode, Pydantic turns `"5"` into `5`. To allow only a
real JSON number, type the field as a strict int:

```python
from pydantic import BaseModel, StrictInt


class Post(BaseModel):
    title: str
    content: str
    rating: StrictInt
```

With `StrictInt`, `5` passes and `"5"` fails.

The same rule applies to a path parameter. `id: int` means the URL segment must parse as an integer:

```python
@app.get("/posts/{id}")
def get_post(id: int):
    ...
```

- `GET /posts/1` runs the function with `id == 1`.
- `GET /posts/abc` returns 422 and never calls `find_post`.

`rating: Optional[int] = None` means the field may be omitted or sent as `null`. A required int, written as`rating: int`
with no default, fails with 422 when the client leaves it out.

## 4. Path order: `/posts/latest` before `/posts/{id}`

FastAPI matches routes in the order they are registered. A path parameter such as `{id}` matches any single segment,
including the word `latest`.

Register the fixed path first:

```python
@app.get("/posts/latest")
def get_latest_post():
    post = my_post[len(my_post) - 1]
    return {"Latest Post": post}
```

```python
@app.get("/posts/{id}")
def get_post(id: int):
    ...
```

If `/posts/{id}` is registered first, a request to `/posts/latest` is treated as an id and never reaches
`get_latest_post`.

## 5. Response with status code

We can use the `Response` object to return a response with a status code.

```python
from fastapi import Response


@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    post = find_post(id)
    if not post:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": f"post with id: {id} was not found"}
    return {"post_detail": post}
```

If the post is not found, we set the status code to 404 and return a message.

```json
{
  "message": "post with id: 1 was not found"
}
```

### Using HTTPException

We can use the `HTTPException` class to return a response with a status code.

```python
from fastapi import HTTPException


@app.get("/posts/{id}")
def get_post(id: int):
    post = find_post(id)
    if not post:
        raise HTTPException(status_code=404, detail=f"post with id: {id} was not found")
    return {"post_detail": post}
```

## 6. FastAPI built-in support for documentation

FastAPI automatically generates interactive API documentation from your route definitions and Pydantic schemas.
No extra setup is needed — it is available as soon as the server starts.

### Swagger UI — `/docs`

Visit `http://127.0.0.1:8000/docs` in your browser.

- Lists every route with its method, path, and expected request body.
- Lets you send real requests directly from the browser and see the response.
- Reflects your `Post` schema so the UI shows exactly which fields are required, optional, and what types they accept.

### ReDoc — `/redoc`

Visit `http://127.0.0.1:8000/redoc` for a read-only, three-panel reference view of the same API.

### Why it works automatically

FastAPI reads the type hints on each route function and the Pydantic model fields to build an OpenAPI schema.
Because `Post` is declared as a `BaseModel`, FastAPI knows the shape of the request body and exposes it in both UIs without any extra code.

## 7. Structure the FastAPI project

We can structure the FastAPI project into modules.

```text
app/
├── main.py
├── posts.py
└── users.py
```

Keep your route definitions in `main.py` and import the other modules as needed. For run the application, we can use the following command:

```bash
uvicorn app.main:app --reload
```

This will start the application on `http://127.0.0.1:8000`.

We can also use the following command to run the application in development mode:

```bash
uvicorn app.main:app --reload
```

This will start the application on `http://127.0.0.1:8000` and reload the application when we make changes to the code.

## 8. Connect to a database

- Database is a collection of organized data that can be easily accessed, managed and updated our data.
- We don't work or intract with the database directly, we use a database management system (DBMS) to interact with the database.
- We are using PostgreSQL as our database management system.

Username: postgres
Password: root
Port: 5432
Locale: DEFAULT

### Example code to connect to PostgreSQL

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

## 9. Schema models

- Schema/Pydantic models define the structure of a request and response body.
- This ensure that when a user wants to create a post, the request will only go thrrough if it has a title and a content in the request body.

```python
from pydantic import BaseModel


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    # pass means that the class is empty and will be inherited from the PostBase class
    pass
```

## 10. The `requirements.txt` file

The `requirements.txt` file is a file that contains the dependencies for the project.

```text
fastapi==0.116.1
uvicorn==0.35.0
sqlalchemy==2.0.41
psycopg2-binary==2.9.13
python-jose==3.5.0
python-multipart==0.0.32
passlib==1.7.4
bcrypt==3.2.2
pydantic==2.11.7
pydantic-settings==2.10.1
```

We can install the dependencies by running the following command:

```bash
pip install -r requirements.txt
```

This will install all the dependencies for the project.
