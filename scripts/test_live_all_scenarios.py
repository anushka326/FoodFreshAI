import sys
import os
import json
import uuid
import httpx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.database import chat_db

def run_tests():
    print("=" * 70)
    print("FOODFRESH AI - FRESHOBUDDY COMPREHENSIVE AI & MODE VERIFICATION")
    print("=" * 70)

    # 1. Obtain user token
    with chat_db.get_db_connection() as conn:
        row = conn.execute("SELECT user_id, email FROM users LIMIT 1").fetchone()
        user_id = row["user_id"]
        token = chat_db.create_session(user_id)
        print(f"Authenticated as user: {row['email']} (Token: {token[:12]}...)")

    client = httpx.Client(base_url="http://127.0.0.1:8000", timeout=60.0)
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    test_cases = [
        {
            "name": "1. Maharashtra High Shelf Life Fruit (Image 1 Query)",
            "query": "Which is the fruit that could have more shelf life? And which is available in Maharashtra",
            "pantry_mode": False,
            "must_contain": ["shelf life"],
            "must_not_contain": ["Your pantry history is currently empty"],
        },
        {
            "name": "2. Maharashtra Low Shelf Life Fruit (Image 2 Query)",
            "query": "Fruit having very low shelf life in Maharashtra",
            "pantry_mode": False,
            "must_contain": ["low", "shelf life"],
            "must_not_contain": ["Your pantry history is currently empty"],
        },
        {
            "name": "3. Kashmiri Apples Shelf Life (Image 3 Query)",
            "query": "what could be the average shelf life of the kashmiri apples freshly bought",
            "pantry_mode": False,
            "must_contain": ["apple"],
            "must_not_contain": ["Your pantry history is currently empty", "The Kashmiri in my offline database"],
        },
        {
            "name": "4. Green Apples Shelf Life (Image 4 Query)",
            "query": "What is the average shelf life of freshly bought green apples?",
            "pantry_mode": False,
            "must_contain": ["apple", "week"],
            "must_not_contain": ["Your pantry history is currently empty"],
        },
        {
            "name": "5. Cold Drink Shelf Life (Original Failure 1)",
            "query": "What is the average shelf life of a cold drink?",
            "pantry_mode": False,
            "must_contain": ["drink", "month"],
            "must_not_contain": ["Your pantry history is currently empty"],
        },
        {
            "name": "6. Coldrinks Shelf Life (Original Failure 2)",
            "query": "Coldrinks shelf life",
            "pantry_mode": False,
            "must_contain": ["drink"],
            "must_not_contain": ["Your pantry history is currently empty"],
        },
        {
            "name": "7. Cooked Rice Safety",
            "query": "How long can cooked rice remain in the refrigerator?",
            "pantry_mode": False,
            "must_contain": ["rice", "day"],
            "must_not_contain": ["Your pantry history is currently empty"],
        },
        {
            "name": "8. Strawberry Storage",
            "query": "How should I store strawberries?",
            "pantry_mode": False,
            "must_contain": ["strawberr"],
            "must_not_contain": ["Your pantry history is currently empty"],
        },
        {
            "name": "9. Pantry Mode OFF: Inventory Query (Global Mode Guard)",
            "query": "Do I have mangoes?",
            "pantry_mode": False,
            "must_not_contain": ["saved in your pantry", "Your pantry history is currently empty"],
        },
        {
            "name": "10. Pantry Mode ON: Populated Pantry Eat First",
            "query": "Which food should I eat first?",
            "pantry_mode": True,
            "must_contain": ["eat first", "priority"],
            "must_not_contain": ["Your pantry history is currently empty"],
        },
        {
            "name": "11. Pantry Mode ON: Empty Pantry Guard for New User",
            "query": "Which food should I eat first?",
            "pantry_mode": True,
            "use_empty_user": True,
            "must_contain": ["pantry is currently empty"],
        },
    ]

    passed = 0
    total = len(test_cases)

    for tc in test_cases:
        print(f"\n--- Testing: {tc['name']} ---")
        print(f"Query: \"{tc['query']}\" | PantryMode: {tc['pantry_mode']}")
        
        req_headers = headers
        if tc.get("use_empty_user"):
            empty_uid = f"usr_empty_{uuid.uuid4().hex[:8]}"
            chat_db.create_user(empty_uid, f"{empty_uid}@example.com", "hash$dummy", "Empty Pantry User")
            empty_token = chat_db.create_session(empty_uid)
            req_headers = {"Authorization": f"Bearer {empty_token}", "Content-Type": "application/json"}

        payload = {"message": tc["query"], "pantryMode": tc["pantry_mode"]}
        try:
            resp = client.post("/api/fresho-buddy/chat", json=payload, headers=req_headers)
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
            data = resp.json()
            reply = data.get("reply", {})
            text = reply.get("text", "")
            model = reply.get("model", "")
            status = reply.get("status", "")

            print(f"Status: {status} | Model: {model}")
            print(f"Reply Preview: {text[:200]}...")

            # Assertions
            if "must_contain" in tc:
                for mc in tc["must_contain"]:
                    assert mc.lower() in text.lower(), f"Expected '{mc}' in response text!"
            if "must_not_contain" in tc:
                for mnc in tc["must_not_contain"]:
                    assert mnc.lower() not in text.lower(), f"Forbidden string '{mnc}' found in response!"

            print(f"--> [PASS] {tc['name']}")
            passed += 1
        except Exception as e:
            print(f"--> [FAIL] {tc['name']}: {e}")

    print("\n" + "=" * 70)
    print(f"TEST SUMMARY: {passed}/{total} Passed")
    print("=" * 70)
    if passed == total:
        print("ALL TESTS PASSED WITH ZERO REGRESSIONS! 🌱")
    else:
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
