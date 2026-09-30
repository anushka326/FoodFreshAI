# FoodFresh AI — FreshoBuddy Gemini AI Integration Report

**Date**: September 26, 2026  
**System Layer**: GENERATIVE AI & PERSISTENT DATABASE  
**LLM SDK**: Official `google-genai` (Version 2.25.0)  
**Database**: SQLite (`backend/app/database/fresho_buddy.db`)  
**Backend Routes**: [`backend/app/routes/fresho_buddy.py`](file:///d:/VIT%20TY%20SEM5/ML%20Project/FOODFRESHAI/backend/app/routes/fresho_buddy.py)  
**Backend Service**: [`backend/app/services/fresho_buddy_service.py`](file:///d:/VIT%20TY%20SEM5/ML%20Project/FOODFRESHAI/backend/app/services/fresho_buddy_service.py)  
**Frontend UI**: [`frontend/src/pages/FreshoBuddyPage/FreshoBuddyPage.jsx`](file:///d:/VIT%20TY%20SEM5/ML%20Project/FOODFRESHAI/frontend/src/pages/FreshoBuddyPage/FreshoBuddyPage.jsx)  

---

## 1. System Taxonomy & Boundary Declaration

| Component Category | Classification | Technology / Foundation | Key Responsibility |
| :--- | :--- | :--- | :--- |
| **Language Model** | **GENERATIVE AI** | Google Gemini (`gemini-2.5-flash` default) via `google-genai` | Conversational kitchen companion explaining produce care, recipes, and waste reduction. |
| **Conversation Storage** | **DATABASE LAYER** | SQLite (`fresho_buddy.db`) | Persistent conversation sessions and messages with strict user isolation. |
| **Title Generator** | **RULE ENGINE** | Deterministic Regex Token Extractor | Generates concise conversation titles without wasting LLM token calls. |

---

## 2. Architecture & Security Model

```
[React Client] (User authenticated or guest)
       │
       ▼  HTTP POST /api/fresho-buddy/chat
[FastAPI Route]
       │
       ├──> [SQLite Database] (Stores user message, links to conversation)
       │
       ├──> [FreshoBuddy Service]
       │         │
       │         ├── Reads GEMINI_API_KEY from backend environment (never exposed to client)
       │         ├── Injects FoodFresh AI System Prompt & Food Safety Policies
       │         ├── Appends structured food analysis context (Produce, Freshness, Shelf-Life, Storage)
       │         │
       │         ▼
       │    [Google Gemini API] (Generates contextual advice)
       │
       └──> [SQLite Database] (Stores assistant reply, updates conversation timestamp)
       │
       ▼
[JSON Response to Client]
```

### API Key Security Guarantee
1. `GEMINI_API_KEY` is loaded exclusively inside the Python FastAPI process from `os.environ` or `backend/.env`.
2. The key is **NEVER** embedded in frontend bundles, React components, or returned in HTTP API payloads.
3. Verification script [`scripts/test_gemini_connection.py`](file:///d:/VIT%20TY%20SEM5/ML%20Project/FOODFRESHAI/scripts/test_gemini_connection.py) demonstrates key verification without exposing the key.

### Graceful Fallback When Unconfigured
If `GEMINI_API_KEY` is missing or unconfigured:
- The backend **does not crash**.
- FreshoBuddy returns a clean, user-friendly notification:
  > *"FreshoBuddy is not configured yet. Add GEMINI_API_KEY to the backend environment."*
- If network connection to Gemini drops, client-side fallback ensures the UI remains fully responsive.

---

## 3. Database Persistence & User Isolation

Database schema implemented in `backend/app/database/chat_db.py`:

```sql
CREATE TABLE conversations (
    conversation_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX idx_conversations_user 
ON conversations(user_id, updated_at DESC);

CREATE TABLE messages (
    message_id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    analysis_context TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(conversation_id) REFERENCES conversations(conversation_id) ON DELETE CASCADE
);

CREATE INDEX idx_messages_conv 
ON messages(conversation_id, created_at ASC);
```

### Strict User Isolation
- All database queries for conversations and messages enforce `WHERE user_id = ?`.
- Users cannot access, view, or modify other users' conversations.
- Supports multi-session conversations, deletion, and chronological reload.

---

## 4. UI Capabilities (Sidebar & Context Passing)

1. **Left Sidebar / History**:
   - Organized into **Today**, **Yesterday**, and **Older** sections.
   - "+ New Chat" button allows starting fresh sessions at any time.
   - Clicking any conversation loads its complete message history.
2. **Deterministic Title Generation**:
   - First user message is converted into a clean title (e.g. *"How should I store these tomatoes?"* $\rightarrow$ **"Tomato Storage"**).
   - Zero LLM API calls wasted on title generation.
3. **Analyze Food Context Handshake**:
   - Clicking *"Ask FreshoBuddy"* on the Analyze Food page passes structured produce context (`detectedFood`, `freshness`, `shelfLife`, `storageType`, `daysStored`).
   - Context appears in a top banner with an option to *"Clear Context"*.
   - FreshoBuddy automatically references the scanned item's condition without overriding ML predictions.
