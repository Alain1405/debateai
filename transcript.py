import datetime
from typing import List, Dict, Any, Optional
import json

class TranscriptRecorder:
    def __init__(self, output_file: Optional[str] = None):
        self.entries: List[Dict[str, Any]] = []
        self.output_file = output_file or f"debate_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    def add_entry(self, speaker: str, content: str, timestamp: Optional[float] = None):
        """Add an entry to the transcript"""
        self.entries.append({
            "speaker": speaker,
            "content": content,
            "timestamp": timestamp or datetime.datetime.now().timestamp()
        })
    
    def save(self):
        """Save the transcript to the specified file"""
        with open(self.output_file, "w") as f:
            json.dump({
                "metadata": {
                    "date": datetime.datetime.now().isoformat(),
                    "entries": len(self.entries)
                },
                "transcript": self.entries
            }, f, indent=2)
        
        print(f"Debate transcript saved to {self.output_file}")