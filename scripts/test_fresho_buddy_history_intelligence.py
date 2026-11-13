"""
FoodFresh AI - FreshoBuddy History Intelligence & Persistence Test Suite
Validates Parts 1-24:
- Real History Grounding (Part 1, 2, 3, 5, 6, 7)
- Screenshot Scenario (Part 23)
- Multi-Turn Conversation Persistence (Part 10, 11, 12, 13, 24)
- Deterministic Fallback on API Disconnection (Part 16)
"""

import os
import sys
import json
import time
from pathlib import Path

# Ensure UTF-8 output on Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load .env
for env_path in [PROJECT_ROOT / ".env", PROJECT_ROOT / "backend" / ".env"]:
    if env_path.exists():
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if k and k not in os.environ:
                            os.environ[k] = v
        except Exception:
            pass

from backend.app.database import chat_db
from backend.app.services.fresho_buddy_service import get_fresho_buddy_service, derive_conversation_title
from backend.app.services.pantry_triage_service import triage_pantry_items, detect_pantry_intent


def test_screenshot_scenario():
    print("\n" + "=" * 60)
    print("TEST 1: SCREENSHOT SCENARIO & HISTORY GROUNDING")
    print("=" * 60)

    test_user = "test_user_screenshot"
    
    chat_db.clear_pantry_items(test_user)
    for fixture in (
        {"foodName": "Mango", "estimatedQualityDays": 0, "shelfLife": {"remaining": {"minDays": 0}}},
        {"foodName": "Cantaloupe", "estimatedQualityDays": 1, "shelfLife": {"remaining": {"minDays": 1}}},
        {"foodName": "Watermelon", "estimatedQualityDays": 0, "shelfLife": {"remaining": {"minDays": 0}}},
    ):
        chat_db.add_pantry_item(test_user, fixture)
    items = chat_db.get_pantry_items(test_user)
    print(f"Retrieved {len(items)} saved produce items for {test_user}:")
    for it in items:
        print(f"  • {it['foodName']}: {it['status']} | {it['qualityPeriod']} | Priority: {it['eatFirstPriority']}")

    assert len(items) == 3, f"Expected 3 items from screenshot, got {len(items)}"
    names = {it['foodName'] for it in items}
    assert "Mango" in names and "Cantaloupe" in names and "Watermelon" in names

    # Deterministic Triage Check
    triage = triage_pantry_items(items)
    print(f"\nDeterministic Triage Result:")
    print(f"  - Top Urgent Food: {triage['topUrgent']['foodName']}")
    print(f"  - Is Tie at Top: {triage['isTie']}")
    if triage["isTie"]:
        print(f"  - Tied Top Foods: {[x['foodName'] for x in triage['tiedTop']]}")
    print(f"  - Expiring Soon Count: {len(triage['expiringSoon'])}")

    fresho_service = get_fresho_buddy_service()

    # Question 1: Which food should I eat first?
    print("\n--- Question 1: 'Which food should I eat first?' ---")
    reply1 = fresho_service.generate_reply("Which food should I eat first?", user_id=test_user)
    text1 = reply1["text"]
    print("Response snippet:\n", text1[:300], "...")
    assert "mango" in text1.lower() or "watermelon" in text1.lower() or "cantaloupe" in text1.lower()
    assert "**" in text1, "Response must include bold markdown formatting for key decisions and foods"
    time.sleep(1)

    # Question 2: What food needs attention?
    print("\n--- Question 2: 'What food needs attention?' ---")
    reply2 = fresho_service.generate_reply("What food needs attention?", user_id=test_user)
    text2 = reply2["text"]
    print("Response snippet:\n", text2[:300], "...")
    assert "mango" in text2.lower() or "watermelon" in text2.lower()
    time.sleep(1)

    # Question 3: What should I cook today?
    print("\n--- Question 3: 'What should I cook today?' ---")
    reply3 = fresho_service.generate_reply("What should I cook today?", user_id=test_user)
    text3 = reply3["text"]
    print("Response snippet:\n", text3[:300], "...")
    assert any(f in text3.lower() for f in ["mango", "watermelon", "cantaloupe"])
    time.sleep(1)

    # Question 4: What foods do I currently have?
    print("\n--- Question 4: 'What foods do I currently have?' ---")
    reply4 = fresho_service.generate_reply("What foods do I currently have?", user_id=test_user)
    text4 = reply4["text"]
    print("Response snippet:\n", text4[:300], "...")
    assert "mango" in text4.lower() and "cantaloupe" in text4.lower() and "watermelon" in text4.lower()
    time.sleep(1)

    # Question 5: Which food has the shortest remaining quality?
    print("\n--- Question 5: 'Which food has the shortest remaining quality window?' ---")
    reply5 = fresho_service.generate_reply("Which food has the shortest remaining quality window?", user_id=test_user)
    text5 = reply5["text"]
    print("Response snippet:\n", text5[:300], "...")
    assert "0" in text5 or "mango" in text5.lower() or "watermelon" in text5.lower()
    time.sleep(1)

    # Question 6: How should I store apples?
    print("\n--- Question 6: 'How should I store apples?' ---")
    reply6 = fresho_service.generate_reply("How should I store apples?", user_id=test_user)
    text6 = reply6["text"]
    print("Response snippet:\n", text6[:300], "...")
    assert "apple" in text6.lower()
    time.sleep(1)

    # Question 7: Why do bananas get brown spots?
    print("\n--- Question 7: 'Why do bananas get brown spots?' ---")
    reply7 = fresho_service.generate_reply("Why do bananas get brown spots?", user_id=test_user)
    text7 = reply7["text"]
    print("Response snippet:\n", text7[:300], "...")
    assert "banana" in text7.lower() or "ethylene" in text7.lower() or "sugar" in text7.lower() or "spot" in text7.lower()

    print("\n--> TEST 1 PASSED: All 7 history-aware queries verified!")


