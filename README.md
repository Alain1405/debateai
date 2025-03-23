# DebateAI: Multi-Agent AI Debate Simulation Platform

## Project Description

DebateAI is a sophisticated platform that orchestrates structured debates between multiple AI agents, each representing different political and ideological perspectives. The system creates a dynamic, interactive environment where these personas can engage in meaningful discourse on various controversial topics.

This project explores how artificial intelligence can simulate complex social interactions and different viewpoints, potentially offering insights into human discourse and deliberation. By enabling AI agents with distinct ideological frameworks to debate contentious topics, DebateAI examines:

- How differing perspectives can be represented by AI models
- Whether AI can generate nuanced arguments across the political spectrum
- How biases manifest in multi-agent AI conversations
- The effectiveness of different debate formats in facilitating productive discourse
- The potential for AI to serve as a tool for exploring complex social and political issues

## Setup Instructions

### Prerequisites
- Python 3.10 or higher
- Poetry (dependency management tool))

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/Alain1405/debateai.git
   cd debateai
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Create a `.env` file with your API keys (use .env.example as template):with your API keys (use .env.example as template):
   ```bash
   cp .env.example .enve .env
   # Then edit .env and add your actual API keyhen edit .env and add your actual API key
   ```   ```

### Running a Debateg a Debate

To start a new debate:rt a new debate:

```bash
# Activate the Poetry environment
eval $(poetry2 env activate)  # For Poetry 2
# OR
poetry shell  # For Poetry 1

# Run the main scripthe main script
python main.py
```

Options:
- `--participants N`: Set the number of participants (default: 4)- `--participants N`: Set the number of participants (default: 4)
- `--iterations N`: Maximum number of debate turns (default: 5)aximum number of debate turns (default: 5)
- `--output-dir DIR`: Directory for Jekyll blog posts (default: _posts)r DIR`: Directory for Jekyll blog posts (default: _posts)
- `--no-blog`: Disable Jekyll blog post creation--no-blog`: Disable Jekyll blog post creation

## Core ArchitectureArchitecture
The project uses the OpenAI Agents framework to create a multi-agent system with:ent system with:

Multiple Debater Agents: Each agent has a distinct persona (constants.py defines 10 personas like "Progressive Activist", "Libertarian Individualist", etc.) with unique:y defines 10 personas like "Progressive Activist", "Libertarian Individualist", etc.) with unique:

Core beliefsCore beliefs
Rhetorical style (represented by a slogan)presented by a slogan)
Key issues they focus on
Inherent blind spots/biasesInherent blind spots/biases
Moderator Agent: Oversees the debate, facilitates turn-taking, provides summaries, and ensures all perspectives are heard by managing handoffs between debater agents.

Debate Structure: Supports four debate formats (constants.py):ture: Supports four debate formats (constants.py):

Socratic Dialogue
Fishbowl Discussion
Iron Man Debate
Mediated DialogueMediated Dialogue
Web Search Capability: Debater agents can perform web searches to support their arguments with real-world data. to support their arguments with real-world data.

## Key Components
main.py: Entry point that initializes the debate, handles agent creation, and manages the flow of conversationt that initializes the debate, handles agent creation, and manages the flow of conversation
constants.py: Contains configurations for debate personas, formats, topics, and moderator functionalityontains configurations for debate personas, formats, topics, and moderator functionality
agent_helpers.py: Implements the custom tracking and display hooks for agent interactions Implements the custom tracking and display hooks for agent interactions
logger.py: Provides formatted logging with different verbosity levels

## Technical Featuresures
Agent Hooks System: The CustomAgentHooks class tracks and displays:

Total agent interactions
Per-agent interaction counts
Tool usage statisticsTool usage statistics
Formatted messages with colored outputth colored output
Interactive Selection: Users can select debate topics and formats at runtimet runtime

Structured Agent Communication: The moderator ensures orderly transitions between speakers with proper contextcation: The moderator ensures orderly transitions between speakers with proper context

Tool Usage: Agents can use web searches to support their arguments with factual informationn use web searches to support their arguments with factual information

## Automated Debate Generation

The project includes a GitHub Actions workflow that automatically generates a new debate daily and publishes the results. The workflow:he results. The workflow:

1. Runs at 12:00 UTC daily (can also be triggered manually)
2. Generates a new debate using a random or predefined topic2. Generates a new debate using a random or predefined topic
3. Creates Jekyll-formatted posts in the `_posts` directorysts in the `_posts` directory
4. Commits and pushes the debate transcript to the repository4. Commits and pushes the debate transcript to the repository

## Future Development Plans## Future Development Plans

RAG (Retrieval-Augmented Generation) for shared long-term memorymory
Individual RAG systems for each agent's memory and external information information
Summarization for short-term memory
Biased memory querying (agents query long-term memory through their ideological lens)Biased memory querying (agents query long-term memory through their ideological lens)
Periodic memory regenerationn
Additional tools for memory and internet accessAdditional tools for memory and internet access

## Research Goals

The project aims to test:

- How AI agents exhibit biases
- AI agents' ability to generate novel information- AI agents' ability to generate novel information
- Advanced RAG systems with memory capabilitiesstems with memory capabilities
- Incremental knowledge development through debate- Incremental knowledge development through debate

TODO:TODO:

- Rag for long shared long term memory
- Indivudal Rag for each agent for external info and debate memoryo and debate memory
- Summary for short term memory
- Every agents query the long term memory on their own terms (bias)- Every agents query the long term memory on their own terms (bias)
- Every now and then we take a break and recreate the long term memoryry now and then we take a break and recreate the long term memory
- Tool for:- Tool for:
  - Access memory
  - Access internet

What we test:
- Biases
- Can AI agents generate infoents generate info
- Advanced RAGs with memoryith memory
- Incremental knowledge