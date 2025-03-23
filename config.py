from dataclasses import dataclass
from typing import Optional
import argparse

@dataclass
class DebateConfig:
    num_participants: int = 4
    max_iterations: int = 5
    log_level: str = "INFO"
    output_file: Optional[str] = None
    
    @classmethod
    def from_args(cls):
        parser = argparse.ArgumentParser(description="Run an AI debate with multiple personas")
        parser.add_argument("--participants", type=int, default=4, help="Number of debate participants")
        parser.add_argument("--iterations", type=int, default=5, help="Maximum number of debate turns")
        parser.add_argument("--log-level", choices=["DEBUG", "INFO", "QUIET"], default="INFO", help="Logging verbosity")
        parser.add_argument("--output", type=str, help="File to save debate transcript")
        
        args = parser.parse_args()
        
        return cls(
            num_participants=args.participants,
            max_iterations=args.iterations,
            log_level=args.log_level,
            output_file=args.output
        )