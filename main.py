from agents import Agent, Runner
from dotenv import load_dotenv
from constants import DEBATE_CONFIGS
import uuid
import asyncio

from openai.types.responses import ResponseContentPartDoneEvent, ResponseTextDeltaEvent
from colorama import init, Fore, Style
import textwrap

from agents import Agent, RawResponsesStreamEvent, Runner, TResponseInputItem, trace
from logger import DebateLogger, LogLevel

load_dotenv()

# Initialize colorama
init()

PARTICIPANTS = 2

def format_message(speaker: str, message: str) -> str:
    """Format a message with speaker name and wrapped text."""
    width = 80
    wrapped_text = textwrap.fill(message, width=width - 4)
    indented_text = textwrap.indent(wrapped_text, "    ")
    return f"{Fore.CYAN}{speaker}:{Style.RESET_ALL}\n{indented_text}\n"


def select_debate_format():
    print("\nAvailable debate formats:")
    for i, format in enumerate(DEBATE_CONFIGS["debate_formats"], 1):
        print(f"{i}. {format['name']}: {format['best_for']}")

    while True:
        try:
            choice = int(input("\nSelect a debate format (enter number): ")) - 1
            if 0 <= choice < len(DEBATE_CONFIGS["debate_formats"]):
                return DEBATE_CONFIGS["debate_formats"][choice]
        except ValueError:
            pass
        print("Invalid selection. Please try again.")


def select_topic():
    print("\nAvailable debate topics:")
    for i, topic in enumerate(DEBATE_CONFIGS["debate_topics"], 1):
        print(f"{i}. {topic['name']}: {topic['description']}")

    while True:
        try:
            choice = int(input("\nSelect a topic (enter number): ")) - 1
            if 0 <= choice < len(DEBATE_CONFIGS["debate_topics"]):
                return DEBATE_CONFIGS["debate_topics"][choice]
        except ValueError:
            pass
        print("Invalid selection. Please try again.")


def create_moderator(debate_format, topic, debaters):
    moderator_prompt = f"""You are a debate moderator. Your role is to facilitate a discussion between {PARTICIPANTS} different personas on the topic of {topic['name']}.

The debate follows the {debate_format['name']} format: {debate_format['structure']}

Your responsibilities:
- {DEBATE_CONFIGS['moderator']['role']}
- When handing off to another participant, ALWAYS:
  1. Summarize the key points discussed so far
  2. Frame a specific question or point for them to address
  3. Provide context of who spoke before and their main arguments
- Ensure each participant gets equal speaking time
- Guide the discussion according to the {debate_format['name']} format
- Keep the conversation focused on: {topic['description']}

Format your handoffs like this:
"Summary of discussion so far: [summary]
Previous speaker [name] argued: [main points]
[Next speaker name], please address: [specific question/point]"

Your key skills:
{chr(10).join(f'- {skill}' for skill in DEBATE_CONFIGS['moderator']['skills'])}

Start by introducing the topic and format, then manage the discussion flow."""

    return Agent(
        name="Moderator",
        instructions=moderator_prompt,
        handoffs=debaters,
        handoff_description="Pass the discussion to the next participant with context.",
    )


# Get user selections
selected_topic = select_topic()
selected_format = select_debate_format()

print(f"\nDebate Topic: {selected_topic['name']}")
print(f"Debate Format: {selected_format['name']}")

prompt_template = """You are {name}, a debater with the following core beliefs:
{beliefs}

Your debate style follows this slogan: {slogan}

Key issues you care about:
{key_issues}

They say these are your blind spots: {blind_spots}

The debate will follow the {format_name} format: {format_structure}

Current debate topic: {topic}

Please engage in any debate by staying true to your persona's beliefs and characteristics but also following the debate format.
"""
debaters = []
# Define debating agents
for persona in DEBATE_CONFIGS["personas"][:PARTICIPANTS]:
    formatted_key_issues = "\n".join(f"- {issue}" for issue in persona["key_issues"])

    current_prompt = prompt_template.format(
        name=persona["name"],
        beliefs=persona["core_beliefs"],
        slogan=persona["slogan"],
        key_issues=formatted_key_issues,
        blind_spots=persona["blind_spots"],
        format_name=selected_format["name"],
        format_structure=selected_format["structure"],
        topic=selected_topic["name"],
    )

    agent = Agent(
        name=persona["name"],
        instructions=current_prompt,
    )
    # print(agent.name)
    # print(agent.instructions)
    debaters.append(agent)
    # print("Getting response")
    # result = Runner.run_sync(agent, "What are your thoughts on climate change?")
    # print(result.final_output)

# Create moderator first
moderator = create_moderator(selected_format, selected_topic, debaters)
print("\nModerator initialized:")
print(moderator.instructions)


async def main():
    # Configure logger
    logger = DebateLogger(LogLevel.INFO)  # Can be changed to DEBUG or QUIET
    
    inputs: list[TResponseInputItem] = [
        {
            "content": "Start the debate by introducing the topic and handing over the conversation.",
            "role": "user",
        }
    ]

    print(f"\n{Fore.YELLOW}=== Debate Session Started ==={Style.RESET_ALL}\n")

    while True:
        conversation_id = str(uuid.uuid4().hex[:16])
        current_response = []

        with trace("Routing example", group_id=conversation_id):
            # Debug logging of conversation history
            agent_name = result.current_agent.name if 'result' in locals() else 'Moderator'
            debug_msg = "\n".join(f"{msg.get('role', 'No role')}: {msg.get('content', 'Empty message')[:100]}..." 
                                for msg in inputs)
            logger.debug(agent_name, debug_msg)

            result = Runner.run_streamed(moderator, input=inputs)
            async for event in result.stream_events():
                if not isinstance(event, RawResponsesStreamEvent):
                    continue
                data = event.data
                if isinstance(data, ResponseTextDeltaEvent):
                    current_response.append(data.delta)
                    print(data.delta, end="", flush=True)
                elif isinstance(data, ResponseContentPartDoneEvent):
                    full_message = "".join(current_response)
                    print("\n")
                    logger.info(result.current_agent.name, full_message)
                    logger.separator()

        inputs = result.to_input_list()
        print("\n")


if __name__ == "__main__":
    asyncio.run(main())
