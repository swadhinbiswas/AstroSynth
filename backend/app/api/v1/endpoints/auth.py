from fastapi import APIRouter, Depends

from app.core.security import (
    Role,
    create_access_token,
    get_current_user,
    hash_password,
    require_roles,
    verify_password,
)

router = APIRouter(tags=["auth"])
# Demo user store (Postgres users table is canonical; this keeps the demo runnable w/o DB).
_USERS: dict[str, dict] = {}


@router.post("/auth/register")
def register(email: str, password: str, full_name: str = ""):
    if email in _USERS:
        return {"ok": False, "message": "User exists"}
    _USERS[email] = {
        "password": hash_password(password),
        "role": Role.SCIENTIST.value,
        "full_name": full_name,
    }
    return {"ok": True, "token": create_access_token(email, Role.SCIENTIST.value)}


@router.post("/auth/login")
def login(email: str, password: str):
    u = _USERS.get(email)
    if not u or not verify_password(password, u["password"]):
        # Demo fallback account
        if email == "demo@astrosynth.space" and password == "demo1234":
            return {
                "ok": True,
                "token": create_access_token(email, Role.SCIENTIST.value),
            }
        return {
            "ok": False,
            "message": "Invalid credentials (hint: demo@astrosynth.space / demo1234)",
        }
    return {"ok": True, "token": create_access_token(email, u["role"])}


@router.get("/me")
def me(user=Depends(get_current_user)):
    return {"user": user}


@router.get("/admin/ping")
def admin_ping(user=Depends(require_roles(Role.ADMIN))):
    return {"ok": True, "msg": f"hello admin {user['sub']}"}
