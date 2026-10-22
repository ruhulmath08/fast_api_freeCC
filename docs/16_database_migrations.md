# Database migrations

SQLAlchemy models describe the schema you *want*, but they do not change an existing database for you (see [Limitation of SQLAlchemy](15_limitation_of_sqlalchemy.md)). **Alembic** versions those changes so every environment (local, staging, production) can apply the same history safely.

1. [What is a database migration?](#1-what-is-a-database-migration)
2. [Why do we need migrations?](#2-why-do-we-need-migrations)
3. [Install and initialize Alembic](#3-install-and-initialize-alembic)
4. [Configure Alembic for this project](#4-configure-alembic-for-this-project)
5. [Stop using](#5-stop-using-create_all) `create_all`
6. [Create and apply a migration](#6-create-and-apply-a-migration)
7. [Add a column with a new migration](#7-add-a-column-with-a-new-migration)
8. [Useful Alembic commands](#8-useful-alembic-commands)
9. [Upgrade and downgrade](#9-upgrade-and-downgrade)
10. [Best practices](#10-best-practices)
11. [Key takeaways](#11-key-takeaways)
12. [References](#references)

---

## 1. What is a database migration?

A migration is a versioned script that changes the database schema (or data) in a controlled way.

**Version 1** — `posts` has `id` and `title`:

| id  | title        |
| --- | ------------ |
| 1   | first post   |

**Version 2** — you add `content`:

```sql
ALTER TABLE posts
ADD COLUMN content VARCHAR NOT NULL;
```

Alembic stores that change as a Python file under `alembic/versions/` and records the applied revision in the `alembic_version` table so it knows what to run next.

---

## 2. Why do we need migrations?

| Problem | Without migrations | With migrations |
| --- | --- | --- |
| Schema drift | Each developer edits the DB by hand | Same ordered scripts everywhere |
| Deployments | Easy to forget a column in production | Run `alembic upgrade head` in CI/CD |
| History | No record of how the schema evolved | Git + `alembic/versions/` |
| Rollbacks | Guess and fix manually | `downgrade` (with care — data can be lost) |

> **[IMPORTANT]**: In production, run migrations as a controlled deploy step — not from every app instance on startup. Multiple instances must not race to alter the schema.

---

## 3. Install and initialize Alembic

This project already uses `psycopg2` (see [Connect PostgreSQL](4_connect_postgreSQL.md) and `requirements.txt`). Install Alembic:

```bash
pip install alembic
```

Check it works:

```bash
alembic --version
alembic --help
```

Initialize from the project root:

```bash
alembic init alembic
```

That creates:

```plaintext
fast_api_freeCC/
├── alembic/
│   ├── versions/          # migration scripts live here
│   ├── env.py             # connects Alembic to your models + DB
│   └── script.py.mako
├── alembic.ini
└── app/
    ├── models.py
    ├── database.py
    └── config.py
```

> **[NOTE]**: Use `alembic init alembic` so the folder name matches this repo (`script_location = alembic` in `alembic.ini`). Do not use a different folder name unless you update `alembic.ini` to match.

---

## 4. Configure Alembic for this project

Alembic must know (1) your SQLAlchemy metadata and (2) the database URL from settings.

Update `alembic/env.py`:

```python
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from app.models import Base
from app.config import settings

config = context.config
config.set_main_option(
    "sqlalchemy.url",
    (
        f"postgresql+psycopg2://{settings.database_username}:"
        f"{settings.database_password}@{settings.database_hostname}"
        f":{settings.database_port}/{settings.database_name}"
    ),
)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
```

Keep the existing `run_migrations_offline` / `run_migrations_online` helpers; they use `target_metadata` and `sqlalchemy.url`.

- Import `Base` from `app.models` so autogenerate can see `Post`, `User`, and `Vote`.
- Build the URL from `settings` — never commit real passwords in `alembic.ini`.

---

## 5. Stop using `create_all`

Earlier lessons used:

```python
models.Base.metadata.create_all(bind=engine)
```

in `app/main.py`. That creates tables from models on every startup and **fights Alembic**:

- Alembic thinks a column is missing and generates `add_column`.
- The column already exists → `DuplicateColumn` errors.
- Or Alembic creates a table that `create_all` already created.

Once you adopt Alembic, remove (or comment out) `create_all` and let migrations own the schema.

---

## 6. Create and apply a migration

### Generate an empty revision

```bash
alembic revision -m "create post table"
```

This only creates a file under `alembic/versions/`. It does **not** change the database. Revision IDs are generated (for example `cc21d1967b67`) — yours will differ.

### Fill in `upgrade` / `downgrade`

Example for creating `posts` with `id` and `title`:

```python
def upgrade() -> None:
    op.create_table(
        "posts",
        sa.Column("id", sa.Integer, nullable=False, autoincrement=True, primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("posts")
```

`down_revision = None` means this is the first migration in the chain.

### Apply it

```bash
alembic upgrade head
```

That applies every pending revision up to the latest. To target one revision by id:

```bash
alembic upgrade cc21d1967b67
```

> **[WARNING]**: The correct command is `alembic upgrade <revision>`, **not** `alembic upgrade revision <revision>`.

You can also use autogenerate after models and the DB are in sync with Alembic:

```bash
alembic revision --autogenerate -m "create post table"
```

> **[IMPORTANT]**: Always review autogenerated scripts before applying. Autogenerate is a starting point, not a guarantee.

---

## 7. Add a column with a new migration

Once the `posts` table exists, new columns are added with a **new** Alembic revision — not by editing an already-applied migration. Alembic keeps a linear chain: each file’s `down_revision` points at the previous one.

> **[IMPORTANT]**: Only migrate columns that are **not** already created in an earlier revision. The create-table migration already includes `title`. A second migration that runs `op.add_column(..., "title")` fails with:
>
> `DuplicateColumn: column "title" of relation "posts" already exists`

### Step 1 — Update the SQLAlchemy model

In `app/models.py`, add the field you want on `Post` (if it is not there yet):

```python
content = Column(String, nullable=False)
```

### Step 2 — Create a new Alembic revision

**Option A — empty revision (manual):**

```bash
alembic revision -m "add content in post table"
```

**Option B — autogenerate** (Alembic compares `Base.metadata` to the live DB):

```bash
alembic revision --autogenerate -m "add content in post table"
```

Both create a new file under `alembic/versions/`. Autogenerate fills in `op.add_column` for you when it detects the model/DB difference — still **review** the file before applying.

### Step 3 — Fill in (or review) the migration

Alembic wires the chain via revision ids. Example (ids will differ on your machine):

```python
"""add content in post table

Revision ID: ff1011da82d9
Revises: cc21d1967b67
Create Date: 2026-10-22 00:41:57.080552

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "ff1011da82d9"
down_revision: Union[str, Sequence[str], None] = "cc21d1967b67"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("posts", sa.Column("content", sa.String(), nullable=False))


def downgrade() -> None:
    op.drop_column("posts", "content")
```

| Field | Meaning |
| --- | --- |
| `revision` | This migration’s id |
| `down_revision` | Parent revision (here: create post table) — Alembic sets this when you run `revision` |
| `upgrade()` | SQL applied by `alembic upgrade` |
| `downgrade()` | SQL applied by `alembic downgrade` |

Confirm the parent with:

```bash
alembic current
alembic history
```

### Step 4 — Apply the migration

```bash
alembic upgrade head
```

Alembic runs every pending revision from the DB’s current revision up to the latest head (for example `cc21d1967b67` → `ff1011da82d9`).

### Step 5 — Verify

```bash
alembic current
```

You should see the new revision marked `(head)`. Optionally:

```bash
alembic heads
```

`current` = what the **database** has applied. `heads` = tip of the **migration files**. When they match, the DB is fully upgraded.

---

## 8. Useful Alembic commands

| Command | What it does |
| --- | --- |
| `alembic current` | Revision currently applied to **this** database |
| `alembic heads` | Latest revision(s) in the **migration files** (does not change the DB) |
| `alembic history` | Full chain of revisions |
| `alembic upgrade head` | Apply all pending upgrades |
| `alembic downgrade -1` | Roll back one revision |
| `alembic downgrade <revision>` | Roll back to a specific revision (runs each `downgrade()` along the way) |
| `alembic stamp <revision>` | Mark the DB as being at a revision **without** running SQL (advanced / recovery) |

If `current` and `heads` disagree, you still have pending migrations (or a branch that needs merging).

---

## 9. Upgrade and downgrade

Every migration defines two directions:

```python
def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("phone_number", sa.String(20), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "phone_number")
```

| Direction | Typical use |
| --- | --- |
| `upgrade` | Deploy forward |
| `downgrade` | Local undo / careful rollback |

### Downgrade one step

```bash
alembic downgrade -1 # Back to one step earlier
```

If the DB is at `ff1011da82d9` (add content), this runs that migration’s `downgrade()` — for example `op.drop_column("posts", "content")` — and leaves you at `cc21d1967b67`.

### Downgrade to a specific revision

To go back to the create-post-table revision explicitly:

```bash
alembic downgrade cc21d1967b67
```

Alembic walks the chain backward until the database is at `cc21d1967b67`. Any revisions after that (such as add content) are undone via their `downgrade()` functions.

Verify:

```bash
alembic current
```

You should see `cc21d1967b67`. To move forward again:

```bash
alembic upgrade head
```

> **[WARNING]**: Downgrade is not a backup. Dropping a column permanently deletes that data. Prefer backups plus a tested restore plan for production.

---

## 10. Best practices

1. **Keep migrations in Git** and review them with the model changes.
2. **One logical change per migration** when learning; keep scripts easy to read.
3. **Never casually edit a migration that already ran** in shared or production DBs — add a new migration instead.
4. **Do not put the same column in two migrations** (create + add again).
5. **Prefer additive changes** in production (add column → migrate data → switch app → drop old column later).
6. **Run migrations once per deploy**, not on every app worker start.
7. **Test upgrade (and downgrade, if you rely on it)** against a DB that already has data.
8. **Protect credentials** via `.env` / settings — same pattern as [configuration settings](12_add_configuration_settings.md).

---

## 11. Key takeaways

1. Migrations version database changes the same way Git versions code.
2. Alembic is the standard companion to SQLAlchemy in FastAPI projects.
3. Configure `alembic/env.py` with `Base.metadata` and your settings-based DB URL.
4. Remove `create_all` once Alembic owns the schema.
5. `alembic revision` writes a file; `alembic upgrade head` applies it.
6. `alembic current` = DB state; `alembic heads` = file tip(s).
7. Migrations do not replace backups.

---

## References

- [Alembic](https://alembic.sqlalchemy.org/)
