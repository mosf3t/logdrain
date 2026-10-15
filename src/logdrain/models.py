from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class LogRecord(BaseModel):
    record_id: int
    raw_text: str
    timestamp: Optional[datetime] = None
    severity: str
    message_body: str
    thread: str
    logger_class: str
    source_line: int
    is_malformed: bool = False

class ParameterDetail(BaseModel):
    value: str
    category: str = Field(default="GENERIC", description="Category like FILE_PATH, PROGRAM_NAME, STATE, NUMERIC")
    normalized_name: Optional[str] = None

class LogAnalysisResult(BaseModel):
    record_id: int
    cluster_id: int
    template_text: str
    parameters: List[ParameterDetail]
    severity: str
    timestamp: Optional[datetime] = None
    thread: str
