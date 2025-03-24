import uuid
from typing import List, Dict, Optional
from colorama import Fore, Style

from agents import Agent, Runner, WebSearchTool, TResponseInputItem, trace
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

from constants import DEBATE_CONFIGS
from agent_helpers import CustomAgentHooks
from jekyll_transcript import JekyllPostGenerator
from pydantic import BaseModel
from typing import Literal

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
Let the Moderator and Host manage the converastion and handoffs between participants. 
Follow the moderator guidance and the debate format to ensure a constructive and productive debate.
Do not mention debate phases or handoffs in your responses.
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
                model="gpt-4o-mini",
            )
            self.debaters.append(agent)
    
    def _create_moderator(self) -> None:
        """Create the moderator agent to facilitate constructive debate"""
        moderator_prompt = f"""You are a debate moderator participating in a debate on {self.topic['name']}. You don't have a position on the topic, but your job is to make the debate more constructive and productive. The participants are {', '.join([agent.name for agent in self.debaters])}.

Your key skills:
{chr(10).join(f'- {skill}' for skill in DEBATE_CONFIGS['moderator']['skills'])}

Focus on enhancing the quality of dialogue rather than controlling who speaks.

The debate will follow the {self.format['name']} format: {self.format['structure']} and it's strucutered in 5 phases:

Phase 1 (Opening Statements)
- Invite each participant to briefly share their position (no interruptions)
- Once all have spoken, hand off to the moderator to deepen the discussion
Phase 2 (Clarification & Engagement)
- Ask participants to explain or summarize each other's views
- Clarify terminology or assumptions
- Encourage deep reflection with questions like "What value does that represent for you?" or "Can you express this idea in the best possible terms?"
- This phase can be repeated up to 3 times to ensure understanding, then we must move one

Phase 3 (Exploration of Disagreement)
- Identify key areas of friction or difference
- Ask questions like "Is this a disagreement of values, facts, or priorities?" or "What trade-offs are at play here?"
- This phase should be repeated between 3 and 6 times, depending on the complexity of the topic and on the extent of the disagreements

Phase 4 (Common Ground Discovery)
- Prompt participants to find overlaps or shared goals with questions like "Do you agree on any underlying concerns?" or "Is there a solution that meets multiple priorities?"
- Encourage participants to build on each other's ideas
- Signal the host when common ground has been explored or no further progress is likely

Your responsibilities:
- {DEBATE_CONFIGS['moderator']['role']}
- Clarify misunderstandings between participants
- Identify areas of potential agreement
- Ask probing questions to deepen the conversation
- Reframe heated exchanges in more constructive terms
- Encourage participants to engage with each other's strongest arguments
- Signal to the host who should speak next
- Signal to the host when the debate has reached a satisfactory conclusion
- When the conversation is handed over to you, guide it through the 5 phases of the debate format, suggesting the next speaker

At the end of your response, you can optionally include a phase indicator like "[Current Phase: Clarification, Next Speaker: Speaker Name]" to help the host track debate progress and hand off the conversation.
"""

        self.moderator = Agent(
            name="Moderator",
            instructions=moderator_prompt,
            hooks=CustomAgentHooks(display_name="Moderator"),
            model="gpt-4o",
        )
        # Add moderator to the list of debaters so it can be part of handoffs
        self.debaters.append(self.moderator)

    def _create_host(self) -> None:
        """Create the host agent that manages the debate flow"""
        host_prompt = f"""You are a debate host managing a discussion between {self.num_participants} different personas on the topic of {self.topic['name']}.

The debate follows the {self.format['name']} format: {self.format['structure']}
The objective is to explore different perspectives on the topic, find common ground, and clarify key points of contention.

Your responsibilities:
- Introduce the debate topic, format, participants and moderator ({', '.join([agent.name for agent in self.debaters])})
- Manage who speaks next, ensuring fair participation, starting from the moderator
- Handoff based on 5 debate phases:
  1. Opening Statements - Each participant briefly shares their position
  2. Clarification & Engagement - Moderator leads understanding of positions
  3. Exploration of Disagreement - Moderator identifies key tensions
  4. Common Ground Discovery - Moderator helps find shared values
  5. Closing & Summary - You provide final analysis
- Let the moderator guide the conversation through these phases by handing off the conversation to him/her.
- Provide a final analysis summarizing key insights and areas of agreement/disagreement

🧭 Phase Guidance for Host:

Phase 5 (Closing & Summary)
- After the moderator signals the conversation has matured, thank participants and summarize:
  - Core views represented
  - Key disagreements
  - Areas of overlap or agreement
  - Open questions or potential paths forward

In your response, you must set the 'status' field to indicate whether the debate is still in progress or has concluded:
- Set status to 'in_progress' when the debate should continue
- Set status to 'concluded' when you provide your final summary and the debate should end

Start by introducing the topic and format, then guide the debate through Phase 1 (Opening Statements) by inviting participants to share their initial positions."""

        self.host = Agent(
            name="Host",
            instructions=host_prompt,
            handoffs=self.debaters,
            handoff_description="Pass the discussion to the next participant or moderator with context.",
            hooks=CustomAgentHooks(display_name="Host"),
            output_type=self.FinalResult,
            model="gpt-4o",
        )

    class FinalResult(BaseModel):
        summary: str
        status: Literal["in_progress", "concluded"] = "in_progress"
    
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
        debate_concluded = False
        
        while iteration_count < self.max_iterations and not debate_concluded:
            iteration_count += 1
            conversation_id = str(uuid.uuid4().hex[:16])
            
            with trace("Debate iteration", group_id=conversation_id):
                # Run the host agent
                result = await Runner.run(self.host, input=inputs, max_turns=self.max_iterations)
                
                # Record the output to transcript
                if self.save_transcript and hasattr(result, "final_output"):
                    speaker_name = hasattr(result, "last_agent") and result.last_agent.name or "Host"
                    
                    # Extract content properly from the final_output object
                    if hasattr(result.final_output, "summary"):
                        content = result.final_output.summary
                        
                        # Check if the debate has concluded based on the status field
                        if hasattr(result.final_output, "status") and result.final_output.status == "concluded":
                            debate_concluded = True
                            print(f"\n{Fore.GREEN}Host has indicated the debate has concluded.{Style.RESET_ALL}")
                            if self.save_transcript:
                                self.transcript.add_entry(speaker="System", 
                                                         content="Debate concluded with a final summary from the Host.")
                    else:
                        content = str(result.final_output)
                    
                    # Add to transcript
                    self.transcript.add_entry(speaker=speaker_name, content=content)
                
                inputs = result.to_input_list()
            
            # Add feedback about remaining iterations
            if iteration_count >= self.max_iterations and not debate_concluded:
                print(f"\n{Fore.RED}Debate reached the maximum of {self.max_iterations} turns and will now end.{Style.RESET_ALL}")
                if self.save_transcript:
                    self.transcript.add_entry(speaker="System", 
                                             content=f"Debate ended after reaching the maximum of {self.max_iterations} turns.")
        
        # Save the transcript and generate blog post if requested
        if self.save_transcript:
            self.transcript.save()
            
        print(f"\n{Fore.YELLOW}=== Debate Session Ended ==={Style.RESET_ALL}\n")