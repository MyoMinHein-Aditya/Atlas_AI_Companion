import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

logger = logging.getLogger("atlas-backend")

SQLALCHEMY_DATABASE_URL = settings.computed_database_url
engine = None
SessionLocal = None

try:
    logger.info(f"Attempting connection to PostgreSQL database on {settings.db_host}:{settings.db_port}")
    # Add a connect timeout so it doesn't block startup indefinitely if Postgres is down
    connect_args = {}
    if "postgresql" in SQLALCHEMY_DATABASE_URL:
        connect_args = {"connect_timeout": 3}

    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
    
    # Force a test connection to trigger connection exceptions immediately
    with engine.connect() as conn:
        logger.info("PostgreSQL database connection established successfully.")
except Exception as e:
    logger.warning(
        f"PostgreSQL connection failed: {str(e)}. "
        "Falling back to local SQLite database for development."
    )
    # Setup fallback local SQLite DB
    sqlite_url = "sqlite:///./atlas.db"
    engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})
    logger.info(f"Fallback SQLite database initialized at: {sqlite_url}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Database session dependency injector."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