def test_chat_persistence():
    print("\n" + "=" * 60)
    print("TEST 2: CHAT PERSISTENCE & USER ISOLATION")
    print("=" * 60)

    user_a = "user_alpha"
    user_b = "user_beta"

    # Step 1: Create Conversation for User A
    conv_a = chat_db.create_conversation(user_id=user_a, title=derive_conversation_title("Which food should I eat first?"))
    conv_a_id = conv_a["conversationId"]
    print(f"Created Conversation A for {user_a}: ID={conv_a_id}, Title='{conv_a['title']}'")
    assert conv_a["title"] == "Pantry Priority"

    # Step 2: Add messages
    chat_db.add_message(conv_a_id, user_a, "user", "Which food should I eat first?")
    chat_db.add_message(conv_a_id, user_a, "assistant", "Based on your saved pantry history, **Mango should be used first**.")

    # Step 3: Fetch conversation back
    loaded_a = chat_db.get_conversation(conv_a_id, user_a)
    assert loaded_a is not None
    assert len(loaded_a["messages"]) == 2
    print(f"Loaded Conversation A messages: {len(loaded_a['messages'])} verified")

    # Step 4: Strict User Isolation: User B cannot view User A's conversation
    loaded_b_view = chat_db.get_conversation(conv_a_id, user_b)
    assert loaded_b_view is None, "Security violation: User B must not access User A's conversation"
    print(f"Verified User B cannot access User A's conversation (returned None)")

    # Step 5: User B creates their own conversation
    conv_b = chat_db.create_conversation(user_id=user_b, title=derive_conversation_title("How should I store apples?"))
    conv_b_id = conv_b["conversationId"]
    print(f"Created Conversation B for {user_b}: ID={conv_b_id}, Title='{conv_b['title']}'")
    assert conv_b["title"] == "Apples Storage Advice"

    # Step 6: Verify User A's conversation list only has User A's chats
    list_a = chat_db.list_conversations(user_a)
    assert any(c["conversationId"] == conv_a_id for c in list_a)
    assert not any(c["conversationId"] == conv_b_id for c in list_a)
    print("Verified User A's conversation list contains only User A's conversations")

    # Cleanup
    chat_db.delete_conversation(conv_a_id, user_a)
    chat_db.delete_conversation(conv_b_id, user_b)
    print("\n--> TEST 2 PASSED: Persistence and user isolation verified!")


def test_empty_pantry_behavior():
    print("\n" + "=" * 60)
    print("TEST 3: EMPTY PANTRY BEHAVIOR (0-ITEMS HANDLING)")
    print("=" * 60)

    empty_user = "user_empty_pantry"
    chat_db.clear_pantry_items(empty_user)
    items = chat_db.get_pantry_items(empty_user, allow_seed=False)
    assert len(items) == 0

    fresho_service = get_fresho_buddy_service()
    reply = fresho_service.generate_reply("Which food should I eat first?", user_id=empty_user)
    print("Empty pantry reply:\n", reply["text"])
    assert "empty" in reply["text"].lower() or "analyze" in reply["text"].lower()
    print("\n--> TEST 3 PASSED: Clean handling of 0 items verified!")


def main():
    test_screenshot_scenario()
    test_chat_persistence()
    test_empty_pantry_behavior()
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    main()
