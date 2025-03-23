import asyncio
import argparse
import os
from colorama import init
from dotenv import load_dotenv

from constants import DEBATE_CONFIGS
from debate import Debate
from config import DebateConfig

# Initialize colorama and load environment variables
init()
load_dotenv()

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

def parse_arguments():
    parser = argparse.ArgumentParser(description="Run an AI debate simulation")
    parser.add_argument("--participants", type=int, default=4, help="Number of debate participants (default: 4)")
    parser.add_argument("--iterations", type=int, default=5, help="Maximum number of debate turns (default: 50)")
    parser.add_argument("--output-dir", type=str, default="_posts", help="Directory for Jekyll blog posts (default: _posts)")
    parser.add_argument("--no-blog", action="store_true", help="Disable Jekyll blog post creation")
    
    return parser.parse_args()

async def main():
    # Parse command-line arguments
    args = parse_arguments()
    
    # Get user selections
    selected_topic = select_topic()
    selected_format = select_debate_format()

    print(f"\nDebate Topic: {selected_topic['name']}")
    print(f"Debate Format: {selected_format['name']}")
    
    # Create output directory if it doesn't exist
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

if __name__ == "__main__":
    asyncio.run(main())
