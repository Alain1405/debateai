import datetime
from typing import List, Dict, Any, Optional
import json
import os

class TranscriptRecorder:
    def __init__(self, output_file: Optional[str] = None):
        # Use the debates directory to store transcripts
        self.debates_dir = "debates"
        os.makedirs(self.debates_dir, exist_ok=True)
        
        # Create filename based on datetime if not provided
        if output_file:
            self.output_file = output_file
        else:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            self.output_file = os.path.join(self.debates_dir, f"debate_{timestamp}.json")
        
        self.entries: List[Dict[str, Any]] = []
    
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