import json
import os
import time
import threading
import uuid
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any


# 1. Define clean data structures
@dataclass
class Event:
    ts: float
    type: str  # "STATE" or "CLARITY"
    payload: Dict[str, Any]


@dataclass
class SessionData:
    session_id: str
    candidate_id: str
    started_at: float
    events: List[Event] = field(default_factory=list)
    ended_at: Optional[float] = None
    summary: Dict[str, Any] = field(default_factory=lambda: {
        "hard_score": 0, "soft_score": 0, "verdict": "PENDING"
    })


# 2. The Logger Class
class SessionLogger:
    def __init__(self, candidate_id: str):
        self.lock = threading.Lock()  # Crucial for multithreading
        self.filepath = os.path.join("data", "session_log.json")
        os.makedirs("data", exist_ok=True)
        self.data = SessionData(
            session_id=str(uuid.uuid4()),
            candidate_id=candidate_id,
            started_at=time.time()
        )
        
        # Initial save to create the file
        self._flush()
    
    def _flush(self):
        """Internal method to write to disk. Always called under lock."""
        with open(self.filepath, 'w') as f:
            # asdict converts dataclasses to dicts automatically
            json.dump(asdict(self.data), f, indent=2)
    
    def log_state(self, state: str):
        """Called by Role 3 (Window Monitor)"""
        with self.lock:
            ts = time.time() - self.data.started_at
            event = Event(ts=round(ts, 2), type="STATE", payload={"state": state})
            self.data.events.append(event)
            self._flush()
    
    def log_clarity(self, clarity_data: dict):
        """Called by Role 2 (LLM Engine)"""
        with self.lock:
            ts = time.time() - self.data.started_at
            event = Event(ts=round(ts, 2), type="CLARITY", payload=clarity_data)
            self.data.events.append(event)
            self._flush()

    def log_event(self, event_type: str, payload: dict):
        """Generic event logger"""
        with self.lock:
            ts = time.time() - self.data.started_at
            event = Event(ts=round(ts, 2), type=event_type, payload=payload)
            self.data.events.append(event)
            self._flush()
    
    def finish_session(self, hard_score: int, soft_score: int, verdict: str):
        """Finalize the logs"""
        with self.lock:
            self.data.ended_at = time.time()
            self.data.summary = {
                "hard_score": hard_score,
                "soft_score": soft_score,
                "verdict": verdict
            }
            self._flush()

    def update_candidate_id(self, new_id: str):
        """Update the candidate ID and save to file"""
        with self.lock:
            self.data.candidate_id = new_id
            self._flush()



