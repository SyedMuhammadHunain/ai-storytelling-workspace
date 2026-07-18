"""Prompt templates for AI agents."""

from typing import Dict, Any


def build_concept_prompt(genre: str, premise: str, tone: str = "engaging") -> str:
    """
    Build prompt for Concept Agent.
    
    Args:
        genre: Book genre
        premise: Initial premise/idea
        tone: Desired tone
        
    Returns:
        Formatted prompt
    """
    return f"""You are a professional story concept developer. Your task is to expand a brief premise into a compelling book concept.

**Genre:** {genre}
**Premise:** {premise}
**Tone:** {tone}

Generate a complete book concept with the following elements:

1. **Logline** (1-2 sentences): A compelling one-sentence summary that captures the essence of the story. Include the protagonist, their goal, and the main obstacle.

2. **Central Conflict**: The primary struggle or challenge that drives the narrative. What is at stake? What must be overcome?

3. **Theme**: The deeper meaning or message of the story. What universal truth or question does it explore?

Format your response as JSON:
{{
  "logline": "...",
  "central_conflict": "...",
  "theme": "..."
}}

Make it compelling, original, and appropriate for the {genre} genre."""


def build_character_prompt(
    concept_logline: str,
    theme: str,
    genre: str,
    character_role: str = "protagonist"
) -> str:
    """
    Build prompt for Character Agent.
    
    Args:
        concept_logline: Story logline for context
        theme: Story theme
        genre: Book genre
        character_role: Role (protagonist, antagonist, supporting)
        
    Returns:
        Formatted prompt
    """
    return f"""You are a professional character developer. Create a detailed character profile for a {genre} story.

**Story Context:**
- Logline: {concept_logline}
- Theme: {theme}
- Genre: {genre}

**Character Role:** {character_role}

Create a compelling {character_role} character with:

1. **Name**: Memorable and appropriate for the genre
2. **Physical Description**: Age, appearance, distinctive features
3. **Backstory**: Key events that shaped them (2-3 sentences)
4. **Goals**: What they want (3 specific goals)
5. **Flaws**: Weaknesses or limitations (3 specific flaws)
6. **Character Arc**: How they change throughout the story
7. **Voice Signature**: How they speak and express themselves

Format as JSON:
{{
  "name": "...",
  "role": "{character_role}",
  "physical_description": "...",
  "backstory": "...",
  "goals": ["...", "...", "..."],
  "flaws": ["...", "...", "..."],
  "arc": "...",
  "voice_signature": "..."
}}

Make the character complex, believable, and integral to the story's theme."""


def build_worldbuilding_prompt(
    concept_logline: str,
    genre: str,
    characters: list,
    setting_type: str = "detailed"
) -> str:
    """
    Build prompt for Worldbuilding Agent.
    
    Args:
        concept_logline: Story logline
        genre: Book genre
        characters: List of character names
        setting_type: Level of detail needed
        
    Returns:
        Formatted prompt
    """
    characters_str = ", ".join(characters) if characters else "the characters"
    
    return f"""You are a professional worldbuilding expert. Create a rich, immersive world for this {genre} story.

**Story Context:**
- Logline: {concept_logline}
- Genre: {genre}
- Main Characters: {characters_str}

Create a {setting_type} world with:

1. **Primary Setting**: Main location(s) where the story takes place
2. **Time Period**: When the story occurs (historical, contemporary, future, etc.)
3. **World Rules**: Key rules that govern this world (magic systems, technology, social structures, etc.)
4. **Cultural Elements**: Important customs, beliefs, or social dynamics
5. **Atmosphere**: The overall feel and mood of the world

Format as JSON:
{{
  "primary_setting": "...",
  "time_period": "...",
  "world_rules": ["...", "...", "..."],
  "cultural_elements": ["...", "...", "..."],
  "atmosphere": "..."
}}

Make the world feel lived-in, consistent, and integral to the story."""


def build_plot_prompt(
    concept_logline: str,
    theme: str,
    characters: Dict[str, str],
    target_chapters: int = 30
) -> str:
    """
    Build prompt for Plot Architect Agent.
    
    Args:
        concept_logline: Story logline
        theme: Story theme
        characters: Dict of character names and roles
        target_chapters: Target number of chapters
        
    Returns:
        Formatted prompt
    """
    characters_str = "\n".join([f"- {name} ({role})" for name, role in characters.items()])
    
    return f"""You are a professional plot architect. Create a detailed story structure with {target_chapters} chapters.

**Story Context:**
- Logline: {concept_logline}
- Theme: {theme}
- Characters:
{characters_str}

Create a three-act structure with:

**Act 1 (Setup - Chapters 1-{target_chapters//3}):**
- Introduce world, characters, and normal life
- Inciting incident that disrupts the status quo
- First plot point that launches the main story

**Act 2 (Confrontation - Chapters {target_chapters//3+1}-{2*target_chapters//3}):**
- Rising action and complications
- Midpoint twist or revelation
- Increasing stakes and challenges
- Second plot point leading to climax

**Act 3 (Resolution - Chapters {2*target_chapters//3+1}-{target_chapters}):**
- Climax and final confrontation
- Resolution of main conflict
- Character transformation complete
- Denouement

For each chapter, provide:
1. Chapter number and title
2. Key events (2-3 sentences)
3. Character development moments
4. Plot progression

Format as JSON array:
[
  {{
    "chapter_number": 1,
    "title": "...",
    "summary": "...",
    "key_events": ["...", "..."],
    "character_moments": ["..."],
    "act": 1
  }},
  ...
]

Ensure proper pacing, escalating tension, and satisfying character arcs."""


