"""Image generation prompt templates for storytelling."""

from typing import Dict, Any


def build_cover_art_prompt(
    title: str,
    genre: str,
    theme: str,
    logline: str
) -> str:
    """
    Build prompt for book cover art.
    
    Args:
        title: Book title
        genre: Book genre
        theme: Central theme
        logline: Story logline
        
    Returns:
        Formatted prompt for cover art generation
    """
    return f"""Professional book cover art for a {genre} novel.

Title: {title}
Story: {logline}
Theme: {theme}

Style: Epic, cinematic, professional quality, dramatic lighting, high detail.
Composition: Centered focal point, strong visual hierarchy, compelling imagery.
Color palette: Rich, atmospheric colors appropriate for {genre}.
Quality: Publication-ready, award-winning book cover design.

IMPORTANT: No text, no title, no author name on the cover. Pure visual imagery only."""


def build_character_portrait_prompt(
    name: str,
    physical_description: str,
    role: str,
    genre: str
) -> str:
    """
    Build prompt for character portrait.
    
    Args:
        name: Character name
        physical_description: Physical description
        role: Character role
        genre: Book genre
        
    Returns:
        Formatted prompt for character portrait
    """
    return f"""Character portrait for {genre} novel.

Character: {name} ({role})
Appearance: {physical_description}

Style: Professional character art, high detail, consistent visual style.
Composition: Portrait shot, character facing forward or at slight angle.
Background: Simple, atmospheric, doesn't distract from character.
Lighting: Dramatic, highlights facial features and expression.
Quality: High detail, professional character art.

Focus on capturing the essence and personality of the character."""


def build_scene_illustration_prompt(
    chapter_title: str,
    chapter_summary: str,
    setting: str,
    genre: str
) -> str:
    """
    Build prompt for scene illustration.
    
    Args:
        chapter_title: Chapter title
        chapter_summary: Chapter summary
        setting: Scene setting
        genre: Book genre
        
    Returns:
        Formatted prompt for scene illustration
    """
    return f"""Scene illustration for {genre} novel chapter: "{chapter_title}"

Scene: {chapter_summary}
Setting: {setting}

Style: Professional illustration, cinematic composition.
Composition: Wide shot, establishing the scene and atmosphere.
Atmosphere: Immersive environment that matches the story tone.
Detail: Focus on atmosphere and key story elements.
Quality: Professional illustration, consistent visual style.

Capture the emotional tone and key story moment of this scene."""


def generate_cover_art_prompt(
    title: str,
    genre: str,
    logline: str,
    theme: str,
    tone: str
) -> str:
    """
    Generate prompt for book cover art.
    
    Args:
        title: Book title
        genre: Book genre
        logline: One-sentence story summary
        theme: Central theme
        tone: Story tone
        
    Returns:
        Formatted prompt for cover art generation
    """
    prompt = f"""Professional book cover art for a {genre} novel.

Title: {title}
Story: {logline}
Theme: {theme}
Tone: {tone}

Style: Epic, cinematic, professional quality, dramatic lighting, high detail.
Composition: Centered focal point, strong visual hierarchy, compelling imagery.
Color palette: Rich, atmospheric colors that match the {tone} tone.
Quality: Publication-ready, award-winning book cover design.

IMPORTANT: No text, no title, no author name on the cover. Pure visual imagery only."""
    
    return prompt


def generate_character_portrait_prompt(
    character_name: str,
    description: str,
    role: str,
    personality: str,
    genre: str,
    style_brief: str
) -> str:
    """
    Generate prompt for character portrait.
    
    Args:
        character_name: Character's name
        description: Physical description
        role: Character's role (protagonist, antagonist, etc.)
        personality: Key personality traits
        genre: Book genre
        style_brief: Consistent style guide for all images
        
    Returns:
        Formatted prompt for character portrait
    """
    prompt = f"""Character portrait for {genre} novel.

Character: {character_name} ({role})
Appearance: {description}
Personality: {personality}

Style: {style_brief}
Composition: Portrait shot, character facing forward or at slight angle.
Expression: Reflects personality - {personality}
Background: Simple, atmospheric, doesn't distract from character.
Lighting: Dramatic, highlights facial features and expression.
Quality: High detail, professional character art, consistent with book's visual style.

Focus on capturing the essence and personality of the character."""
    
    return prompt


