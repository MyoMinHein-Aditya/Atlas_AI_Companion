import sys
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app.db.base import Base
from app.services import db_service

# Setup in-memory SQLite database for sandboxed execution testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    # Setup tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Tear down tables
        Base.metadata.drop_all(bind=engine)

def test_db_session_creation(db_session):
    # Create session
    session = db_service.create_session(db_session, title="Unit Test Session")
    assert session.id is not None
    assert session.title == "Unit Test Session"
    assert session.summary is None
    
    # Query session
    fetched = db_service.get_session(db_session, session.id)
    assert fetched is not None
    assert fetched.id == session.id
    assert fetched.title == "Unit Test Session"

def test_db_message_logging(db_session):
    session = db_service.create_session(db_session)
    
    # Save user message
    msg1 = db_service.save_message(db_session, session.id, "user", "Database connection test prompt")
    assert msg1.id is not None
    assert msg1.sender == "user"
    assert msg1.content == "Database connection test prompt"
    
    # Save assistant message
    msg2 = db_service.save_message(db_session, session.id, "atlas", "Logged successfully")
    assert msg2.sender == "atlas"
    
    # Fetch history chronologically
    history = db_service.get_session_history(db_session, session.id)
    assert len(history) == 2
    assert history[0].sender == "user"
    assert history[1].sender == "atlas"

def test_db_memory_node_fact(db_session):
    # Save key-value fact
    db_service.save_memory_fact(db_session, "user_editor", "VS Code", "preferences")
    
    # Read fact
    val = db_service.get_memory_fact(db_session, "user_editor")
    assert val == "VS Code"
    
    # Update fact
    db_service.save_memory_fact(db_session, "user_editor", "Neovim")
    val_updated = db_service.get_memory_fact(db_session, "user_editor")
    assert val_updated == "Neovim"