def build_chapter_drafting_prompt(
    chapter_number: int,
    chapter_title: str,
    chapter_summary: str,
    previous_chapter_summary: str,
    characters: Dict[str, Dict[str, Any]],
    world_context: str,
    target_words: int = 3000
) -> str:
    """
    Build prompt for Chapter Drafting Agent.
    
    Args:
        chapter_number: Chapter number
        chapter_title: Chapter title
        chapter_summary: What should happen in this chapter
        previous_chapter_summary: Summary of previous chapter
        characters: Character details
        world_context: World/setting information
        target_words: Target word count
        
    Returns:
        Formatted prompt
    """
    return f"""You are a professional fiction writer. Write Chapter {chapter_number}: "{chapter_title}"

**Chapter Brief:**
{chapter_summary}

**Previous Chapter:**
{previous_chapter_summary}

**World Context:**
{world_context}

**Target Length:** ~{target_words} words

**Writing Guidelines:**
1. Show, don't tell - use vivid sensory details
2. Maintain consistent character voices
3. Balance action, dialogue, and description
4. Create engaging scene transitions
5. End with a hook for the next chapter
6. Use proper paragraph breaks and pacing

Write the complete chapter text. Focus on:
- Compelling prose that draws readers in
- Natural dialogue that reveals character
- Vivid descriptions that immerse readers
- Proper story progression
- Emotional resonance

Begin writing the chapter now:"""


def build_dialogue_prompt(
    scene_context: str,
    characters_present: list,
    character_voices: Dict[str, str],
    dialogue_purpose: str
) -> str:
    """
    Build prompt for Dialogue/Voice Agent.
    
    Args:
        scene_context: What's happening in the scene
        characters_present: List of character names
        character_voices: Dict of character voice signatures
        dialogue_purpose: What the dialogue should accomplish
        
    Returns:
        Formatted prompt
    """
    voices_str = "\n".join([
        f"- {name}: {voice}"
        for name, voice in character_voices.items()
        if name in characters_present
    ])
    
    return f"""You are a dialogue specialist. Enhance the dialogue in this scene.

**Scene Context:**
{scene_context}

**Characters Present:** {", ".join(characters_present)}

**Character Voices:**
{voices_str}

**Dialogue Purpose:**
{dialogue_purpose}

Rewrite the dialogue to:
1. Match each character's unique voice
2. Sound natural and authentic
3. Reveal character through subtext
4. Advance the plot or deepen relationships
5. Avoid exposition dumps
6. Use appropriate tags and beats

Provide the enhanced dialogue with proper formatting."""


def build_editing_prompt(
    text: str,
    editing_focus: str,
    style_guide: str = "clear, engaging prose"
) -> str:
    """
    Build prompt for editing agents (developmental, line, copy).
    
    Args:
        text: Text to edit
        editing_focus: What to focus on (structure, prose, grammar, etc.)
        style_guide: Style guidelines
        
    Returns:
        Formatted prompt
    """
    return f"""You are a professional editor. Review and improve this text.

**Editing Focus:** {editing_focus}
**Style Guide:** {style_guide}

**Text to Edit:**
{text}

Provide:
1. **Issues Found**: List specific problems
2. **Suggestions**: Concrete improvements
3. **Revised Text**: The improved version

Focus on:
- Clarity and readability
- Consistency and flow
- Grammar and mechanics
- Style and voice
- Pacing and structure

Format as JSON:
{{
  "issues": ["...", "..."],
  "suggestions": ["...", "..."],
  "revised_text": "..."
}}"""


def build_continuity_check_prompt(
    current_text: str,
    story_bible_summary: str,
    check_type: str = "comprehensive"
) -> str:
    """
    Build prompt for Continuity Agent.
    
    Args:
        current_text: Text to check
        story_bible_summary: Summary of established facts
        check_type: Type of check (character, plot, world, comprehensive)
        
    Returns:
        Formatted prompt
    """
    return f"""You are a continuity checker. Verify consistency with established story elements.

**Check Type:** {check_type}

**Established Story Elements:**
{story_bible_summary}

**Text to Check:**
{current_text}

Identify any continuity errors or inconsistencies:
1. Character inconsistencies (behavior, appearance, abilities)
2. Plot contradictions (timeline, events, cause-effect)
3. World rule violations (magic, technology, geography)
4. Factual errors (names, dates, locations)

Format as JSON:
{{
  "errors_found": [
    {{
      "type": "character|plot|world|factual",
      "description": "...",
      "location": "...",
      "severity": "minor|moderate|major",
      "suggestion": "..."
    }}
  ],
  "overall_consistency": "excellent|good|needs_work|poor"
}}

If no errors found, return empty errors_found array."""


def build_qa_prompt(
    manuscript_section: str,
    qa_checklist: list,
    quality_standards: str
) -> str:
    """
    Build prompt for QA Agent.
    
    Args:
        manuscript_section: Section to review
        qa_checklist: List of items to check
        quality_standards: Quality criteria
        
    Returns:
        Formatted prompt
    """
    checklist_str = "\n".join([f"- {item}" for item in qa_checklist])
    
    return f"""You are a quality assurance specialist for fiction manuscripts.

**Quality Standards:**
{quality_standards}

**QA Checklist:**
{checklist_str}

**Manuscript Section:**
{manuscript_section}

Perform a comprehensive quality check and provide:

1. **Checklist Results**: Pass/Fail for each item
2. **Quality Score**: Overall rating (1-10)
3. **Issues Found**: Specific problems
4. **Recommendations**: How to improve

Format as JSON:
{{
  "checklist_results": {{
    "item_name": {{"status": "pass|fail", "notes": "..."}},
    ...
  }},
  "quality_score": 8,
  "issues": ["...", "..."],
  "recommendations": ["...", "..."],
  "ready_for_publication": true|false
}}"""
