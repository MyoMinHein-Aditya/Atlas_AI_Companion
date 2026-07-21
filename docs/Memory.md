# Memory System Architecture — Atlas

Atlas utilizes a database-centered relational memory layer stored in PostgreSQL. We have excluded ChromaDB to keep the database stack clean and leverage PostgreSQL's robust query capabilities.

---

## 1. Memory Tier Overview

Memory is divided into three tiers based on retrieval latency and operational scope:

```text
+------------------------------------------------------------+
| 1. Active Chat Session Context (RAM - Last 15-20 Messages)  |
+------------------------------------------------------------+
                             |
                             v (Exceeds Token Limit)
+------------------------------------------------------------+
| 2. Rolling Context Summaries (PostgreSQL `sessions.summary`)|
+------------------------------------------------------------+
                             |
                             v (Periodically Extracted)
+------------------------------------------------------------+
| 3. Long-Term Facts & Profile Settings (PostgreSQL `memories`)|
+------------------------------------------------------------+
```

### 1.1 Active Chat Session Context (Short-Term)
- **Scope**: The immediate thread of conversation.
- **Handling**: Held in Python backend application memory during the active session. Sent directly in the prompt payload to Gemini/Groq.

### 1.2 Rolling Context Summaries (Mid-Term)
- **Scope**: Summarized state of long chats.
- **Handling**: When messages in a session cross a token threshold (e.g., 4000 tokens), an background task triggers an LLM summarization call. The summary is written to the database (`sessions` table) and injected as system instructions, freeing up active context tokens.

### 1.3 Long-Term Fact Store (Long-Term)
- **Scope**: Permanent user metadata, file paths, tool configuration histories, and personal preferences.
- **Handling**: An extraction agent evaluates finished sessions to deduce declarative facts (e.g., "User's favorite text editor is VS Code", "Workspace path is d:/Projects/Atlas"). These facts are persisted in the `memories` table and retrieved during boot.

---

## 2. PostgreSQL Schema Draft for Memory

```sql
-- Represents an individual chat session
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    summary TEXT -- stores the rolling context summary
);

-- Stores individual message turns
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    sender VARCHAR(50) NOT NULL, -- 'user' or 'atlas'
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Stores extracted long-term facts
CREATE TABLE memories (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100) UNIQUE NOT NULL, -- e.g., 'workspace_path' or 'user_name'
    value TEXT NOT NULL,
    category VARCHAR(50), -- 'preferences', 'system_path', 'profile'
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

---

## 3. Memory Consolidation Workflow

1. **Trigger**: Every 10 user message exchanges, check if the current active message payload exceeds the window size.
2. **Execution**:
   - Send the message list to the LLM with a consolidation prompt.
   - Update the database `sessions.summary` with the new text.
   - Clear older database records from local active memory list (the database retains the message history in the `messages` table for UI scrolling, but they are excluded from current LLM API payloads).
3. **Boot Injection**: When Atlas starts up, the backend loads the key preferences from the `memories` table and prepends them as permanent instruction context.
