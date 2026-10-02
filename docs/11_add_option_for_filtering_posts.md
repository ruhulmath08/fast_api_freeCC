# Add option for filtering posts

In this section, we will add an option for filtering posts.

1. Add limit when get posts
2. Add skip when get posts
3. Add search functionality when get posts

## 1. Add limit when get posts

Add a limit parameter to the get posts endpoint.

```python
@router.get("/", response_model=list[schemas.Post])
# limit: int = 10 is the default value for the limit parameter
def get_posts(db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user),
              limit: int = 10):
    # Get the posts from the database with the limit
    posts = db.query(models.Post).limit(limit).all()
    return posts
```

Now we can pass the limit parameter to the get posts endpoint.

```http
GET http://127.0.0.1:8000/posts?limit=10
```

> Note: `limit`: the number of posts to return

---

## 2. Add skip when get posts

Add a skip parameter to the get posts endpoint. This is used to skip the first n records in the database.

```python
@router.get("/", response_model=list[schemas.Post])
# limit: int = 10 is the default value for the limit parameter
def get_posts(db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user),
              limit: int = 10, skip: int = 0):
    # Get the posts from the database with the limit
    posts = db.query(models.Post).limit(limit).offset(skip).all()
    return posts
```

**Example:**

```http
GET http://127.0.0.1:8000/posts?limit=2&skip=10
```

> Note: `skip`: the number of posts to skip

This will return the next 2 posts after skipping the first 10 posts.

---

## 3. Add search functionality when get posts

Add a search parameter to the get posts endpoint. This is used to search the posts by the title. We will use the `like`
operator to search the posts.

**Example:**

```python
@router.get("/", response_model=list[schemas.Post])
# limit: int = 10 is the default value for the limit parameter
def get_posts(db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user),
              limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    # Get the posts from the database with the limit
    posts = (
        db.query(models.Post)
        .filter(models.Post.title.contains(search))
        .limit(limit)
        .offset(skip)
        .all()
    )
    return posts
```

**URL:**

```http
GET http://127.0.0.1:8000/posts?limit=2&skip=2&search=This
```

**Response:**

```json
[
  {
    "title": "This ost is from FFF",
    "content": "Hello I am FFF, this is my first post",
    "published": false,
    "id": 13,
    "created_at": "2026-10-02T12:23:00.384281+06:00",
    "owner_id": 22,
    "owner": {
      "id": 22,
      "email": "fff@gmail.com",
      "created_at": "2026-09-30T19:26:51.689696+06:00"
    }
  },
  {
    "title": "This ost is from FFF",
    "content": "Hello I am FFF, this is my second post",
    "published": false,
    "id": 14,
    "created_at": "2026-10-02T12:23:07.173164+06:00",
    "owner_id": 22,
    "owner": {
      "id": 22,
      "email": "fff@gmail.com",
      "created_at": "2026-09-30T19:26:51.689696+06:00"
    }
  }
]
```

This will return the posts with the title containing "This" in the first 2 posts after skipping the first 2 posts.
