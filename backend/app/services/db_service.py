import logging
from typing import List
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models.memory import ChatSession, ChatMessage, MemoryNode

logger = logging.getLogger("atlas-backend")

def create_session(db: Session, title: str = None) -> ChatSession:
    """Create a new chat session."""
    session = ChatSession(
        title=title or f"Chat session at {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    logger.info(f"Created new database chat session: {session.id}")
    return session

def get_session(db: Session, session_id: str) -> ChatSession:
    """Retrieve session metadata."""
    return db.query(ChatSession).filter(ChatSession.id == session_id).first()

def get_all_sessions(db: Session) -> List[ChatSession]:
    """Retrieve all chat sessions sorted by last updated."""
    return db.query(ChatSession).order_by(ChatSession.updated_at.desc()).all()

def save_message(db: Session, session_id: str, sender: str, content: str) -> ChatMessage:
    """Persist a message to the database and update session modified time."""
    message = ChatMessage(
        session_id=session_id,
        sender=sender,
        content=content
    )
    db.add(message)
    
    # Update the parent session updated_at timestamp
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if session:
        session.updated_at = datetime.now(timezone.utc)
        # If session has no title or default title, use first user prompt
        if (not session.title or "Chat session at" in session.title) and sender == "user":
            session.title = content[:30] + "..." if len(content) > 30 else content
            
    db.commit()
    db.refresh(message)
    return message

def get_session_history(db: Session, session_id: str) -> List[ChatMessage]:
    """Retrieve session message logs sorted chronologically."""
    return db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at.asc()).all()

async def consolidate_session_context(db: Session, session_id: str):
    """Consolidates long conversations into a rolling context summary."""
    try:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            return

        message_count = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).count()
        # Consolidate if conversation thread is long (e.g. > 10 messages)
        if message_count <= 10:
            return

        logger.info(f"Initiating memory context consolidation for session: {session_id}")
        messages = get_session_history(db, session_id)
        transcript = "\n".join([f"{m.sender}: {m.content}" for m in messages])

        # Import locally to avoid circular dependencies
        from app.services.ai import ai_service

        summary_prompt = (
            "Summarize the following chat conversation context between user and Atlas. "
            "Extract critical user preferences, project paths, and findings. "
            "Keep the output extremely brief and under 150 words:\n\n"
            f"{transcript}"
        )

        summary_chunks = []
        async for token in ai_service.stream_chat_tokens(summary_prompt, []):
            summary_chunks.append(token)

        summary_text = "".join(summary_chunks).strip()
        session.summary = summary_text
        db.commit()
        logger.info(f"Consolidated summary context: '{summary_text}' successfully.")
    except Exception as e:
        logger.error(f"Failed to consolidate chat context: {str(e)}")

# Memory Node Fact Helpers
def get_memory_fact(db: Session, key: str) -> str:
    node = db.query(MemoryNode).filter(MemoryNode.key == key).first()
    return node.value if node else ""

def save_memory_fact(db: Session, key: str, value: str, category: str = None) -> MemoryNode:
    node = db.query(MemoryNode).filter(MemoryNode.key == key).first()
    if node:
        node.value = value
        if category:
            node.category = category
    else:
        node = MemoryNode(key=key, value=value, category=category)
        db.add(node)
    db.commit()
    db.refresh(node)
    return node
