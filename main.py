from agents import Agent, Runner, WebSearchTool
from dotenv import load_dotenv
from constants import DEBATE_CONFIGS
import uuid
import asyncio

from openai.types.responses import ResponseContentPartDoneEvent, ResponseTextDeltaEvent
from colorama import init, Fore, Style

from agents import Agent, RawResponsesStreamEvent, Runner, TResponseInputItem, trace
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from agent_helpers import CustomAgentHooks
from pydantic import BaseModel

load_dotenv()

# Initialize colorama
init()

PARTICIPANTS = 4

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
The objective of the debate is to explore different perspectives and arguments on the topic, find common ground and clarify the key points of contention and how they relate to key differences in values.

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

Start by introducing the topic and format, then manage the discussion flow. 
When the conversation is complete, after at least 5 to 10 rounds, provide a summary of the key points discussed and any areas of agreement or disagreement and then stop."""

    return Agent(
        name="Moderator",
        instructions=moderator_prompt,
        handoffs=debaters,
        handoff_description="Pass the discussion to the next participant with context.",
        hooks=CustomAgentHooks(display_name="Moderator"),
        output_type=FinalResult,
    )

class FinalResult(BaseModel):
    summary: str

# Get user selections
selected_topic = select_topic()
selected_format = select_debate_format()

print(f"\nDebate Topic: {selected_topic['name']}")
print(f"Debate Format: {selected_format['name']}")

prompt_template = """You are {name}, you are participating in a debate. Your core beliefs are:
{beliefs}

Your debate style follows this slogan: {slogan}

Key issues you care about:
{key_issues}

These are your blind spots: {blind_spots}

The debate will follow the {format_name} format: {format_structure}.

Current debate topic: {topic}

Please engage in any debate by staying true to your persona's beliefs and characteristics but also following the debate format.
The objective of the debate is to explore different perspectives and arguments on the topic, find common ground and clarify the key points of contention and how they relate to key differences in values.
Your tone is in line with your persona. 
You want your arguments to be based on facts and logic, and for that you have 2 web searches available to use during the debate. Your searches should be biased by your believes, relevant to the topic and help you make a stronger argument. Reference the source of your data when using it.
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
        instructions=f"{RECOMMENDED_PROMPT_PREFIX}: {current_prompt}",
        tools=[WebSearchTool()],
        hooks=CustomAgentHooks(display_name=persona["name"]),
    )
    debaters.append(agent)

# Create moderator first
moderator = create_moderator(selected_format, selected_topic, debaters)
print("\nModerator initialized:")
print(moderator.instructions)


async def main():
    inputs: list[TResponseInputItem] = [
        {
            "content": "Start the debate by introducing the topic and handing over the conversation.",
            "role": "user",
        }
    ]

    print(f"\n{Fore.YELLOW}=== Debate Session Started ==={Style.RESET_ALL}\n")

    # Add maximum iterations to prevent infinite loops
    max_iterations = 50
    iteration_count = 0

    while iteration_count < max_iterations:
        iteration_count += 1
        conversation_id = str(uuid.uuid4().hex[:16])

        with trace("Routing example", group_id=conversation_id):
            # Run the agent - output will be handled by hooks
            result = Runner.run_streamed(moderator, input=inputs)
            async for event in result.stream_events():
                # We don't need to process output here as hooks will handle it
                pass

        inputs = result.to_input_list()

        # Add feedback about remaining iterations
        if iteration_count == max_iterations:
            print(f"\n{Fore.RED}Debate reached the maximum of {max_iterations} turns and will now end.{Style.RESET_ALL}")

    print(f"\n{Fore.YELLOW}=== Debate Session Ended ==={Style.RESET_ALL}")


if __name__ == "__main__":
    asyncio.run(main())