def generate_scene_illustration_prompt(
    scene_description: str,
    chapter_title: str,
    mood: str,
    key_elements: list,
    genre: str,
    style_brief: str
) -> str:
    """
    Generate prompt for scene illustration.
    
    Args:
        scene_description: Description of the scene
        chapter_title: Chapter title
        mood: Emotional mood of the scene
        key_elements: List of key visual elements
        genre: Book genre
        style_brief: Consistent style guide
        
    Returns:
        Formatted prompt for scene illustration
    """
    elements_str = ", ".join(key_elements) if key_elements else "atmospheric environment"
    
    prompt = f"""Scene illustration for {genre} novel chapter: "{chapter_title}"

Scene: {scene_description}
Mood: {mood}
Key elements: {elements_str}

Style: {style_brief}
Composition: Wide cinematic shot, establishing the scene and atmosphere.
Atmosphere: Strong sense of {mood}, immersive environment.
Lighting: Matches the mood - {mood}
Detail: Focus on atmosphere and key story elements.
Quality: Professional illustration, consistent with book's visual style.

Capture the emotional tone and key story moment of this scene."""
    
    return prompt


def create_style_brief(
    genre: str,
    tone: str,
    art_style: str = "realistic",
    color_palette: str = "rich and atmospheric"
) -> str:
    """
    Create a consistent style brief for all images in a book.
    
    Args:
        genre: Book genre
        tone: Story tone
        art_style: Visual art style (realistic, painterly, etc.)
        color_palette: Color palette description
        
    Returns:
        Style brief to be used across all image generations
    """
    style_brief = f"""{art_style.capitalize()} {genre} art style.
Color palette: {color_palette}.
Tone: {tone}.
Quality: Professional, publication-ready, cinematic."""
    
    return style_brief


def optimize_prompt_for_provider(
    prompt: str,
    provider: str,
    max_length: int = 1000
) -> str:
    """
    Optimize prompt for specific provider's requirements.
    
    Args:
        prompt: Original prompt
        provider: Provider name (mistral, openai)
        max_length: Maximum prompt length
        
    Returns:
        Optimized prompt
    """
    # Truncate if too long
    if len(prompt) > max_length:
        prompt = prompt[:max_length-3] + "..."
    
    # Provider-specific optimizations
    if provider.lower() == "openai":
        # DALL-E prefers more concise prompts
        # Remove redundant phrases
        prompt = prompt.replace("IMPORTANT: ", "")
        prompt = prompt.replace("Quality: ", "")
    
    elif provider.lower() == "mistral":
        # Pixtral may benefit from more structured prompts
        # Keep as is for now
        pass
    
    return prompt


# Preset style briefs for common genres
GENRE_STYLE_PRESETS: Dict[str, Dict[str, Any]] = {
    "fantasy": {
        "art_style": "painterly fantasy art",
        "color_palette": "rich jewel tones, magical lighting",
        "mood_keywords": ["epic", "mystical", "enchanted"]
    },
    "science fiction": {
        "art_style": "sleek sci-fi concept art",
        "color_palette": "cool blues and teals, neon accents",
        "mood_keywords": ["futuristic", "technological", "vast"]
    },
    "mystery": {
        "art_style": "noir-inspired realistic art",
        "color_palette": "dark shadows, dramatic contrasts",
        "mood_keywords": ["mysterious", "suspenseful", "atmospheric"]
    },
    "romance": {
        "art_style": "soft realistic art",
        "color_palette": "warm tones, soft lighting",
        "mood_keywords": ["intimate", "emotional", "dreamy"]
    },
    "thriller": {
        "art_style": "gritty realistic art",
        "color_palette": "desaturated with bold accents",
        "mood_keywords": ["tense", "dark", "intense"]
    },
    "horror": {
        "art_style": "dark atmospheric art",
        "color_palette": "deep shadows, unsettling contrasts",
        "mood_keywords": ["eerie", "disturbing", "ominous"]
    }
}


def get_genre_style_preset(genre: str) -> Dict[str, Any]:
    """
    Get style preset for a genre.
    
    Args:
        genre: Book genre
        
    Returns:
        Style preset dictionary
    """
    genre_lower = genre.lower()
    
    # Try exact match
    if genre_lower in GENRE_STYLE_PRESETS:
        return GENRE_STYLE_PRESETS[genre_lower]
    
    # Try partial match
    for preset_genre, preset in GENRE_STYLE_PRESETS.items():
        if preset_genre in genre_lower or genre_lower in preset_genre:
            return preset
    
    # Default to fantasy style
    return GENRE_STYLE_PRESETS["fantasy"]
