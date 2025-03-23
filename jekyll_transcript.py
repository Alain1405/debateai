import datetime
import os
import re
from typing import List, Dict, Any, Optional
from transcript import TranscriptRecorder

class JekyllPostGenerator(TranscriptRecorder):
    """Extends TranscriptRecorder to create Jekyll-compatible blog posts from debate transcripts."""
    
    def __init__(self, 
                output_dir: str = "_posts",
                output_file: Optional[str] = None,
                debate_title: Optional[str] = None,
                debate_format: Optional[str] = None,
                tags: List[str] = None,
                categories: List[str] = None):
        """
        Initialize the Jekyll post generator.
        
        Args:
            output_dir: Directory where Jekyll posts will be saved (default: "_posts")
            output_file: Optional specific filename for the JSON transcript
            debate_title: Title of the debate
            debate_format: Format of the debate
            tags: List of tags for the Jekyll post
            categories: List of categories for the Jekyll post
        """
        super().__init__(output_file)
        self.output_dir = output_dir
        self.debate_title = debate_title or "AI Debate"
        self.debate_format = debate_format or "General Discussion"
        self.tags = tags or ["ai", "debate", "artificial-intelligence"]
        self.categories = categories or ["debates"]
        self.debate_date = datetime.datetime.now()
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
    
    def create_slug(self) -> str:
        """Create an SEO-friendly slug from the debate title."""
        slug = self.debate_title.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)  # Remove special chars
        slug = re.sub(r'\s+', '-', slug)          # Replace spaces with hyphens
        return slug
    
    def generate_frontmatter(self) -> str:
        """Generate Jekyll frontmatter for the post."""
        # Ensure proper YAML formatting for lists
        categories_str = '[' + ', '.join(f"'{cat}'" for cat in self.categories) + ']'
        tags_str = '[' + ', '.join(f"'{tag}'" for tag in self.tags) + ']'
        
        frontmatter = [
            "---",
            f"layout: post",
            f"title: \"AI Debate: {self.debate_title}\"",
            f"date: {self.debate_date.strftime('%Y-%m-%d %H:%M:%S')}",
            f"categories: {categories_str}",
            f"tags: {tags_str}",
            f"description: \"An AI-powered debate on {self.debate_title} using the {self.debate_format} format with multiple AI personas.\"",
            f"excerpt: \"Explore diverse perspectives on {self.debate_title} through an AI-simulated debate featuring different ideological viewpoints.\"",
            f"author: AI Debate System",
            "published: true",
            "---\n\n"
        ]
        return "\n".join(frontmatter)
    
    def format_debate_intro(self) -> str:
        """Create an introduction section for the debate."""
        intro = [
            f"# AI Debate: {self.debate_title}",
            "",
            f"*This is an AI-simulated debate on the topic of **{self.debate_title}** using the **{self.debate_format}** format. Multiple AI personas with different ideological perspectives engage in a moderated discussion to explore this complex issue.*",
            "",
            "## Debate Overview",
            "",
            f"**Topic:** {self.debate_title}",
            f"**Format:** {self.debate_format}",
            f"**Date:** {self.debate_date.strftime('%B %d, %Y')}",
            f"**Number of Participants:** {self._count_unique_speakers()}",
            "",
            "---",
            "",
            "## Debate Transcript",
            ""
        ]
        return "\n".join(intro)
    
    def _count_unique_speakers(self) -> int:
        """Count the number of unique speakers in the transcript."""
        speakers = set()
        for entry in self.entries:
            if "speaker" in entry and entry["speaker"] != "Moderator" and entry["speaker"] != "System":
                speakers.add(entry["speaker"])
        return len(speakers)
    
    def format_debate_content(self) -> str:
        """Format the debate transcript as markdown."""
        content = []
        
        for entry in self.entries:
            if "speaker" not in entry or "content" not in entry:
                continue
                
            speaker = entry["speaker"]
            message = entry["content"]
            
            # Skip empty messages or system messages
            if not message or speaker == "System":
                continue
                
            # Format differently based on speaker role
            if speaker == "Moderator":
                content.append(f"### {speaker}:\n\n{message}\n")
            else:
                content.append(f"#### {speaker}:\n\n{message}\n")
        
        return "\n".join(content)
    
    def format_debate_conclusion(self) -> str:
        """Create a conclusion section for the debate."""
        conclusion = [
            "## About This Debate",
            "",
            "This debate was generated using the DebateAI platform, which simulates discussions between multiple AI agents representing different ideological perspectives. Each agent is given a distinct persona with specific beliefs, values, and rhetorical styles.",
            "",
            "The goal of these simulated debates is to explore complex topics from multiple angles and demonstrate how different worldviews approach the same issues.",
            "",
            "*Note: The views expressed by these AI personas do not represent the opinions of the creators or the AI models themselves, but are simulations of different ideological frameworks for educational purposes.*",
            ""
        ]
        return "\n".join(conclusion)
    
    def create_jekyll_post(self) -> str:
        """Generate a complete Jekyll blog post from the transcript."""
        # First save the original JSON format
        super().save()
        
        # Create the Jekyll post filename (YYYY-MM-DD-slug.md)
        post_date = self.debate_date.strftime('%Y-%m-%d')
        slug = self.create_slug()
        filename = f"{post_date}-{slug}.md"
        filepath = os.path.join(self.output_dir, filename)
        
        # Compose the full post content
        post_content = "".join([
            self.generate_frontmatter(),
            self.format_debate_intro(),
            self.format_debate_content(),
            self.format_debate_conclusion()
        ])
        
        # Write the post file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(post_content)
        
        print(f"Jekyll blog post created at: {filepath}")
        return filepath
    
    def save(self):
        """Override the default save method to create both JSON and Jekyll post."""
        super().save()  # Save the JSON transcript
        self.create_jekyll_post()  # Create the Jekyll blog post