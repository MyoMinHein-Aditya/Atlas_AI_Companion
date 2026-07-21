# Database Configuration & Schema — Atlas

Atlas persists its configuration state, settings, transcript history, and long-term memory facts using PostgreSQL.

---

## 1. Connection Configurations

- **Database Engine**: PostgreSQL (v15+)
- **ORM (Object Relational Mapper)**: SQLAlchemy (Python)
- **Migration Engine**: Alembic (Python)
- **Local Dev Service**: Ran via Docker container (`atlas_postgres`) on port `5432`.

The database connection URL is loaded from the environment:
`postgresql://<username>:<password>@<host>:<port>/<db_name>`

---

## 2. Relational Table Schemas

Below are the detailed column properties and associations for the core database structures.

### 2.1 Table: `sessions`
Represents an encapsulated stream of conversation between the user and Atlas.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PRIMARY KEY, Default: UUIDv4 | Unique identifier for the chat session. |
| `title` | VARCHAR(255) | Nullable | Descriptive name, auto-generated from the first message. |
| `summary` | TEXT | Nullable | Combined mid-term summary context of the chat thread. |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Date and time the session started. |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last modification date. |

### 2.2 Table: `messages`
Stores the individual message logs belonging to each session.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PRIMARY KEY, Default: UUIDv4 | Message unique identifier. |
| `session_id` | UUID | FOREIGN KEY referencing `sessions(id)` | Cascades on session deletion. |
| `sender` | VARCHAR(50) | NOT NULL, check constraint | Either `'user'` or `'atlas'`. |
| `content` | TEXT | NOT NULL | Plain-text content of the user instruction or agent response. |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Time message was recorded. |

### 2.3 Table: `memories`
Stores extracted facts and key-value preference configurations.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | INT | PRIMARY KEY, Auto-increment | Fact key index. |
| `key` | VARCHAR(100) | UNIQUE, NOT NULL | Reference tag (e.g., `'user_workspace'`, `'preferred_theme'`). |
| `value` | TEXT | NOT NULL | Associated fact content or settings data. |
| `category` | VARCHAR(50) | Nullable | Category tag for grouping (`'profile'`, `'automation'`). |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Time this fact was stored or corrected. |

---

## 3. Database Migration Strategy

We will configure Alembic to track schemas.
- **Initialization**: Run `alembic init alembic` from the `/backend` directory.
- **Migration generation**: `alembic revision --autogenerate -m "Initial schema setup"`
- **Applying changes**: Alembic updates are applied during backend startup in `backend/app/main.py` using `upgrade` programmatic command calls. This ensures database schema updates happen automatically when the local service boots.
