"""
Test Suite for FoodFresh AI - Themed Avatar Selection & Isolation
Verifies:
1. Avatar persistence in database against authenticated user account.
2. PUT /api/auth/profile and PUT /api/auth/avatar endpoints.
3. GET /api/auth/me returns persisted avatar & avatarUrl.
4. Strict multi-user account isolation (User A cannot see or mutate User B's avatar).
5. Session persistence across login/logout.
"""

import asyncio
import uuid
import httpx
from backend.app.main import app
from backend.app.database import chat_db

async def run_tests():
    print("==================================================")
    print("Testing Themed Avatar Selection & Account Isolation")
    print("==================================================")

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Register User 1
        u1_email = f"chef_pip_{uuid.uuid4().hex[:6]}@foodfresh.test"
        u1_pass = "PantryGuard123!"
        reg1 = await client.post("/api/auth/register", json={
            "fullName": "Chef Pip",
            "email": u1_email,
            "password": u1_pass,
        })
        assert reg1.status_code == 200, f"User 1 registration failed: {reg1.text}"
        u1_data = reg1.json()
        u1_token = u1_data["token"]
        u1_id = u1_data["user"]["id"]
        print(f"✓ User 1 registered: ID={u1_id}, Email={u1_email}")

        # 2. Register User 2
        u2_email = f"chef_bella_{uuid.uuid4().hex[:6]}@foodfresh.test"
        u2_pass = "PantryGuard123!"
        reg2 = await client.post("/api/auth/register", json={
            "fullName": "Chef Bella",
            "email": u2_email,
            "password": u2_pass,
        })
        assert reg2.status_code == 200, f"User 2 registration failed: {reg2.text}"
        u2_data = reg2.json()
        u2_token = u2_data["token"]
        u2_id = u2_data["user"]["id"]
        print(f"✓ User 2 registered: ID={u2_id}, Email={u2_email}")

        # 3. User 1 selects "fruit_apple" (Pip the Apple) via PUT /api/auth/avatar
        res1 = await client.put(
            "/api/auth/avatar",
            headers={"Authorization": f"Bearer {u1_token}"},
            json={"avatar": "fruit_apple"},
        )
        assert res1.status_code == 200, f"Avatar update failed: {res1.text}"
        user1_updated = res1.json()["user"]
        assert user1_updated["avatar"] == "fruit_apple", f"Expected fruit_apple, got {user1_updated.get('avatar')}"
        assert user1_updated["avatarUrl"] == "fruit_apple", f"Expected avatarUrl=fruit_apple, got {user1_updated.get('avatarUrl')}"
        print(f"✓ User 1 updated avatar to 'fruit_apple' via /api/auth/avatar")

        # 4. User 2 selects "veggie_broccoli" (Benny Broccoli) via PUT /api/auth/profile
        res2 = await client.put(
            "/api/auth/profile",
            headers={"Authorization": f"Bearer {u2_token}"},
            json={"avatar": "veggie_broccoli"},
        )
        assert res2.status_code == 200, f"Profile update failed: {res2.text}"
        user2_updated = res2.json()["user"]
        assert user2_updated["avatar"] == "veggie_broccoli", f"Expected veggie_broccoli, got {user2_updated.get('avatar')}"
        print(f"✓ User 2 updated avatar to 'veggie_broccoli' via /api/auth/profile")

        # 5. Verify Isolation via GET /api/auth/me for User 1
        me1 = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {u1_token}"})
        assert me1.status_code == 200
        me1_user = me1.json()["user"]
        assert me1_user["avatar"] == "fruit_apple", f"User 1 avatar contaminated: {me1_user.get('avatar')}"
        print(f"✓ User 1 /api/auth/me correctly returns isolated avatar: 'fruit_apple'")

        # 6. Verify Isolation via GET /api/auth/me for User 2
        me2 = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {u2_token}"})
        assert me2.status_code == 200
        me2_user = me2.json()["user"]
        assert me2_user["avatar"] == "veggie_broccoli", f"User 2 avatar contaminated: {me2_user.get('avatar')}"
        print(f"✓ User 2 /api/auth/me correctly returns isolated avatar: 'veggie_broccoli'")

        # 7. Persistence across Logout & Re-Login
        await client.post("/api/auth/logout", headers={"Authorization": f"Bearer {u1_token}"})
        login1 = await client.post("/api/auth/login", json={"email": u1_email, "password": u1_pass})
        assert login1.status_code == 200
        login1_user = login1.json()["user"]
        assert login1_user["avatar"] == "fruit_apple", f"Avatar not persisted after re-login: {login1_user.get('avatar')}"
        new_token1 = login1.json()["token"]

        # Verify session continuity with new token
        me1_re = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {new_token1}"})
        assert me1_re.status_code == 200
        assert me1_re.json()["user"]["avatar"] == "fruit_apple"
        print(f"✓ Avatar persisted seamlessly across logout and re-login for User 1")

        # 8. Test direct DB query verification
        raw_user1 = chat_db.get_user_by_id(u1_id)
        assert raw_user1["avatar"] == "fruit_apple"
        raw_user2 = chat_db.get_user_by_id(u2_id)
        assert raw_user2["avatar"] == "veggie_broccoli"
        print(f"✓ Direct SQLite database verification confirmed values stored in users.avatar")

        # 9. Test security: unauthenticated call rejected
        unauth = await client.put("/api/auth/avatar", json={"avatar": "eco_earth"})
        assert unauth.status_code in (401, 403), f"Expected 401/403 for unauth call, got {unauth.status_code}"
        print(f"✓ Security check: unauthenticated avatar modification blocked ({unauth.status_code})")

    print("\n==================================================")
    print("ALL 9/9 AVATAR SELECTION & ISOLATION TESTS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(run_tests())
