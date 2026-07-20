"""Back Matter Agent - Generates acknowledgments and author bio."""

import asyncio
from typing import Dict, Any

from .base import AIAgent
from ..story_bible import StoryBible
from ..utils.prompts import PromptTemplates


class BackMatterAgent(AIAgent):
    """
    Back Matter Agent generates back matter sections using AI.
    
    Creates acknowledgments, author bio, and discussion questions.
    """
    
    def __init__(self, ai_provider=None):
        """Initialize the Back Matter Agent."""
        super().__init__(
            name="Back Matter Agent",
            ai_provider=ai_provider,
            default_model="mistral-large-latest",
            default_temperature=0.6,
            default_max_tokens=1500
        )
        
    async def execute(self, bible: StoryBible) -> Dict[str, Any]:
        """
        Execute back matter generation.
        
        Args:
            bible: Story Bible to update
            
        Returns:
            Execution results
        """
        self.log_start()
        
        # Generate back matter sections with AI
        back_matter = await self._generate_back_matter(bible)
        
        # Store in metadata
        bible.metadata["back_matter"] = back_matter
        
        # Record changes
        self.record_changes(
            bible,
            changes={
                "back_matter": True,
                "sections": list(back_matter.keys())
            },
            summary="Generated back matter: acknowledgments, author bio, discussion questions"
        )
        
        self.log_action("Generated back matter sections")
        self.log_end(success=True)
        
        return {
            "success": True,
            "back_matter": back_matter
        }
    
    async def _generate_back_matter(self, bible: StoryBible) -> Dict[str, str]:
        """
        Generate back matter using AI.
        
        Args:
            bible: Story Bible with book information
            
        Returns:
            Dictionary of back matter sections
        """
        # Extract book info
        title = bible.metadata.get("title", bible.project_name or "Untitled Novel")
        author = bible.metadata.get("author", "[Author Name]")
        
        # Format prompt
        prompt = PromptTemplates.format_prompt(
            PromptTemplates.BACK_MATTER,
            title=title,
            author=author,
            genre=bible.brief.genre,
            theme=bible.concept.theme
        )
        
        # Generate back matter with AI
        response = await self.generate_text(
            prompt=prompt,
            temperature=0.6,
            max_tokens=1500
        )
        
        # Parse AI response
        back_matter = self._parse_back_matter(response.content, author)
        
        return back_matter
    
    def _parse_back_matter(self, ai_response: str, author: str) -> Dict[str, str]:
        """
        Parse AI response into back matter sections.
        
        Args:
            ai_response: Raw AI response
            author: Author name
            
        Returns:
            Dictionary of back matter sections
        """
        sections = {}
        lines = ai_response.strip().split('\n')
        
        current_section = None
        current_content = []
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Detect section headers
            if 'author bio' in line_lower or 'about the author' in line_lower:
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = 'author_bio'
                current_content = []
                # Check if content is on same line
                if ':' in line and line.split(':', 1)[1].strip():
                    current_content.append(line.split(':', 1)[1].strip())
            elif 'acknowledgment' in line_lower:
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = 'acknowledgments'
                current_content = []
                if ':' in line and line.split(':', 1)[1].strip():
                    current_content.append(line.split(':', 1)[1].strip())
            elif 'about the book' in line_lower or 'book description' in line_lower:
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = 'about_the_book'
                current_content = []
                if ':' in line and line.split(':', 1)[1].strip():
                    current_content.append(line.split(':', 1)[1].strip())
            elif 'discussion question' in line_lower:
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                current_section = 'discussion_questions'
                current_content = []
            elif current_section and line.strip() and not line.startswith('#'):
                current_content.append(line)
        
        # Save last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        # Ensure we have at least acknowledgments and author bio
        if 'acknowledgments' not in sections:
            sections['acknowledgments'] = f"""Acknowledgments

I would like to thank everyone who supported me throughout the writing of this book.
Your encouragement and feedback were invaluable."""
        
        if 'author_bio' not in sections:
            sections['author_bio'] = f"""About the Author

{author} is a writer who enjoys crafting compelling stories.

Connect with the author:
- Website: [author-website.com]
- Social Media: @authorhandle"""
        
        return sections