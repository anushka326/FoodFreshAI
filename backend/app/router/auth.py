# backend/app/router/auth.py
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlite3 import Connection

from .. import auth, database, schemas

router = APIRouter()

# Dependency that provides a SQLite connection (as a generator)
get_db = database.get_db

@router.post("/register", response_model=schemas.Token)
def register(payload: schemas.UserCreate, db: Connection = Depends(get_db)):
    # Check for existing email
    cur = db.execute("SELECT id FROM users WHERE email = ?", (payload.email,))
    if cur.fetchone():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    hashed = auth.get_password_hash(payload.password)
    db.execute(
        "INSERT INTO users (email, full_name, hashed_password) VALUES (?,?,?)",
        (payload.email, payload.full_name, hashed),
    )
    db.commit()
    # Get the new user's id
    cur = db.execute("SELECT id FROM users WHERE email = ?", (payload.email,))
    user_id = cur.fetchone()["id"]
    access_token = auth.create_access_token(data={"sub": str(user_id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=schemas.Token)
def login(payload: schemas.UserLogin, db: Connection = Depends(get_db)):
    cur = db.execute("SELECT id, hashed_password FROM users WHERE email = ?", (payload.email,))
    row = cur.fetchone()
    if not row or not auth.verify_password(payload.password, row["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": str(row["id"])})
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(token: str = Depends(auth.oauth2_scheme), db: Connection = Depends(get_db)):
    payload = auth.decode_access_token(token)
    if payload is None or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user_id = int(payload["sub"])
    cur = db.execute("SELECT id, email, full_name FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return {"id": row["id"], "email": row["email"], "full_name": row["full_name"]}

@router.get("/me", response_model=schemas.UserOut)
def read_current_user(current_user: dict = Depends(get_current_user)):
    return current_user

