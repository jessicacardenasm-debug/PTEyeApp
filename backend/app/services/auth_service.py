from app.models.user import UserInfo
from app.core.security import verify_password, hash_password

# Demo users — replace with real DB (SQLAlchemy + PostgreSQL) in production
_DEMO_USERS = {
    "dr.garcia@ocularguard.com": {
        "id": "USR-001",
        "name": "Dr. García",
        "email": "dr.garcia@ocularguard.com",
        "role": "Oftalmólogo",
        "hashed_password": hash_password("demo1234"),
    }
}


def authenticate_user(email: str, password: str) -> UserInfo | None:
    user = _DEMO_USERS.get(email)
    if not user or not verify_password(password, user["hashed_password"]):
        return None
    return UserInfo(**{k: v for k, v in user.items() if k != "hashed_password"})
