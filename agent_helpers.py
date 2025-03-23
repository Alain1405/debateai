from typing import Any, Dict
from colorama import Fore, Style
import textwrap

from agents import Agent, AgentHooks, RunContextWrapper, Tool

class CustomAgentHooks(AgentHooks):
    # Class-level variables to track across all agents
    total_calls = 0
    agent_counts: Dict[str, int] = {}
    total_tool_usages = 0
    agent_tool_counts: Dict[str, int] = {}

    def __init__(self, display_name: str):
        self.event_counter = 0
        self.display_name = display_name
        # Initialize this agent's counts if not already present
        if display_name not in CustomAgentHooks.agent_counts:
            CustomAgentHooks.agent_counts[display_name] = 0
        if display_name not in CustomAgentHooks.agent_tool_counts:
            CustomAgentHooks.agent_tool_counts[display_name] = 0

    def _format_message(self, sender: str, message: str) -> str:
        """Format a message with sender name and wrapped text."""
        width = 80
        wrapped_text = textwrap.fill(str(message), width=width - 4)
        indented_text = textwrap.indent(wrapped_text, "    ")
        
        # Get the speaking count for this agent
        count = CustomAgentHooks.agent_counts.get(sender, 0)
        tool_count = CustomAgentHooks.agent_tool_counts.get(sender, 0)
        
        # Format the message with speaker stats
        return f"{Fore.CYAN}{sender} (#{count}, tools: {tool_count}):{Style.RESET_ALL}\n{indented_text}\n"
    
    def _format_event(self, event_type: str, message: str) -> str:
        """Format system events."""
        return f"{Fore.YELLOW}[{event_type}]{Style.RESET_ALL} {message}"
    
    def _format_stats(self) -> str:
        """Format the overall statistics."""
        interaction_stats = f"Total agent interactions: {CustomAgentHooks.total_calls}"
        tool_stats = f"Total tool usages: {CustomAgentHooks.total_tool_usages}"
        
        # Format per-agent stats
        agent_stats = []
        for name in sorted(CustomAgentHooks.agent_counts.keys()):
            speak_count = CustomAgentHooks.agent_counts.get(name, 0)
            tool_count = CustomAgentHooks.agent_tool_counts.get(name, 0)
            agent_stats.append(f"{name}: {speak_count} (tools: {tool_count})")
        
        return f"{Fore.GREEN}[STATS] {interaction_stats} | {tool_stats} ({' | '.join(agent_stats)}){Style.RESET_ALL}"

    async def on_start(self, context: RunContextWrapper, agent: Agent) -> None:
        self.event_counter += 1
        print(self._format_event("START", f"Agent {agent.name} started"))

    async def on_end(self, context: RunContextWrapper, agent: Agent, output: Any) -> None:
        print(f"{Fore.YELLOW}{'='*40}{Style.RESET_ALL}")
        print(self._format_event("OUTPUT", f"$$$ THIs IS THE END!!!"))
        self.event_counter += 1
        
        # Increment the total calls counter
        CustomAgentHooks.total_calls += 1
        
        # Increment this agent's counter
        if agent.name in CustomAgentHooks.agent_counts:
            CustomAgentHooks.agent_counts[agent.name] += 1
        else:
            CustomAgentHooks.agent_counts[agent.name] = 1
        
        if output:
            # Show the full output content from the agent with stats
            print(self._format_message(agent.name, output))
            
        # Print the current statistics
        print(self._format_stats())
        
        print(self._format_event("END", f"Agent {agent.name} finished"))
        print(f"{Fore.YELLOW}{'='*40}{Style.RESET_ALL}")

    async def on_handoff(self, context: RunContextWrapper, agent: Agent, source: Agent) -> None:
        self.event_counter += 1
        print(self._format_event("HANDOFF", f"{source.name} handed off to {agent.name}"))

    async def on_tool_start(self, context: RunContextWrapper, agent: Agent, tool: Tool) -> None:
        self.event_counter += 1
        print(self._format_event("TOOL", f"{agent.name} using {tool.name}"))

    async def on_tool_end(
        self, context: RunContextWrapper, agent: Agent, tool: Tool, result: str
    ) -> None:
        self.event_counter += 1
        # Truncate long results for display
        result_preview = result[:150] + "..." if len(result) > 150 else result
        print(self._format_event("TOOL RESULT", f"{agent.name} received from {tool.name}:"))
        print(f"    {result_preview}")
        
        # Increment the total tool usages counter
        CustomAgentHooks.total_tool_usages += 1
        
        # Increment this agent's tool usage counter
        if agent.name in CustomAgentHooks.agent_tool_counts:
            CustomAgentHooks.agent_tool_counts[agent.name] += 1
        else:
            CustomAgentHooks.agent_tool_counts[agent.name] = 1