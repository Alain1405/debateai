import uuid
from typing import List, Dict, Optional
from colorama import Fore, Style

from agents import Agent, Runner, WebSearchTool, TResponseInputItem, trace
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

from constants import DEBATE_CONFIGS
from agent_helpers import CustomAgentHooks
from jekyll_transcript import JekyllPostGenerator
from pydantic import BaseModel

class Debate:
    def __init__(self, 
                 topic: Dict[str, str], 
                 format: Dict[str, str], 
                 num_participants: int = 10,
                 max_iterations: int = 50,
                 save_transcript: bool = True,
                 create_blog_post: bool = True,
                 output_dir: str = "_posts"):
        self.topic = topic
        self.format = format
        self.num_participants = num_participants
        self.max_iterations = max_iterations
        self.debaters: List[Agent] = []
        self.moderator: Optional[Agent] = None
        self.host: Optional[Agent] = None
        self.save_transcript = save_transcript
        self.create_blog_post = create_blog_post
        self.output_dir = output_dir
        
        # Create transcript recorder
        if self.save_transcript:
            self.transcript = JekyllPostGenerator(
                output_dir=output_dir,
                debate_title=topic["name"],
                debate_format=format["name"],
                tags=["ai-debate", topic["name"].lower().replace(" ", "-"), format["name"].lower().replace(" ", "-")],
                categories=["debates", "ai-discussions"]
            )
            
            # Reset static transcript_recorder in CustomAgentHooks
            CustomAgentHooks.transcript_recorder = self.transcript
        
        # Initialize the debate
        self._create_debaters()  # First create participants
        self._create_moderator() # Then create moderator (will be added to debaters)
        self._create_host()      # Finally create host with handoffs to all debaters + moderator
    
    def _create_debaters(self) -> None:
        """Create the debater agents based on the personas in DEBATE_CONFIGS"""
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
        
        for persona in DEBATE_CONFIGS["personas"][:self.num_participants]:
            formatted_key_issues = "\n".join(f"- {issue}" for issue in persona["key_issues"])
            
            current_prompt = prompt_template.format(
                name=persona["name"],
                beliefs=persona["core_beliefs"],
                slogan=persona["slogan"],
                key_issues=formatted_key_issues,
                blind_spots=persona["blind_spots"],
                format_name=self.format["name"],
                format_structure=self.format["structure"],
                topic=self.topic["name"],
            )
            
            agent = Agent(
                name=persona["name"],
                instructions=f"{RECOMMENDED_PROMPT_PREFIX}: {current_prompt}",
                tools=[WebSearchTool()],
                hooks=CustomAgentHooks(display_name=persona["name"]),
            )
            self.debaters.append(agent)
    
    def _create_moderator(self) -> None:
        """Create the moderator agent to facilitate constructive debate"""
        moderator_prompt = f"""You are a debate moderator participating in a debate on {self.topic['name']}. You don't have a position on the topic, but your job is to make the debate more constructive and productive.

Your responsibilities:
- {DEBATE_CONFIGS['moderator']['role']}
- Clarify misunderstandings between participants
- Identify areas of potential agreement
- Ask probing questions to deepen the conversation
- Reframe heated exchanges in more constructive terms
- Encourage participants to engage with each other's strongest arguments
- Signal to the host when the debate has reached a satisfactory conclusion

Your key skills:
{chr(10).join(f'- {skill}' for skill in DEBATE_CONFIGS['moderator']['skills'])}

Focus on enhancing the quality of dialogue rather than controlling who speaks."""

        self.moderator = Agent(
            name="Moderator",
            instructions=moderator_prompt,
            hooks=CustomAgentHooks(display_name="Moderator"),
        )
        # Add moderator to the list of debaters so it can be part of handoffs
        self.debaters.append(self.moderator)

    def _create_host(self) -> None:
        """Create the host agent that manages the debate flow"""
        host_prompt = f"""You are a debate host managing a discussion between {self.num_participants} different personas on the topic of {self.topic['name']}.

The debate follows the {self.format['name']} format: {self.format['structure']}
The objective is to explore different perspectives on the topic, find common ground, and clarify key points of contention.

Your responsibilities:
- Introduce the debate topic and format
- Manage who speaks next, ensuring fair participation
- Periodically hand off to the moderator when:
  - The conversation is stagnating
  - It's time to move to the next phase of the conversation
- Recognize when the moderator needs to intervene
- Periodically invite the moderator to help clarify points or improve dialogue
- Conclude the debate when appropriate points have been discussed
- Provide a final analysis summarizing key insights and areas of agreement/disagreement

Start by introducing the topic and format, then hand off to the first participant. After about 5-10 rounds, if the debate has explored the topic thoroughly, work toward a conclusion and final analysis."""

        self.host = Agent(
            name="Host",
            instructions=host_prompt,
            handoffs=self.debaters,
            handoff_description="Pass the discussion to the next participant or moderator with context.",
            hooks=CustomAgentHooks(display_name="Host"),
            output_type=self.FinalResult,
        )

    class FinalResult(BaseModel):
        summary: str
    
    async def run(self) -> None:
        """Run the debate for the specified number of iterations"""
        inputs: list[TResponseInputItem] = [
            {
                "content": "Start the debate by introducing the topic and handing over the conversation.",
                "role": "user",
            }
        ]
        
        print(f"\n{Fore.YELLOW}=== Debate Session Started ==={Style.RESET_ALL}\n")
        
        # Add initial instruction to transcript
        if self.save_transcript:
            self.transcript.add_entry(speaker="System", content="Debate begins on topic: " + self.topic["name"])
        
        iteration_count = 0
        last_speaker = "System"
        last_content = ""
        
        while iteration_count < self.max_iterations + 1:
            iteration_count += 1
            conversation_id = str(uuid.uuid4().hex[:16])
            
            with trace("Debate iteration", group_id=conversation_id):
                # Run the host agent instead of the moderator
                result = await Runner.run(self.host, input=inputs, max_turns=self.max_iterations)
                
                # Record the output to transcript
                if self.save_transcript and hasattr(result, "final_output"):
                    speaker_name = hasattr(result, "last_agent") and result.last_agent.name or "Host"
                    
                    # Extract content properly from the final_output object
                    if hasattr(result.final_output, "summary"):
                        content = result.final_output.summary
                    else:
                        content = str(result.final_output)
                    
                    # Add to transcript
                    self.transcript.add_entry(speaker=speaker_name, content=content)
                    last_speaker = speaker_name
                    last_content = content
                
                inputs = result.to_input_list()
            
            # Add feedback about remaining iterations
            if iteration_count >= self.max_iterations:
                print(f"\n{Fore.RED}Debate reached the maximum of {self.max_iterations} turns and will now end.{Style.RESET_ALL}")
                if self.save_transcript:
                    self.transcript.add_entry(speaker="System", 
                                             content=f"Debate ended after reaching the maximum of {self.max_iterations} turns.")
        
        # Add final summary if available
        if last_speaker == "Moderator" and "summary" in last_content.lower():
            if self.save_transcript:
                self.transcript.add_entry(speaker="System", content="Final debate summary:")
        
        # Save the transcript and generate blog post if requested
        if self.save_transcript:
            self.transcript.save()
            
        print(f"\n{Fore.YELLOW}=== Debate Session Ended ==={Style.RESET_ALL}\n")