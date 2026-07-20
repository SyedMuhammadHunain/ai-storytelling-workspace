"""Front Matter Agent - Generates title page, copyright, TOC."""

import asyncio
from typing import Dict, Any

from .base import AIAgent
from ..story_bible import StoryBible
from ..utils.prompts import PromptTemplates


class FrontMatterAgent(AIAgent):
    """
    Front Matter Agent generates front matter sections using AI.
    
    Creates title page, copyright page, dedication, and table of contents.
    """
    
    def __init__(self, ai_provider=None):
        """Initialize the Front Matter Agent."""
        super().__init__(
            name="Front Matter Agent",
            ai_provider=ai_provider,
            default_model="mistral-large-latest",
            default_temperature=0.5,
            default_max_tokens=1500
        )
        
    async def execute(self, bible: StoryBible) -> Dict[str, Any]:
        """
        Execute front matter generation.
        
        Args:
            bible: Story Bible to update
            
        Returns:
            Execution results
        """
        self.log_start()
        
        # Generate front matter sections with AI
        front_matter = await self._generate_front_matter(bible)
        
        # Store in metadata
        bible.metadata["front_matter"] = front_matter
        
        # Record changes
        self.record_changes(
            bible,
            changes={
                "front_matter": True,
                "sections": list(front_matter.keys())
            },
            summary="Generated front matter: title page, copyright, TOC"
        )
        
        self.log_action("Generated front matter sections")
        self.log_end(success=True)
        
        return {
            "success": True,
            "front_matter": front_matter
        }
    
    async def _generate_front_matter(self, bible: StoryBible) -> Dict[str, str]:
        """
        Generate front matter using AI.
        
        Args:
            bible: Story Bible with book information
            
        Returns:
            Dictionary of front matter sections
        """
        # Extract book title from premise or use project name
        title = self._extract_title(bible)
        author = bible.metadata.get("author", "[Author Name]")
        
        # Format prompt
        prompt = PromptTemplates.format_prompt(
            PromptTemplates.FRONT_MATTER,
            title=title,
            author=author,
            genre=bible.brief.genre,
            logline=bible.concept.logline
        )
        
        # Generate front matter with AI
        response = await self.generate_text(
            prompt=prompt,
            temperature=0.5,
            max_tokens=1500
        )
        
        # Parse AI response
        front_matter = self._parse_front_matter(response.content, bible, title, author)
        
        return front_matter
    
    def _extract_title(self, bible: StoryBible) -> str:
        """Extract or generate book title."""
        # Check metadata first
        if "title" in bible.metadata:
            return bible.metadata["title"]
        
        # Try to extract from premise
        if bible.brief and bible.brief.premise:
            words = bible.brief.premise.split()[:5]
            return " ".join(words).title()
        
        # Fallback
        return bible.project_name or "Untitled Novel"
    
    def _parse_front_matter(
        self,
        ai_response: str,
        bible: StoryBible,
        title: str,
        author: str
    ) -> Dict[str, str]:
        """
        Parse AI response into front matter sections.
        
        Args:
            ai_response: Raw AI response
            bible: Story Bible
            title: Book title
            author: Author name
            
        Returns:
            Dictionary of front matter sections
        """
        sections = {}
        
        # Always include title page
        sections["title_page"] = f"""
{title}

A Novel

by

{author}
"""
        
        # Always include copyright
        from datetime import datetime
        year = datetime.now().year
        sections["copyright"] = f"""
Copyright © {year} {author}

All rights reserved. No part of this book may be reproduced or used in any manner 
without written permission of the copyright owner except for the use of quotations 
in a book review.

First Edition

ISBN: [To be assigned]
"""
        
        # Parse AI response for dedication and other sections
        lines = ai_response.strip().split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            line_lower = line.lower().strip()
            
            if 'dedication' in line_lower and ':' in line:
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)
                current_section = 'dedication'
                current_content = []
                # Check if content is on same line
                if line.split(':', 1)[1].strip():
                    current_content.append(line.split(':', 1)[1].strip())
            elif 'epigraph' in line_lower and ':' in line:
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content)
                current_section = 'epigraph'
                current_content = []
                if line.split(':', 1)[1].strip():
                    current_content.append(line.split(':', 1)[1].strip())
            elif current_section and line.strip():
                current_content.append(line)
        
        # Save last section
        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)
        
        # Always include table of contents
        sections["table_of_contents"] = self._generate_toc(bible)
        
        return sections
    
    def _generate_toc(self, bible: StoryBible) -> str:
        """Generate table of contents from chapters."""
        toc = "Table of Contents\n\n"
        
        for chapter in sorted(bible.chapters, key=lambda c: c.number):
            toc += f"Chapter {chapter.number}: {chapter.title}\n"
            
        return toc if bible.chapters else "Table of Contents\n\n[Chapters to be added]"