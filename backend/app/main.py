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

# Import Automation & Vision Services
from app.services.executor import execute_command, is_command_safe
from app.services.automation import take_screenshot, mouse_click, keyboard_type, keyboard_press
from app.services.browser import browser_service
from app.services.vision import vision_service
from app.services.system import system_service

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
                
                # 2. Persist user prompt to DB
                db_service.save_message(db, session_id, "user", prompt)
                
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
                
                # 6. Execute actions pipeline sequentially
                step_idx = 2
                plan_halted = False
                
                for action in actions:
                    if plan_halted:
                        break
                        
                    action_type = action.get("type")
                    
                    if action_type == "wifi_speed":
                        await websocket.send_json({
                            "type": "execution_status",
                            "step": step_idx,
                            "status": "RUNNING",
                            "description": "Measuring real-time WiFi / Network speed..."
                        })
                        speed_res = await system_service.run_speed_test()
                        summary = speed_res.get("summary", "Network test completed.")
                        await websocket.send_json({
                            "type": "execution_status",
                            "step": step_idx,
                            "status": "SUCCESS",
                            "description": summary
                        })
                        
                        # Dispatch Action Completion Message into chat thread
                        completed_msg = f"Network Speed Test Completed — {summary}"
                        await websocket.send_json({
                            "type": "chat_token",
                            "token": f"\n\n[Action Completed]: {completed_msg}"
                        })
                        db_service.save_message(db, session_id, "atlas", f"[Action Completed]: {completed_msg}")

                    elif action_type == "open_app":
                        app_name = action.get("app", "")
                        await websocket.send_json({
                            "type": "execution_status",
                            "step": step_idx,
                            "status": "RUNNING",
                            "description": f"Opening system application: {app_name}"
                        })
                        result_msg = system_service.launch_system_app(app_name)
                        await websocket.send_json({
                            "type": "execution_status",
                            "step": step_idx,
                            "status": "SUCCESS",
                            "description": result_msg
                        })
                        
                        # Dispatch Action Completion Message into chat thread
                        await websocket.send_json({
                            "type": "chat_token",
                            "token": f"\n\n[Action Completed]: {result_msg}"
                        })
                        db_service.save_message(db, session_id, "atlas", f"[Action Completed]: {result_msg}")

                    elif action_type == "focus_app":
                        name_query = action.get("name", "")
                        await websocket.send_json({
                            "type": "execution_status",
                            "step": step_idx,
                            "status": "RUNNING",
                            "description": f"Bringing open window '{name_query}' into view..."
                        })
                        success = system_service.focus_window_by_name(name_query)
                        status = "SUCCESS" if success else "ERROR"
                        msg = f"Window '{name_query}' brought to view." if success else f"No window matching '{name_query}' found."
                        await websocket.send_json({
                            "type": "execution_status",
                            "step": step_idx,
                            "status": status,
                            "description": msg
                        })
                        
                        # Dispatch Action Completion Message into chat thread
                        await websocket.send_json({
                            "type": "chat_token",
                            "token": f"\n\n[Action Completed]: {msg}"
                        })
                        db_service.save_message(db, session_id, "atlas", f"[Action Completed]: {msg}")

                    elif action_type == "shell":
                        command = action.get("command", "")
                        is_safe_launch = command.strip().lower().startswith("start ") or is_command_safe(command)
                        
                        # Auto-approve safe app launch commands starting with 'start '
                        if is_safe_launch and command.strip().lower().startswith("start "):
                            await websocket.send_json({
                                "type": "execution_status",
                                "step": step_idx,
                                "status": "RUNNING",
                                "description": f"Running: {command}"
                            })
                            output = await execute_command(command)
                            await websocket.send_json({
                                "type": "execution_status",
                                "step": step_idx,
                                "status": "SUCCESS",
                                "description": f"Output:\n{output}"
                            })
                        else:
                            # Trigger Security Consent Prompt for other shell commands
                            await websocket.send_json({
                                "type": "approval_required",
                                "command": command,
                                "step": step_idx
                            })
                            
                            # Wait for client response
                            approved = False
                            while True:
                                client_response = await websocket.receive_json()
                                if client_response.get("type") == "approval_response":
                                    approved = client_response.get("approved", False)
                                    break
                                    
                            if approved:
                                await websocket.send_json({
                                  "type": "execution_status",
                                  "step": step_idx,
                                  "status": "RUNNING",
                                  "description": f"Running: {command}"
                                })
                                
                                output = await execute_command(command)
                                
                                await websocket.send_json({
                                  "type": "execution_status",
                                  "step": step_idx,
                                  "status": "SUCCESS",
                                  "description": f"Output:\n{output}"
                                })
                            else:
                                await websocket.send_json({
                                  "type": "execution_status",
                                  "step": step_idx,
                                  "status": "ERROR",
                                  "description": "Script execution denied by user."
                                })
                                plan_halted = True
                            
                    elif action_type == "screenshot":
                        await websocket.send_json({
                          "type": "execution_status",
                          "step": step_idx,
                          "status": "RUNNING",
                          "description": "Capturing active desktop screenshot..."
                        })
                        
                        png_bytes = take_screenshot()
                        os.makedirs("assets", exist_ok=True)
                        with open("assets/screenshot.png", "wb") as f:
                            f.write(png_bytes)
                            
                        await websocket.send_json({
                          "type": "execution_status",
                          "step": step_idx,
                          "status": "SUCCESS",
                          "description": "Screen captured successfully and saved to assets/screenshot.png"
                        })
                        
                    elif action_type == "browser":
                        url = action.get("url", "")
                        await websocket.send_json({
                          "type": "execution_status",
                          "step": step_idx,
                          "status": "RUNNING",
                          "description": f"Launching Chromium browser to open: {url}"
                        })
                        
                        await browser_service.navigate_to(url)
                        text = await browser_service.scrape_text()
                        await browser_service.close()
                        
                        await websocket.send_json({
                          "type": "execution_status",
                          "step": step_idx,
                          "status": "SUCCESS",
                          "description": f"Loaded page. Scraped {len(text)} characters of text."
                        })
                        
                    elif action_type == "click_element":
                        description = action.get("description", "")
                        await websocket.send_json({
                          "type": "execution_status",
                          "step": step_idx,
                          "status": "RUNNING",
                          "description": f"Locating coordinates for element: '{description}'"
                        })
                        
                        png_bytes = take_screenshot()
                        coords = await vision_service.locate_element(png_bytes, description)
                        
                        if coords:
                            x, y = coords
                            await websocket.send_json({
                              "type": "execution_status",
                              "step": step_idx,
                              "status": "RUNNING",
                              "description": f"Moving cursor and clicking coordinates: ({x}, {y})"
                            })
                            mouse_click(x, y)
                            await websocket.send_json({
                              "type": "execution_status",
                              "step": step_idx,
                              "status": "SUCCESS",
                              "description": f"Successfully clicked ({x}, {y}) for element: '{description}'"
                            })
                        else:
                            await websocket.send_json({
                              "type": "execution_status",
                              "step": step_idx,
                              "status": "ERROR",
                              "description": f"Could not locate pixel coordinate for: '{description}'"
                            })
                            plan_halted = True
                            
                    elif action_type == "read_screen_text":
                        await websocket.send_json({
                          "type": "execution_status",
                          "step": step_idx,
                          "status": "RUNNING",
                          "description": "Analyzing screen layout for text extraction (OCR)..."
                        })
                        
                        png_bytes = take_screenshot()
                        ocr_text = await vision_service.analyze_screenshot(
                            png_bytes, "List all readable text visible on this computer screen."
                        )
                        
                        # Yield text directly to user bubble
                        await websocket.send_json({
                            "type": "chat_token",
                            "token": f"\n\n[Screen Text OCR Output]:\n{ocr_text}\n"
                        })
                        
                        await websocket.send_json({
                          "type": "execution_status",
                          "step": step_idx,
                          "status": "SUCCESS",
                          "description": "Completed screen text extraction."
                        })
                        
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
