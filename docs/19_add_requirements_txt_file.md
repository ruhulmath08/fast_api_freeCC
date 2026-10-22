# Add requirement.txt file

We need to add the `requirement.txt` file to the project. This file will contain the dependencies for the project. In the project root directory, create a file named `requirement.txt`.

```plaintext
alembic==1.14.0
fastapi==0.115.6
sqlalchemy==2.0.39
psycopg2-binary==2.9.10
```

This file will contain the dependencies for the project. We can use the `pip freeze` command to get the dependencies for the project.

```bash
pip freeze > requirement.txt
```

This will create a `requirement.txt` file in the project root directory and it will contain the dependencies for the project.

**requirement.txt file content**:

```txt
alembic==1.14.0
fastapi==0.115.6
sqlalchemy==2.0.39
psycopg2-binary==2.9.10
... # Other dependencies
```

When another developer wants to set up the project on their machine, they can simply run the `pip install -r requirement.txt` command to install the dependencies for the project.

```bash
pip install -r requirement.txt
```

This will install the dependencies for the project.

## Resources

- [pip freeze](https://pip.pypa.io/en/stable/reference/pip_freeze/)
- [pip freeze command](https://pip.pypa.io/en/stable/reference/pip_freeze/)
- [pip freeze command](https://pip.pypa.io/en/stable/reference/pip_freeze/)
