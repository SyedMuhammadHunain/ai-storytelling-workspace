"""Back Matter Agent - Generates acknowledgments and author bio."""

from typing import Dict, Any

from .base import MockAgent
from ..story_bible import StoryBible


class BackMatterAgent(MockAgent):
    """
    Back Matter Agent generates back matter sections.
    
    Creates acknowledgments and author bio.
    """
    
    def __init__(self):
        """Initialize the Back Matter Agent."""
        super().__init__(name="Back Matter Agent")
        
    def execute(self, bible: StoryBible) -> Dict[str, Any]:
        """
        Execute back matter generation.
        
        Args:
            bible: Story Bible to update
            
        Returns:
            Execution results
        """
        self.log_start()
        
        # Generate back matter sections
        back_matter = self._generate_back_matter(bible)
        
        # Store in metadata
        bible.metadata["back_matter"] = back_matter
        
        # Record changes
        self.record_changes(
            bible,
            changes={
                "back_matter": True,
                "sections": list(back_matter.keys())
            },
            summary="Generated back matter: acknowledgments, author bio"
        )
        
        self.log_action("Generated back matter sections")
        self.log_end(success=True)
        
        return {
            "success": True,
            "back_matter": back_matter
        }
        
    def _generate_back_matter(self, bible: StoryBible) -> Dict[str, str]:
        """
        Generate mock back matter.
        
        Args:
            bible: Story Bible with book information
            
        Returns:
            Dictionary of back matter sections
        """
        return {
            "acknowledgments": """
Acknowledgments

I would like to thank my family and friends for their unwavering support throughout 
the writing of this book. Special thanks to my beta readers who provided invaluable 
feedback, and to my editor for helping shape this story into its final form.

To the readers who have followed this journey - thank you for believing in this story.
""",
            "author_bio": """
About the Author

[Author Name] is a writer of [genre] fiction. This is their [first/second/etc] novel.
When not writing, they enjoy [hobbies] and live in [location] with [family/pets].

Connect with the author:
- Website: [author-website.com]
- Social Media: @authorhandle
"""
        }
