from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash the password
def hash(password: str):
    return pwd_context.hash(password)

# Verify the password
def verify(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)