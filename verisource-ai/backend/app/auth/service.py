import bcrypt
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.users.models import User


# 🔒 Hash password
def get_password_hash(password: str) -> str:
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


# 🔒 Verify password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def create_user(db: Session, username: str, password: str, role: str):
    hashed_password = get_password_hash(password)

    user = User(
        username=username,
        password=hashed_password,
        role=role,
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
        return {
            "message": "User registered successfully",
            "username": user.username,
            "role": user.role,
        }

    except IntegrityError:
        db.rollback()
        raise Exception("Username already exists")


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        return None

    if not verify_password(password, user.password):
        return None

    return user