#!/usr/bin/env python3
"""Authenticated API-to-SQLite smoke flow; run explicitly after starting both servers."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import uuid

import requests

ROOT = Path(__file__).resolve().parent.parent
API = "http://127.0.0.1:8000"
WEB = "http://127.0.0.1:3000"
IMAGE = ROOT / "data" / "real_world_eval" / "tomato.jpg"
REPORT = ROOT / "reports" / "application_e2e_test.md"


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def main() -> int:
    run_id = uuid.uuid4().hex[:10]
    email = f"foodfresh-smoke-{run_id}@example.test"
    password = f"FfAI-{uuid.uuid4().hex[:12]}!"
    user_id = None
    token = None
    conversation_id = None
    analysis_id = f"analysis_smoke_{run_id}"
    result = None
    steps: list[str] = []
    session = requests.Session()
    try:
        web_status = requests.get(WEB, timeout=10).status_code
        health = requests.get(f"{API}/api/health", timeout=10)
        require(web_status == 200, f"Frontend returned HTTP {web_status}")
        require(health.status_code == 200, f"Backend health returned HTTP {health.status_code}")
        steps.append(f"Frontend HTTP {web_status}; backend health HTTP {health.status_code}.")

        registered = requests.post(f"{API}/api/auth/register", json={
            "fullName": "FoodFresh API Smoke Test", "email": email, "password": password,
        }, timeout=15)
        require(registered.status_code == 200, f"Registration HTTP {registered.status_code}: {registered.text[:200]}")
        registered_json = registered.json()
        user_id = registered_json["user"]["id"]
        steps.append("Registered a unique test account.")

        login = requests.post(f"{API}/api/auth/login", json={"email": email, "password": password}, timeout=15)
        require(login.status_code == 200, f"Login HTTP {login.status_code}: {login.text[:200]}")
        token = login.json()["token"]
        session.headers.update({"Authorization": f"Bearer {token}"})
        me = session.get(f"{API}/api/auth/me", timeout=10)
        require(me.status_code == 200 and me.json()["user"]["id"] == user_id, "Authenticated identity check failed")
        steps.append("Logged in and verified the authenticated account.")

        require(IMAGE.is_file(), f"Local smoke image is unavailable: {IMAGE}")
        with IMAGE.open("rb") as image_file:
            analyzed = session.post(
                f"{API}/api/food-recognition/predict",
                files={"file": (IMAGE.name, image_file, "image/jpeg")},
                data={"storage_type": "countertop", "days_stored": "0"}, timeout=240,
            )
        require(analyzed.status_code == 200, f"Analysis HTTP {analyzed.status_code}: {analyzed.text[:300]}")
        result = analyzed.json()
        require(result.get("success") is True, "Analysis response did not report success")
        require(result.get("detectedFood"), "Analysis returned no food name")
        steps.append(
            f"Analyzed local image `{IMAGE.relative_to(ROOT)}`: {result.get('detectedFood')}; "
            f"freshness {((result.get('freshness') or {}).get('label'))}; "
            f"models {json.dumps(result.get('modelVersions', {}), sort_keys=True)}."
        )

        freshness = result.get("freshness") or {}
        shelf_life = result.get("shelfLife") or {}
        food = result["detectedFood"]
        record = {
            "id": analysis_id,
            "analysisId": analysis_id,
            "foodName": food,
            "detectedFood": food,
            "foodForm": result.get("foodForm"),
            "status": freshness.get("label") or "Uncertain",
            "statusCategory": "attention" if "rotten" in str(freshness.get("label", "")).lower() else "fresh",
            "qualityScore": result.get("recognitionConfidence"),
            "storageType": "countertop",
            "storageEnvironment": "Countertop Ambient",
            "daysStoredAtAnalysis": 0,
            "freshness": freshness,
            "freshnessState": freshness.get("label"),
            "freshnessConfidence": freshness.get("confidence"),
            "shelfLife": shelf_life,
            "estimatedQualityDays": result.get("estimatedQualityDays"),
            "modelVersions": result.get("modelVersions"),
            "analyzedAt": datetime.now(timezone.utc).isoformat(),
        }
        saved = session.post(f"{API}/api/history", json={"item": record}, timeout=20)
        require(saved.status_code == 200, f"Save HTTP {saved.status_code}: {saved.text[:250]}")
        steps.append("Saved the actual analysis result to pantry history.")

        history = session.get(f"{API}/api/history", timeout=15)
        require(history.status_code == 200, f"History HTTP {history.status_code}")
        saved_row = next((item for item in history.json().get("items", []) if item.get("analysisId") == analysis_id), None)
        require(saved_row is not None, "Saved analysis was absent from refreshed pantry history")
        steps.append(f"Refetched history; record remains, remainingDays={saved_row.get('remainingDays')}.")

        chat1 = session.post(f"{API}/api/fresho-buddy/chat", json={
            "message": "Which food should I eat first?",
        }, timeout=30)
        require(chat1.status_code == 200, f"Pantry chat HTTP {chat1.status_code}: {chat1.text[:250]}")
        chat1_json = chat1.json()
        conversation_id = chat1_json["conversationId"]
        first_reply = chat1_json["reply"]
        require(first_reply.get("model") == "deterministic_pantry_triage", "Eat-first response was not deterministic")
        require(food.lower() in first_reply.get("text", "").lower(), "Eat-first reply did not use the saved item")

        chat2 = session.post(f"{API}/api/fresho-buddy/chat", json={
            "conversationId": conversation_id, "message": "Why?",
        }, timeout=30)
        require(chat2.status_code == 200, f"Why chat HTTP {chat2.status_code}")
        second_reply = chat2.json()["reply"]
        require(second_reply.get("model") == "deterministic_pantry_triage", "Why response was not deterministic")
        conversation = session.get(f"{API}/api/fresho-buddy/conversations/{conversation_id}", timeout=15)
        require(conversation.status_code == 200, "Conversation history was not persisted")
        steps.append("Asked eat-first and why; both replies used deterministic DB-backed pantry triage and persisted conversation history.")

        logout = session.post(f"{API}/api/auth/logout", timeout=15)
        require(logout.status_code == 200, "Logout failed")
        session.headers.pop("Authorization", None)
        relogin = requests.post(f"{API}/api/auth/login", json={"email": email, "password": password}, timeout=15)
        require(relogin.status_code == 200, "Second login failed")
        session.headers.update({"Authorization": f"Bearer {relogin.json()['token']}"})
        history_after_login = session.get(f"{API}/api/history", timeout=15).json().get("items", [])
        persisted = any(item.get("analysisId") == analysis_id for item in history_after_login)
        require(persisted, "Pantry record did not survive logout/login")
        conv_after_login = session.get(f"{API}/api/fresho-buddy/conversations/{conversation_id}", timeout=15)
        require(conv_after_login.status_code == 200, "Chat did not survive logout/login")
        steps.append("Logged out/in again; pantry record and chat remained available.")

        session.post(f"{API}/api/auth/logout", timeout=15)
        token = None
        success = True
        error = None
    except Exception as exc:
        success = False
        error = f"{type(exc).__name__}: {exc}"
        if token:
            try:
                session.post(f"{API}/api/auth/logout", timeout=5)
            except Exception:
                pass

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# HTTP end-to-end application smoke test", "",
             f"- Result: {'PASS' if success else 'FAIL'}",
             f"- Run: `{run_id}`",
             f"- SQLite: `backend/app/database/fresho_buddy.db`",
             "- Browser automation: unavailable in this environment; this run exercises the same backend APIs and checks the frontend HTTP entry point.", "",
             "## Steps", ""]
    lines.extend(f"- {step}" for step in steps)
    if error:
        lines += ["", f"Error: `{error}`"]
    lines += ["", "No secrets or password/token values are written to this report.", ""]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print("PASS" if success else "FAIL", error or "")
    print("Report:", REPORT)
    if result:
        print(json.dumps({"food": result.get("detectedFood"), "foodForm": result.get("foodForm"),
                          "freshness": result.get("freshness"), "shelfLife": result.get("shelfLife"),
                          "modelVersions": result.get("modelVersions")}, indent=2))
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
