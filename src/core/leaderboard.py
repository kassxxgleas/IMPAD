import json
import os
import time
from typing import List, Dict, Any
from dataclasses import dataclass, asdict

@dataclass
class LeaderboardEntry:
    name: str
    timestamp: float
    hard_score: int
    soft_score: int
    total_score: float
    ai_overview: str
    code_content: str

class Leaderboard:
    def __init__(self, filepath: str = "data/leaderboard.json"):
        self.filepath = filepath
        self.entries: List[LeaderboardEntry] = []
        self._load()

    def _load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    data = json.load(f)
                    self.entries = [LeaderboardEntry(**entry) for entry in data]
            except (json.JSONDecodeError, TypeError):
                print(f"[Leaderboard] Warning: Could not load {self.filepath}. Starting fresh.")
                self.entries = []
        else:
            self.entries = []

    def save(self):
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        with open(self.filepath, 'w') as f:
            json.dump([asdict(e) for e in self.entries], f, indent=2)

    def add_entry(self, name: str, hard_score: int, soft_score: int, ai_overview: str, code_content: str):
        total_score = (hard_score + soft_score) / 2
        entry = LeaderboardEntry(
            name=name,
            timestamp=time.time(),
            hard_score=hard_score,
            soft_score=soft_score,
            total_score=total_score,
            ai_overview=ai_overview,
            code_content=code_content
        )
        self.entries.append(entry)
        # Sort by total score descending
        self.entries.sort(key=lambda x: x.total_score, reverse=True)
        self.save()
        print(f"[Leaderboard] Entry added for {name}!")

    def display(self, top_n: int = 5):
        print("\n" + "="*60)
        print(f"{'RANK':<5} | {'NAME':<20} | {'HARD':<5} | {'SOFT':<5} | {'TOTAL':<5}")
        print("-" * 60)
        for i, entry in enumerate(self.entries[:top_n]):
            print(f"{i+1:<5} | {entry.name:<20} | {entry.hard_score:<5} | {entry.soft_score:<5} | {entry.total_score:<5.1f}")
        print("="*60 + "\n")
