import os
import sys
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
from backend.app.database import chat_db
from backend.app.services import auth_service
from backend.app.routes.auth import register, RegisterRequest, login, LoginRequest
from fastapi import HTTPException
from pydantic import ValidationError

print("=" * 60)
print("FOODFRESH AI AUTHENTICATION & REGISTRATION VERIFICATION SUITE")
print("=" * 60)

# 1. Test registration with a new email address
test_email = f"chef_test_{uuid.uuid4().hex[:8]}@example.com"
test_password = "ChefPassword!2026"
test_name = "Master Chef Auguste"

print(f"\n[1] Registering new user: {test_email}...")
req = RegisterRequest(fullName=test_name, email=test_email, password=test_password)
reg_res = register(req)

assert reg_res["success"] is True, "Registration success flag must be True"
assert "token" in reg_res and reg_res["token"].startswith("sess_"), "Must return valid session token"
user_obj = reg_res["user"]
assert user_obj["email"] == test_email.lower(), "Returned user email must match"
assert user_obj["fullName"] == test_name, "Returned user name must match"
user_id = user_obj["id"]
print(f"--> [PASS] Registration API succeeded. User ID: {user_id}, Token: {reg_res['token']}")

# 2. Verify user is actually saved in SQLite
print(f"\n[2] Verifying record in SQLite database...")
with chat_db.get_db_connection() as conn:
    cur = conn.cursor()
    cur.execute("SELECT user_id, email, password_hash, full_name, created_at FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()

assert row is not None, f"User {user_id} must be in SQLite database"
assert row["email"] == test_email.lower()
assert row["full_name"] == test_name
assert "$" in row["password_hash"], "Password hash must contain salt and hash"
print(f"--> [PASS] User successfully verified in SQLite table 'users':")
print(f"    user_id: {row['user_id']}")
print(f"    email: {row['email']}")
print(f"    full_name: {row['full_name']}")
print(f"    created_at: {row['created_at']}")

# 3. Test login with newly registered credentials
print(f"\n[3] Testing login with newly registered credentials...")
login_req = LoginRequest(email=test_email, password=test_password)
login_res = login(login_req)

assert login_res["success"] is True
assert login_res["user"]["id"] == user_id
assert login_res["token"].startswith("sess_")
print(f"--> [PASS] Login succeeded with new credentials! Token: {login_res['token']}")

# 4. Verify session resolution
print(f"\n[4] Verifying session token resolution...")
resolved_user = auth_service.resolve_session(login_res["token"])
assert resolved_user is not None
assert resolved_user["id"] == user_id
print(f"--> [PASS] Session resolved to authenticated user: {resolved_user['fullName']} ({resolved_user['id']})")

# 5. Test duplicate email detection (exact match and case-insensitive match)
print(f"\n[5] Testing duplicate email detection...")
try:
    dup_req = RegisterRequest(fullName="Duplicate User", email=test_email.upper(), password="AnotherPassword123")
    register(dup_req)
    assert False, "Duplicate registration should have failed"
except HTTPException as e:
    assert e.status_code == 400, f"Expected 400 Bad Request, got {e.status_code}"
    assert "already exists" in e.detail.lower(), f"Unexpected error detail: {e.detail}"
    print(f"--> [PASS] Case-insensitive duplicate email correctly rejected: HTTP {e.status_code} - '{e.detail}'")

# 6. Test invalid inputs (password < 6 chars, invalid email)
print(f"\n[6] Testing validation errors for invalid inputs...")
try:
    RegisterRequest(fullName="Test", email="valid@example.com", password="123")
    assert False, "Should fail on short password"
except ValidationError as e:
    print(f"--> [PASS] Pydantic correctly caught short password: {e.errors()[0]['msg']}")

try:
    auth_service.register_user(email="notanemail", password="validpassword", full_name="Test")
    assert False, "Should fail on invalid email"
except ValueError as e:
    print(f"--> [PASS] auth_service correctly caught invalid email: '{e}'")

# 7. Test wrong password on login
print(f"\n[7] Testing login with wrong password...")
try:
    wrong_req = LoginRequest(email=test_email, password="WrongPassword999")
    login(wrong_req)
    assert False, "Login with wrong password should fail"
except HTTPException as e:
    assert e.status_code == 401
    print(f"--> [PASS] Wrong password rejected: HTTP {e.status_code} - '{e.detail}'")

print("\n" + "=" * 60)
print("ALL AUTHENTICATION TESTS PASSED SUCCESSFULLY!")
print("=" * 60)

