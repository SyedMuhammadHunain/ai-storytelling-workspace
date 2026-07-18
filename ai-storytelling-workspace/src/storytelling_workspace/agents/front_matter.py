"""Front Matter Agent - Generates title page, copyright, TOC."""

from typing import Dict, Any

from .base import MockAgent
from ..story_bible import StoryBible


class FrontMatterAgent(MockAgent):
    """
    Front Matter Agent generates front matter sections.
    
    Creates title page, copyright page, and table of contents.
    """
    
    def __init__(self):
        """Initialize the Front Matter Agent."""
        super().__init__(name="Front Matter Agent")
        
    def execute(self, bible: StoryBible) -> Dict[str, Any]:
        """
        Execute front matter generation.
        
        Args:
            bible: Story Bible to update
            
        Returns:
            Execution results
        """
        self.log_start()
        
        # Generate front matter sections
        front_matter = self._generate_front_matter(bible)
        
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
        
    def _generate_front_matter(self, bible: StoryBible) -> Dict[str, str]:
        """
        Generate mock front matter.
        
        Args:
            bible: Story Bible with book information
            
        Returns:
            Dictionary of front matter sections
        """
        # Get book title from brief or use project name
        title = bible.brief.premise.split()[0:3] if bible.brief else ["Untitled", "Book", "Project"]
        title_text = " ".join(title).title()
        
        return {
            "title_page": f"""
{title_text}

A Novel

by

[Author Name]
""",
            "copyright": f"""
Copyright © 2026 [Author Name]

All rights reserved. No part of this book may be reproduced or used in any manner 
without written permission of the copyright owner except for the use of quotations 
in a book review.

First Edition

ISBN: [To be assigned]
""",
            "table_of_contents": self._generate_toc(bible)
        }
        
    def _generate_toc(self, bible: StoryBible) -> str:
        """Generate table of contents from chapters."""
        toc = "Table of Contents\n\n"
        
        for chapter_num in sorted(bible.chapters.keys()):
            chapter = bible.chapters[chapter_num]
            toc += f"Chapter {chapter_num}: {chapter.title}\n"
            
        return toc
