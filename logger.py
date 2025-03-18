from enum import Enum
import colorama
from colorama import Fore, Style
import textwrap

class LogLevel(Enum):
    DEBUG = 0
    INFO = 1
    QUIET = 2

class DebateLogger:
    def __init__(self, level: LogLevel = LogLevel.INFO):
        self.level = level
        colorama.init()
        self.width = 80
        
    def debug(self, agent_name: str, message: str):
        if self.level.value <= LogLevel.DEBUG.value:
            self._format_debug(agent_name, message)
            
    def info(self, agent_name: str, message: str):
        """Log informational messages with safe handling of agent names."""
        if self.level.value <= LogLevel.INFO.value:
            self._format_message(agent_name, message)
    
    def error(self, agent_name: str, message: str):
        """Log error messages regardless of log level."""
        wrapped = textwrap.fill(message, width=self.width - 4)
        indented = textwrap.indent(wrapped, "    ")
        print(f"{Fore.RED}ERROR - {agent_name}:{Style.RESET_ALL}\n{indented}\n")
        print(f"{Fore.RED}{'─' * self.width}{Style.RESET_ALL}")
            
    def separator(self):
        if self.level.value <= LogLevel.INFO.value:
            print(f"{Fore.YELLOW}{'─' * self.width}{Style.RESET_ALL}")
            
    def _format_debug(self, agent_name: str, message: str):
        print(f"\n{Fore.GREEN}Debug - {agent_name}:{Style.RESET_ALL}")
        wrapped = textwrap.fill(message, width=self.width - 4)
        indented = textwrap.indent(wrapped, "  ")
        print(f"{indented}\n")
        
    def _format_message(self, speaker: str, message: str):
        wrapped = textwrap.fill(message, width=self.width - 4)
        indented = textwrap.indent(wrapped, "    ")
        print(f"{Fore.CYAN}{speaker}:{Style.RESET_ALL}\n{indented}\n")