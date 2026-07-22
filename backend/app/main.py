import logging
import os
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import settings
from app.services.ai import ai_service
from app.db.base import Base
from app.db.session import engine, SessionLocal, get_db
from app.models.memory import ChatSession, ChatMessage, MemoryNode
from app.services import db_service

from app.services.system import system_service
from app.services.actions import action_dispatcher

# Setup logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("atlas-backend")


# Create database tables automatically
try:
    logger.info("Initializing database schema tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialization completed.")
except Exception as e:
    logger.error(f"Failed to auto-create database tables: {str(e)}")

app = FastAPI(
    title="Atlas Core Backend",
    description="Local system engine and AI coordinator for Atlas companion.",
    version="0.1.0"
)

# CORS configurations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify electron and local origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to Atlas Local Core API. Navigate to /health or /docs."}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "version": "0.1.0",
        "env": settings.python_env,
        "database": "connected"
    }

@app.get("/api/system/context")
async def get_system_context():
    """Retrieve current OS resource metrics and active window title."""
    return system_service.get_system_context()

@app.get("/api/sessions")
def list_sessions(db: Session = Depends(get_db)):
    """Retrieve all conversational sessions."""
    sessions = db_service.get_all_sessions(db)
    return [
        {
            "id": s.id,
            "title": s.title,
            "summary": s.summary,
            "created_at": s.created_at.isoformat(),
            "updated_at": s.updated_at.isoformat()
        }
        for s in sessions
    ]

@app.get("/api/sessions/{session_id}/messages")
def get_session_messages(session_id: str, db: Session = Depends(get_db)):
    """Retrieve chronologically sorted messages for a session."""
    messages = db_service.get_session_history(db, session_id)
    return [
        {
            "id": m.id,
            "sender": m.sender,
            "content": m.content,
            "created_at": m.created_at.isoformat()
        }
        for m in messages
    ]

@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection established from UI.")
    
    # Establish standalone local db session for this socket connection
    db = SessionLocal()
    
    try:
        # Send greeting event
        await websocket.send_json({
            "type": "chat_token",
            "token": "Atlas system operational. Ready for instructions."
        })
        
        while True:
            # Wait for messages from the React frontend
            data = await websocket.receive_json()
            logger.info(f"Received WebSocket event: {data}")
            
            message_type = data.get("type")
            if message_type == "text_prompt":
                prompt = data.get("content", "")
                session_id = data.get("session_id")
                history = data.get("history", [])
                
                # 1. Resolve active session
                if not session_id:
                    session = db_service.create_session(db)
                    session_id = session.id
                    await websocket.send_json({
                        "type": "session_created",
                        "session_id": session_id
                    })
                else:
                    session = db_service.get_session(db, session_id)
                    if not session:
                        session = db_service.create_session(db)
                        session_id = session.id
                        await websocket.send_json({
                            "type": "session_created",
                            "session_id": session_id
                        })
                
                # 2. Persist user prompt to DB and load full session history
                db_service.save_message(db, session_id, "user", prompt)
                
                # Retrieve full session history directly from database
                db_messages = db_service.get_session_history(db, session_id)
                history = [{"sender": m.sender, "content": m.content} for m in db_messages[:-1]]

                # Attach real-time system state (active window, processes, metrics, battery)
                realtime_sys = system_service.get_system_context()
                sys_context_str = f"[Real-Time System Context]: Active Window: '{realtime_sys['active_window']['title']}', Running Apps: {', '.join(realtime_sys['running_apps'][:5])}, Battery: {realtime_sys['battery']['percent']}% (Plugged: {realtime_sys['battery']['power_plugged']})"
                history.insert(0, {"sender": "atlas", "content": sys_context_str})

                # Send running status to UI
                await websocket.send_json({
                  "type": "execution_status",
                  "step": 1,
                  "status": "RUNNING",
                  "description": "Formulating execution plan..."
                })
                
                # Prepend rolling summary context if it exists
                if session.summary:
                    history.insert(0, {
                        "sender": "atlas",
                        "content": f"[Memory Context Summary]: {session.summary}"
                    })
                
                # 3. Generate action plan JSON from AI
                plan = await ai_service.generate_response_and_plan(prompt, history)
                response_text = plan.get("response", "")
                actions = plan.get("actions", [])
                
                # Send success status for planning
                await websocket.send_json({
                  "type": "execution_status",
                  "step": 1,
                  "status": "SUCCESS",
                  "description": "Plan formulated successfully."
                })
                
                # 4. Stream conversational response
                for token in response_text.split(" "):
                    await websocket.send_json({
                        "type": "chat_token",
                        "token": token + " "
                    })
                    await asyncio.sleep(0.005)
                
                # 5. Save Atlas response to DB
                db_service.save_message(db, session_id, "atlas", response_text)
                
                # 6. Execute actions pipeline sequentially using ActionDispatcher
                step_idx = 2
                plan_halted = False
                
                for action in actions:
                    if plan_halted:
                        break
                    
                    action_type = action.get("type", "action")
                    await websocket.send_json({
                        "type": "execution_status",
                        "step": step_idx,
                        "status": "RUNNING",
                        "description": f"Executing action: {action_type}"
                    })

                    success, result_msg = await action_dispatcher.dispatch(action, websocket, step_idx, session_id, db)
                    status = "SUCCESS" if success else "ERROR"

                    await websocket.send_json({
                        "type": "execution_status",
                        "step": step_idx,
                        "status": status,
                        "description": result_msg
                    })

                    # Dispatch Action Completion Message into chat thread
                    await websocket.send_json({
                        "type": "chat_token",
                        "token": f"\n\n[Action Completed]: {result_msg}"
                    })
                    db_service.save_message(db, session_id, "atlas", f"[Action Completed]: {result_msg}")

                    if not success:
                        plan_halted = True

                    step_idx += 1
                
                # 7. Consolidate chat session context if long
                await db_service.consolidate_session_context(db, session_id)
                
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unsupported event type: {message_type}"
                })
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected.")
    except Exception as e:
        logger.error(f"WebSocket communication error: {str(e)}")
    finally:
        db.close()
