from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 'postgresql://<username>:<password>@<host>:<port>/<database_name>'
# We are using the PostgreSQL database
SQLALCHEMY_DATABASE_URL = 'postgresql+psycopg2://postgres:root@localhost:5432/fastapi'

# Create the engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create the session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db  # This will yield the database session
    finally:
        db.close()  # This will close the database session