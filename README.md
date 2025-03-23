# DebateAI: Multi-Agent AI Debate Simulation Platform

## Project Description

DebateAI is a sophisticated platform that orchestrates structured debates between multiple AI agents, each representing different political and ideological perspectives. The system creates a dynamic, interactive environment where these personas can engage in meaningful discourse on various controversial topics.

This project explores how artificial intelligence can simulate complex social interactions and different viewpoints, potentially offering insights into human discourse and deliberation. By enabling AI agents with distinct ideological frameworks to debate contentious topics, DebateAI examines:

- How differing perspectives can be represented by AI models
- Whether AI can generate nuanced arguments across the political spectrum
- How biases manifest in multi-agent AI conversations
- The effectiveness of different debate formats in facilitating productive discourse
- The potential for AI to serve as a tool for exploring complex social and political issues

## Core Architecture
The project uses the OpenAI Agents framework to create a multi-agent system with:

Multiple Debater Agents: Each agent has a distinct persona (constants.py defines 10 personas like "Progressive Activist", "Libertarian Individualist", etc.) with unique:

Core beliefs
Rhetorical style (represented by a slogan)
Key issues they focus on
Inherent blind spots/biases
Moderator Agent: Oversees the debate, facilitates turn-taking, provides summaries, and ensures all perspectives are heard by managing handoffs between debater agents.

Debate Structure: Supports four debate formats (constants.py):

Socratic Dialogue
Fishbowl Discussion
Iron Man Debate
Mediated Dialogue
Web Search Capability: Debater agents can perform web searches to support their arguments with real-world data.

## Key Components
main.py: Entry point that initializes the debate, handles agent creation, and manages the flow of conversation
constants.py: Contains configurations for debate personas, formats, topics, and moderator functionality
agent_helpers.py: Implements the custom tracking and display hooks for agent interactions
logger.py: Provides formatted logging with different verbosity levels

## Technical Features
Agent Hooks System: The CustomAgentHooks class tracks and displays:

Total agent interactions
Per-agent interaction counts
Tool usage statistics
Formatted messages with colored output
Interactive Selection: Users can select debate topics and formats at runtime

Structured Agent Communication: The moderator ensures orderly transitions between speakers with proper context

Tool Usage: Agents can use web searches to support their arguments with factual information

## Future Development Plans

RAG (Retrieval-Augmented Generation) for shared long-term memory
Individual RAG systems for each agent's memory and external information
Summarization for short-term memory
Biased memory querying (agents query long-term memory through their ideological lens)
Periodic memory regeneration
Additional tools for memory and internet access

## Research Goals

The project aims to test:

- How AI agents exhibit biases
- AI agents' ability to generate novel information
- Advanced RAG systems with memory capabilities
- Incremental knowledge development through debate

TODO:

- Rag for long shared long term memory
- Indivudal Rag for each agent for external info and debate memory
- Summary for short term memory
- Every agents query the long term memory on their own terms (bias)
- Every now and then we take a break and recreate the long term memory
- Tool for:
  - Access memory
  - Access internet

What we test:
- Biases
- Can AI agents generate info
- Advanced RAGs with memory
- Incremental knowledge