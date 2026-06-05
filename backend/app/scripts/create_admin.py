import getpass
import os
import sys

from sqlalchemy.exc import IntegrityError

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User


def _read_value(env_name: str, prompt: str, secret: bool = False) -> str:
    value = os.getenv(env_name, "").strip()
    if value:
        return value
    if secret:
        return getpass.getpass(prompt).strip()
    return input(prompt).strip()


def main() -> int:
    full_name = _read_value("ADMIN_FULL_NAME", "Admin full name: ")
    email = _read_value("ADMIN_EMAIL", "Admin email: ").lower()
    password = _read_value("ADMIN_PASSWORD", "Admin password: ", secret=True)

    if not full_name or not email or not password:
        print("Admin full name, email, and password are required.")
        return 1

    if len(password) < 6:
        print("Admin password must be at least 6 characters.")
        return 1

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print("A user with this email already exists.")
            return 1

        admin = User(
            full_name=full_name,
            email=email,
            password_hash=hash_password(password),
            role="admin",
            is_active=True,
        )
        db.add(admin)
        db.commit()
        print(f"Admin user created: {email}")
        return 0
    except IntegrityError:
        db.rollback()
        print("Unable to create admin user with these details.")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
