import json
import time

class MockLogger:
    def __init__(self):
        self.events = []
        self.start_time = time.time()
        print("🔧 MockLogger initialized")

    def log_state(self, ts, state):
        """Записывает смену состояния (CODING/RESEARCH/IDLE)"""
        event = {
            "ts": round(ts, 2),
            "type": "STATE",
            "state": state
        }
        self.events.append(event)
        print(f"📝 LOG: {event}")

    def set_summary(self, hard_score, soft_score, verdict):
        print(f"📊 SUMMARY: Hard={hard_score}, Soft={soft_score}, Verdict={verdict}")
        
    def save(self):
        with open("session_log_mock.json", "w", encoding='utf-8') as f:
            json.dump({"events": self.events}, f, indent=2)
        print("💾 Saved to session_log_mock.json")