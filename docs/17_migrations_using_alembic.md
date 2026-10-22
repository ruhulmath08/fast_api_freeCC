# Migrations using alembic

Alembic is a database migration tool for SQLAlchemy. It is used to manage the database schema changes.

1. [Install Alembic](#1-install-alembic)
2. [Init Alembic](#2-init-alembic)
3. [Update the `env.py` file inside the `alembic` directory](#3-update-the-envpy-file-inside-the-alembic-directory)
4. [Create a new migration](#4-create-a-new-migration)
5. [Apply the migration to the database](#5-apply-the-migration-to-the-database)
6. [Add a new revision](#6-add-a-new-revision)
7. [Implement the`users` functionality](#7-implement-the-users-functionality)
8. [Implement the relationships using migrations](#8-implement-the-relationships-using-migrations)
9. [Add last few columns to `post` table](#9-add-last-few-columns-to-post-table)
10. [Downgrade to `add users table` revision](#10-downgrade-to-add-users-table-revision)
11. [Generate the `vore` table with autogenerate](#11-generate-the-votes-table-with-autogenerate)
12. [Add `phone_number` column to `users` table](#12-add-phone_number-column-to-users-table)

## 1. Install Alembic

First we need to install `alembic` in our project. We can do this by running the following command:

```bash
pip install alembic
```

This command will install `alembic` in our project. Now we can run the `alembic` specific command:

```bash
alembic --version # Show the version of `alembic` installed in our project.
alembic --help # Show the help for `alembic` commands.
```

This will show the version of `alembic` installed in our project.

---

## 2. Init Alembic

First we need to init `alembic` in our project. We can do this by running the following command:

```bash
alembic init --help # Show the help for `alembic init` command. This is optional just to see the help for the command.
alembic init alembic # Init `alembic` in our project.
```

This will create a new directory called `alembic` and a file called `alembic.ini` in our project root directory.

```plaintext
alembic/
├── env.py
├── script.py.mako
├── README.md
└── versions/
    ├── <revision_number>_<description>.py
    └── <revision_number>_<description>.py
```

- `alembic.ini` is the configuration file for `alembic`.
- `alembic/` is the directory for the `alembic` files. It contains the `env.py` file, the `script.py.mako` file, the `README.md` file and the `versions/` directory.
- `versions/` is the directory for the migration files. It contains the migration files.

---

## 3. Update the `env.py` file inside the `alembic` directory

We need to update the `env.py` file inside the `alembic` directory to configure the database connection.

```python
# env.py
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from app.database import Base
from app.config import settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
# Override the `sqlalchemy.url` in the `config` object with the database connection URL.
config.set_main_option(
    "sqlalchemy.url",
    (
        f"postgresql+psycopg2://{settings.database_username}:"
        f"{settings.database_password}@{settings.database_hostname}"
        f":{settings.database_port}/{settings.database_name}"
    ),
)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

This will configure the database connection to the database.

---

## 4. Create a new migration

We can create a new migration by running the following command:

```bash
alembic revision --help # Show the help for `alembic revision` command. This is optional just to see the help for the command.
alembic revision -m "create post table" # Create a new migration.
```

This will create a new migration file in the `versions/` directory.

```plaintext
alembic/
├── env.py
├── script.py.mako
├── README.md
└── versions/
    ├── be88c17d1e9b_create_post_table.py
```

Now we need to update the migration file to create the `post` table.

```python
# be88c17d1e9b_create_post_table.py
"""create post table

Revision ID: be88c17d1e9b
Revises:
Create Date: 2026-10-22 02:59:18.038688

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'be88c17d1e9b'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'post',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('title', sa.String(), nullable=False),
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('post')
    pass

```

This will create the `post` table in the database. Now we need to run the `alembic upgrade <revision_number>` command to apply the migration to the database.

---

## 5. Apply the migration to the database

We need to apply the migration to the database by running the following command:

```bash
alembic upgrade be88c17d1e9b # Apply the migration to the database.
```

This will apply the migration to the database. Now we can check the database to see if the `post` table has been created.

---

## 6. Add a new revision

Revisions are the individual changes to the database schema. We can add a new revision by running the following command:

1. Create a new migration file.
2. Update the migration file to add the new column.
3. Apply the migration to the database.
4. Rollback or undo the migration/changes.

### 6.1 Create a new migration file

```bash
alembic revision --help # Show the help for `alembic revision` command. This is optional just to see the help for the command.
alembic revision -m "add content column to post table" # Create a new migration.
```

This will create a new migration file in the `versions/` directory.

```plaintext
alembic/
├── env.py
├── script.py.mako
├── README.md
└── versions/
    ├── be88c17d1e9b_create_post_table.py
    ├── 86f420f80cb7_add_content_column_to_post_table.py
```

Now we need to update the migration file to add the `content` column to the `post` table.

### 6.2 Update the migration file to add the new column

We need to update the migration file to add the `content` column to the `post` table.

```python
# 86f420f80cb7_add_content_column_to_post_table.py
"""add content column to post table

Revision ID: 86f420f80cb7
Revises: be88c17d1e9b
Create Date: 2026-10-22 03:17:26.822912

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '86f420f80cb7'
down_revision: Union[str, Sequence[str], None] = 'be88c17d1e9b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('post', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('post', 'content')
    pass
```

This will add the `content` column to the `post` table in the database. Now we need to run the `alembic upgrade <revision_number>` command to apply the migration to the database.

### 6.3 Apply the migration to the database

We need to apply the migration to the database by running the following command:

```bash
alembic current # Show which migration revision is applied to this database.
alembic heads  # Show the latest revision(s) in the migration files.
alembic upgrade 86f420f80cb7 # Apply the migration to the database.
alembic upgrade head # Same as alembic upgrade <revision_number>.
```

This will apply the migration to the database. Now we can check the database to see if the `content` column has been added to the `post` table.

### 6.4 Rollback or undo the migration/changes

We can rollback or undo the migration/changes by running the following command:

```bash
alembic downgrade <down_revision_number> # This down_revision is found in the migration file.
alembic downgrade be88c17d1e9b # Rollback the migration to the specific revision.
```

We can also run the following command to rollback the migration to the latest revision:

```bash
alembic downgrade head # Rollback the migration to the latest revision.
alembic downgrade -1 # Rollback the migration to the previous revision.
```

This will rollback or undo the migration/changes. Now we can check the database to see if the `content` column has been removed from the `post` table.

---

## 7. Implement the `users` functionality

We need to implement the `users` functionality by adding the `users` table to the database. We can do this by doing the following steps:

1. Create a new migration file.
2. Update the migration file to add the `users` table.
3. Apply the migration to the database.
4. Rollback or undo the migration/changes.

### 7.1 Create a new migration file

```bash
alembic revision -m "add users table" # Create a new migration with the name "add users table".
```

This will create a new migration file in the `versions/` directory.

```plaintext
alembic/
├── env.py
├── script.py.mako
├── README.md
└── versions/
    ├── be88c17d1e9b_create_post_table.py
    ├── 86f420f80cb7_add_content_column_to_post_table.py
    ├── 7f4b90107b7d_add_users_table.py
```

### 7.2 Update the migration file to add the `users` table

We need to update the migration file `7f4b90107b7d_add_users_table.py` to add the `
users` table.

```python
# 7f4b90107b7d_add_users_table.py

"""add users table

Revision ID: 7f4b90107b7d
Revises: 86f420f80cb7
Create Date: 2026-10-22 15:55:42.082786

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text

# revision identifiers, used by Alembic.
revision: str = '7f4b90107b7d'
down_revision: Union[str, Sequence[str], None] = '86f420f80cb7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False,),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('users')
    pass

```

This will add the `users` table to the database. Now we need to run the `alembic upgrade <revision_number>` command to apply the migration to the database.

### 7.3 Apply the migration to the database

We need to apply the migration to the database by running the following command:

**Note:** We can use the `alembic current` command to show which migration revision is applied to this database. We can use the `alembic history` command to show the history of migrations.

```bash
alembic current # Show which migration revision is applied to this database. -> be88c17d1e9b
alembic history # Show the history of migrations.
alembic heads # Show the latest revision(s) in the migration files. -> 7f4b90107b7d
```

Now, we are currently at the `7f4b90107b7d` revision. We can apply the migration to the database by running the following command:

```bash
alembic upgrade head # Apply the migration to the database.
```

This will apply the migration to the database. Now we can check the database to see if the `users` table has been created. The `head` command will apply the migration to the database to the latest revision.

The `users` table has been created in the database with the following columns:

| id  | email | password | created_at |
| --- | ----- | -------- | ---------- |

Also the constraints have been applied to the `users` table. The `email` column is unique and the `created_at` column is a timestamp with timezone.

## 8. Implement the relationships using migrations

We need to implement the relationships between the `users` and `posts` tables by adding the `owner_id` column to the `posts` table. We can do this by doing the following steps:

1. Add foreign key constraint to the `posts` table.
2. Add the `owner_id` column to the `posts` table.
3. Apply the migration to the database.

### 8.1 Add foreign key constraint to the `posts` table

```bash
alembic revision -m "add foreign key constraint to posts table" # Create a new migration with the name "add foreign key constraint to posts table".
```

This will create a new migration file in the `versions/` directory.

```plaintext
alembic/
├── env.py
├── script.py.mako
├── README.md
└── versions/
    ├── be88c17d1e9b_create_post_table.py
    ├── 86f420f80cb7_add_content_column_to_post_table.py
    ├── 7f4b90107b7d_add_users_table.py
    ├── 45b04d841a06_add_foreign_key_constraint_to_posts_.py
```

### 8.2 Update the migration file to add the `owner_id` column to the `posts` table

We need to update the migration file `40e622202020_add_foreign_key_constraint_to_posts_table.py` to add the `owner_id` column to the `posts` table.

```python
# 40e622202020_add_foreign_key_constraint_to_posts_table.py
"""add foreign key constraint to posts table

Revision ID: 45b04d841a06
Revises: 7f4b90107b7d
Create Date: 2026-10-22 17:04:57.626776

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '45b04d841a06'
down_revision: Union[str, Sequence[str], None] = '7f4b90107b7d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('post', sa.Column('owner_id', sa.Integer(), nullable=False))
    op.create_foreign_key('post_users_fk', source_table='post', referent_table='users', local_cols=['owner_id'], remote_cols=['id'], ondelete='CASCADE')
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('post_users_fk', table_name='post')
    op.drop_column('post', 'owner_id')
    pass
```

This will add the foreign key constraint to the `posts` table and the `owner_id` column to the `posts` table. Now we need to run the `alembic upgrade <revision_number>` command to apply the migration to the database.

### 8.3 Apply the migration to the database

We need to apply the migration to the database by running the following command:

```bash
alembic current # Show which migration revision is applied to this database. -> 7f4b90107b7d
alembic upgrade head # Apply the migration to the database.
```

This will apply the migration to the database. Now we can check the database to see if the foreign key constraint has been added to the `posts` table and the `owner_id` column has been added to the `posts` table.

## 9. Add last few columns to `post` table

We need to add the last few columns to the `posts` table by adding the `published` column, `created_at` column and `updated_at` column. We can do this by doing the following steps:

1. Create a new migration file.
2. Update the migration file to add the `published` column, `created_at` column and `updated_at` column.
3. Apply the migration to the database.
4. Rollback or undo the migration/changes.

### 9.1 Create a new migration file

```bash
alembic revision -m "add last few columns to post table"
```

This will create a new migration file in the `versions/` directory.

```plaintext
alembic/
├── env.py
├── script.py.mako
├── README.md
└── versions/
    ├── 9c45c365ddd0_add_last_few_columns_to_post_table.py
```

### 9.2 Update the migration file to add the `published` column, `created_at` column and `updated_at` column

We need to update the migration file `9c45c365ddd0_add_last_few_columns_to_post_table.py` to add the `published` column, `created_at` column and `updated_at` column.

```python
# 9c45c365ddd0_add_last_few_columns_to_post_table.py
"""add last few columns to post table

Revision ID: 9c45c365ddd0
Revises: 45b04d841a06
Create Date: 2026-10-22 17:25:05.103110

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text


# revision identifiers, used by Alembic.
revision: str = '9c45c365ddd0'
down_revision: Union[str, Sequence[str], None] = '45b04d841a06'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('post', sa.Column('published', sa.Boolean(), server_default='true', nullable=False))
    op.add_column('post', sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=text('now()')))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('post', 'published')
    op.drop_column('post', 'created_at')
    pass
```

This will add the `published` column, `created_at` column and `updated_at` column to the `posts` table. Now we need to run the `alembic upgrade <revision_number>` command to apply the migration to the database.

### 9.3 Apply the migration to the database

We need to apply the migration to the database by running the following command:

```bash
alembic current # Show which migration revision is applied to this database. -> 45b04d841a06
alembic heads # Show the latest revision(s) in the migration files. -> 9c45c365ddd0
alembic upgrade head # Apply the migration to the database.
```

This will apply the migration to the database. Now we can check the database to see if the `published` column, `created_at` column have been added to the `posts` table.

The `posts` table has been updated with the following columns:

| id  | title | content | owner_id | published | created_at |
| --- | ----- | ------- | -------- | --------- | ---------- |

Also the constraints have been applied to the `posts` table. The `published` column is a boolean and the `created_at` column is a timestamp with timezone.

## 10. Downgrade to `add users table` revision

We can downgrade to the `add users table` revision by running the following command:

```bash
alembic downgrade 7f4b90107b7d # Downgrade to the `add users table` revision.
```

This will downgrade the database to the `add users table` revision. Now we can check the database to see if the `published` column, `created_at` column have been removed from the `posts` table.

## 11. Generate the `votes` table with autogenerate

1. Create a new migration file with autogenerate.
2. Run the migration to the database.

### 11.1 Create a new migration file with autogenerate

We can generate the `votes` table with autogenerate by running the following command:

```bash
alembic revision --autogenerate -m "auto-vote" # Generate the `votes` table with autogenerate.
```

This will generate the `votes` table with autogenerate. Now we can check the migration file to see if the `votes` table has been generated.

```plaintext
alembic/
├── env.py
├── script.py.mako
├── README.md
└── versions/
    ├── <revision_number>_auto_vote.py
```

```python
# <revision_number>_auto_vote.py
"""auto-vote

Revision ID: b8b8be1eabfa
Revises: 9c45c365ddd0
Create Date: 2026-10-22 17:43:54.952588

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b8b8be1eabfa'
down_revision: Union[str, Sequence[str], None] = '9c45c365ddd0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('posts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('content', sa.String(), nullable=False),
    sa.Column('published', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('owner_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('votes',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('post_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_id', 'post_id')
    )
    op.drop_table('post')
    op.add_column('users', sa.Column('phone_number', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'phone_number')
    op.create_table('post',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('content', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('owner_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('published', sa.BOOLEAN(), server_default=sa.text('true'), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], name=op.f('post_users_fk'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('post_pkey'))
    )
    op.drop_table('votes')
    op.drop_table('posts')
    # ### end Alembic commands ###
```

### 11.2 Run the migration to the database

We need to run the migration to the database by running the following command:

```bash
alembic current # Show which migration revision is applied to this database. -> 9c45c365ddd0
alembic heads # Show the latest revision(s) in the migration files. -> b8b8be1eabfa
alembic upgrade head # Apply the migration to the database.
```

This will apply the migration to the database. Now we can check the database to see if the `votes` table has been created.

The `votes` table has been created with the following columns:

| user_id | post_id |
| ------- | ------- |

## 12. Add `phone_number` column to `users` table

We need to add the `phone_number` column to the `users` table by running `autogenerate` command:

1. Add the `phone_number` column to the `users` table.
2. Add the migration file to the `versions/` directory.
3. Run the migration to the database.

### 12.1 Add the `phone_number` column to the `users` table

Update the `users` table in `models.py` to add the `phone_number` column.

```python
# models.py
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.sql.expression import text

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    phone_number = Column(String, nullable=True)
```

### 12.2 Add the migration file to the `versions/` directory

We need to add the migration file to the `versions/` directory by running the following command:

```bash
alembic revision --autogenerate -m "add phone_number"
```

This will create a new migration file in the `versions/` directory.

```plaintext
alembic/
├── env.py
├── script.py.mako
├── README.md
└── versions/
    ├── <revision_number>_add_phone_number.py
```

```python
# <revision_number>_add_phone_number.py
"""add phone_number

Revision ID: c51174297e47
Revises: b8b8be1eabfa
Create Date: 2026-10-22 18:22:27.119972

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c51174297e47'
down_revision: Union[str, Sequence[str], None] = 'b8b8be1eabfa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('phone_number', sa.String(), nullable=True))
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'phone_number')
    pass
    # ### end Alembic commands ###
```

### 12.3 Run the migration to the database

We need to run the migration to the database by running the following command:

```bash
alembic upgrade head # Apply the migration to the database.
```

This will apply the migration to the database. Now we can check the database to see if the `phone_number` column has been added to the `users` table.

The `users` table has been updated with the following columns:

| id  | email | password | created_at | phone_number |
| --- | ----- | -------- | ---------- | ------------ |

Also the constraints have been applied to the `users` table. The `phone_number` column is a string.
