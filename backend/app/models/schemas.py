from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

class ActionItem(BaseModel):
    """Structured Pydantic model for single execution actions."""
    type: str
    app: Optional[str] = None
    name: Optional[str] = None
    path: Optional[str] = None
    command: Optional[str] = None
    url: Optional[str] = None
    description: Optional[str] = None

class AIPlanResponse(BaseModel):
    """Structured Pydantic model for AI plan responses."""
    response: str
    actions: List[ActionItem] = Field(default_factory=list)

class MemoryMetrics(BaseModel):
    total_gb: float
    available_gb: float
    used_gb: float
    percent: float

class DiskMetrics(BaseModel):
    total_gb: float
    free_gb: float
    percent: float

class SystemMetrics(BaseModel):
    cpu_percent: float
    memory: MemoryMetrics
    disk: DiskMetrics

class ActiveWindowInfo(BaseModel):
    title: str
    process: str

class SystemContextPayload(BaseModel):
    metrics: SystemMetrics
    active_window: ActiveWindowInfo
    running_apps: List[str] = Field(default_factory=list)
    os: str

class SpeedTestResult(BaseModel):
    ping_ms: float
    download_mbps: float
    upload_mbps: float
    summary: str
