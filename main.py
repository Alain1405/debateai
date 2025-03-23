import asyncio
import argparse
import os
import json
from colorama import init
from dotenv import load_dotenv
from datetime import datetime

from constants import DEBATE_CONFIGS
from debate import Debate

# Initialize colorama and load environment variables
init()
load_dotenv()

# Path to store the last debate info
DEBATE_STATE_FILE = "debates/debate_state.json"

def select_debate_format(non_interactive=False, default_format=None):
    if non_interactive:
        if default_format is not None:
            # Use the specified default format
            for format in DEBATE_CONFIGS["debate_formats"]:
                if format["name"].lower() == default_format.lower():
                    return format
            # If not found, use the first format
            return DEBATE_CONFIGS["debate_formats"][0]
        else:
            # Use the first format in the list
            return DEBATE_CONFIGS["debate_formats"][0]
    
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


def select_topic(non_interactive=False, last_topic_index=None):
    if non_interactive:
        next_index = 0
        if last_topic_index is not None:
            # Select the next topic (cycling through the list)
            next_index = (last_topic_index + 1) % len(DEBATE_CONFIGS["debate_topics"])
        return DEBATE_CONFIGS["debate_topics"][next_index], next_index
    
    print("\nAvailable debate topics:")
    for i, topic in enumerate(DEBATE_CONFIGS["debate_topics"], 1):
        print(f"{i}. {topic['name']}: {topic['description']}")

    while True:
        try:
            choice = int(input("\nSelect a topic (enter number): ")) - 1
            if 0 <= choice < len(DEBATE_CONFIGS["debate_topics"]):
                return DEBATE_CONFIGS["debate_topics"][choice], choice
        except ValueError:
            pass
        print("Invalid selection. Please try again.")

def load_debate_state():
    """Load the previous debate state from file"""
    try:
        if os.path.exists(DEBATE_STATE_FILE):
            with open(DEBATE_STATE_FILE, 'r') as f:
                return json.load(f)
        return {"last_topic_index": None, "last_run_date": None}
    except Exception as e:
        print(f"Error loading debate state: {e}")
        return {"last_topic_index": None, "last_run_date": None}

def save_debate_state(topic_index):
    """Save the current debate state to file"""
    os.makedirs(os.path.dirname(DEBATE_STATE_FILE), exist_ok=True)
    try:
        with open(DEBATE_STATE_FILE, 'w') as f:
            json.dump({
                "last_topic_index": topic_index,
                "last_run_date": datetime.now().strftime("%Y-%m-%d")
            }, f)
    except Exception as e:
        print(f"Error saving debate state: {e}")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Run an AI debate simulation")
    parser.add_argument("--participants", type=int, default=4, help="Number of debate participants (default: 4)")
    parser.add_argument("--iterations", type=int, default=5, help="Maximum number of debate turns (default: 5)")
    parser.add_argument("--output-dir", type=str, default="_posts", help="Directory for Jekyll blog posts (default: _posts)")
    parser.add_argument("--no-blog", action="store_true", help="Disable Jekyll blog post creation")
    parser.add_argument("--non-interactive", action="store_true", help="Run without user input (for CI/CD)")
    parser.add_argument("--default-format", type=str, help="Default debate format to use in non-interactive mode")
    
    return parser.parse_args()

async def main():
    # Parse command-line arguments
    args = parse_arguments()
    
    # Check if running in GitHub Actions
    in_github_actions = os.environ.get('GITHUB_ACTIONS') == 'true'
    non_interactive = args.non_interactive or in_github_actions
    
    # If in non-interactive mode, load previous state
    debate_state = {}
    if non_interactive:
        debate_state = load_debate_state()
        print(f"Running in non-interactive mode. Last topic index: {debate_state['last_topic_index']}")
    
    # Get selections based on mode
    selected_topic, topic_index = select_topic(non_interactive, debate_state.get("last_topic_index"))
    selected_format = select_debate_format(non_interactive, args.default_format)

    print(f"\nDebate Topic: {selected_topic['name']}")
    print(f"Debate Format: {selected_format['name']}")
    
    # Create output directories if they don't exist
    os.makedirs("debates", exist_ok=True)
    if not args.no_blog and not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
        print(f"Created output directory: {args.output_dir}")

    # Create and run the debate
    debate = Debate(
        topic=selected_topic,
        format=selected_format,
        num_participants=args.participants,
        max_iterations=args.iterations,
        create_blog_post=not args.no_blog,
        output_dir=args.output_dir
    )
    
    await debate.run()
    
    # Save the current state for next run
    if non_interactive:
        save_debate_state(topic_index)
        print(f"Updated debate state - next topic will be index {(topic_index + 1) % len(DEBATE_CONFIGS['debate_topics'])}")

if __name__ == "__main__":
    asyncio.run(main())
