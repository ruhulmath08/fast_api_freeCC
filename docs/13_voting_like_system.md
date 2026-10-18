# Voting/Like system

Now we will add a voting/like system to the posts. We will create a new table called `votes` to store the votes for the posts.

## Voting/Likes system requirements

- User should be able to like a post
- Should only be able to like a post once
- Retrieving posts should also fetch the total number of likes

## Vote model

- Column referencing post id
- Column refererencing id of user who liked the post
- A user should only be able to like a post once so this means we need to ensure every post_id/voter_id is a unique combination
- No user can like a post twice

**Table structure**:

| Post_id | User_id |
| ------- | ------- |
| 12      | 4       |
| 28      | 9       |
| 55      | 2       |
| 12      | 9       |
| 18      | 4       |
| 55      | 2       |

The last row is a duplicate of post `55` liked by user `2`, so it must be rejected.

## Composite Keys

A Composite Key is a database key that consists of two or more columns used together to uniquely identify a row in a table. We need to use a composite key to ensure that a user can only like a post once. This is because we need to ensure that every post_id/voter_id is a unique combination.

**Composite key**:

| Post_id | User_id |
| ------- | ------- |
| 12      | 4       |
| 28      | 9       |
| 55      | 2       |
| 12      | 9       |
| 18      | 4       |
| 55      | 2       |

## Composite key SQLAlchemy implementation

```python
class Vote(Base):
    __tablename__ = "votes"
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
```

## Vote Routes

- PAth will be at "/vote"
- The user_id will be extracted from the JWT token
- The body will contain the id of the post. The user is voting on as well as the direction of the vote (0 for unlike, 1 for like)

**Data model**:

```json
{
  "post_id": 12,
  "vote_dir": 0
}
```

## Vote Schema

```python
from pydantic import BaseModel, conint

class Vote(BaseModel):
    post_id: int
    dir: conint(le=1)
```

## When retrieving posts, we should also fetch the total number of likes

```python
from pydantic import BaseModel
from datetime import datetime
from app.schemas import User

class Post(BaseModel):
    id: int
    title: str
    content: str
    published: bool
    created_at: datetime
    owner_id: int
    owner: User
    likes: int
```

## Add PostOut Schema

```python
from pydantic import BaseModel

class PostOut(BaseModel):
    Post: Post
    votes: int
```

## Update Post router to return PostOut

**Get posts:**

```python
@router.get("/", response_model=list[schemas.PostOut])
# limit: int = 10 is the default value for the limit parameter
def get_posts(db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user),
              limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    # Get the posts from the database with the limit
    # posts = (
    #     db.query(models.Post)
    #     .filter(models.Post.title.contains(search))
    #     .limit(limit)
    #     .offset(skip)
    #     .all()
    # )

    posts = db.query(
        models.Post, func.count(models.Vote.post_id).label("votes")).join(
            models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(
                models.Post.id).filter(
                    models.Post.title.contains(search)).group_by(
                        models.Post.id).limit(limit).offset(skip).all()

    return posts
```

**Get post:**

```python
@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, db: Session = Depends(get_db),
             current_user: models.User = Depends(oauth2.get_current_user)):
    # Get the post from the database by id
    # post = db.query(models.Post).filter(models.Post.id == id).first()

    post = db.query(
        models.Post, func.count(models.Vote.post_id).label("votes")).join(
            models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(
                models.Post.id).filter(models.Post.id == id).first()

    # If the post is not found, raise a 404 error
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")

    # Make sure the post belongs to the current user, otherwise raise a 403 error
    # if post.owner_id != current_user.id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    # Return the post
    return post
```
