# Limitation of SQLAlchemy

SQLAlchemy is a powerful ORM that allows you to interact with your database using Python objects. However, it has some limitations that you should be aware of.

1. Does not allow us to modify the table schema directly.

---

## 1. Does not allow us to modify the database directly

SQLAlchemy does not allow us to do the following:

- Does not allow us to modify the table schema directly.
- Does not allow us to add or remove columns from the table.
- Does not allow us to add or remove foreign keys or constraints keys from the table.

For doing these things, we need to use the tools like `alembic` or `sqlalchemy-migrate`. It will help us to manage the database schema changes.
