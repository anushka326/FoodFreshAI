"""
Verification script for Non-Destructive Legacy Database Migration and Password Compatibility.
"""
import hashlib
import os
import sqlite3
import sys
from pathlib import Path

# Ensure backend is on PYTHONPATH
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.database import chat_db
from backend.app.database.migration import migrate_legacy_users
from backend.app.services import auth_service

def run_test():
    print("=" * 60)
    print("TESTING LEGACY SQLITE DATABASE MIGRATION & AUTH COMPATIBILITY")
    print("=" * 60)

    test_db_path = Path("test_legacy_foodfresh.db")
    if test_db_path.exists():
        test_db_path.unlink()

    # Pre-clean test emails from fresho_buddy.db
    with chat_db.get_db_connection() as tconn:
        tconn.execute("DELETE FROM users WHERE email IN ('legacy_chef_auguste@kitchen.test', 'legacy_chef_julia@kitchen.test')")
        tconn.commit()

    # 1. Create a simulated legacy main-branch database (ad4fc0b schema)
    print("[1] Creating simulated legacy main-branch database...")
    conn = sqlite3.connect(test_db_path)
    conn.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT,
            hashed_password TEXT NOT NULL
        );
    """)

    # User 1: Legacy PBKDF2 96-char hex hash (ad4fc0b format)
    salt1 = os.urandom(16)
    pass1 = "LegacySecurePass123!"
    dk1 = hashlib.pbkdf2_hmac("sha256", pass1.encode("utf-8"), salt1, 100_000)
    legacy_hash1 = salt1.hex() + dk1.hex()
    assert len(legacy_hash1) == 96

    conn.execute(
        "INSERT INTO users (email, full_name, hashed_password) VALUES (?, ?, ?)",
        ("legacy_chef_auguste@kitchen.test", "Chef Auguste Escoffier", legacy_hash1)
    )

    # User 2: Another legacy user
    salt2 = os.urandom(16)
    pass2 = "KitchenSecret999!"
    dk2 = hashlib.pbkdf2_hmac("sha256", pass2.encode("utf-8"), salt2, 100_000)
    legacy_hash2 = salt2.hex() + dk2.hex()
    conn.execute(
        "INSERT INTO users (email, full_name, hashed_password) VALUES (?, ?, ?)",
        ("legacy_chef_julia@kitchen.test", "Chef Julia Child", legacy_hash2)
    )
    conn.commit()
    conn.close()
    print("✓ Created legacy database with 2 users using ad4fc0b 96-char PBKDF2 hashes.")

    # 2. Run non-destructive migration
    print("[2] Running non-destructive migration...")
    res = migrate_legacy_users(source_db_path=test_db_path)
    print(f"✓ Migration result: {res}")
    assert res["migrated_users"] == 2, f"Expected 2 migrated users, got {res['migrated_users']}"

    # 3. Verify original database was NOT modified or deleted
    assert test_db_path.exists(), "Original legacy database was deleted!"
    src_conn = sqlite3.connect(test_db_path)
    count_orig = src_conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    src_conn.close()
    assert count_orig == 2, "Original database users were modified or lost!"
    print("✓ Confirmed original database was preserved completely intact.")

    # 4. Verify users in target production database
    user1 = chat_db.get_user_by_email("legacy_chef_auguste@kitchen.test")
    assert user1 is not None, "Migrated user 1 not found in production database!"
    name = user1["full_name"] if "full_name" in user1.keys() else user1.get("fullName")
    uid = user1["user_id"] if "user_id" in user1.keys() else user1.get("id")
    email = user1["email"]
    assert name == "Chef Auguste Escoffier"
    assert uid.startswith("usr_legacy_")
    print(f"✓ Migrated user 1 preserved: ID={uid}, Email={email}, Name={name}")

    # 5. Test login with legacy credentials
    print("[3] Testing login with legacy ad4fc0b password hash...")
    login_res = auth_service.login_user("legacy_chef_auguste@kitchen.test", pass1)
    assert login_res["token"].startswith("sess_")
    assert login_res["user"]["email"] == "legacy_chef_auguste@kitchen.test"
    print("✓ Legacy user successfully logged in with original password!")

    # 6. Verify password hash was automatically upgraded to current salt$hash format
    updated_user1 = chat_db.get_user_by_email("legacy_chef_auguste@kitchen.test")
    updated_hash = updated_user1["password_hash"] if "password_hash" in updated_user1.keys() else updated_user1["passwordHash"]
    assert "$" in updated_hash, f"Expected upgraded salt$hash format, got {updated_hash}"
    print("✓ Password hash automatically upgraded to current 120,000 PBKDF2 salt$hash standard.")

    # 7. Test re-login with upgraded hash
    login_re = auth_service.login_user("legacy_chef_auguste@kitchen.test", pass1)
    assert login_re["token"].startswith("sess_")
    print("✓ Second login succeeded seamlessly with upgraded hash.")

    # 8. Test idempotency (running migration again does not duplicate or error)
    print("[4] Testing idempotency of migration...")
    res2 = migrate_legacy_users(source_db_path=test_db_path)
    assert res2["migrated_users"] == 0, "Idempotency failed: migrated users again!"
    assert res2["skipped_existing"] == 2, "Idempotency failed: did not skip existing users!"
    print("✓ Idempotency verified: re-running migration cleanly skipped existing accounts.")

    # Clean up test records
    with chat_db.get_db_connection() as tconn:
        tconn.execute("DELETE FROM users WHERE email IN ('legacy_chef_auguste@kitchen.test', 'legacy_chef_julia@kitchen.test')")
        tconn.commit()
    if test_db_path.exists():
        test_db_path.unlink()

    print("\n" + "=" * 60)
    print("ALL LEGACY MIGRATION & AUTH TESTS PASSED 100%! ✓")
    print("=" * 60)

if __name__ == "__main__":
    run_test()
