# AI Integration Guide

The AI Integration layer is the heart of the workspace, designed to abstract API specifics, handle rate limits, track costs, and ensure reliability.

## Provider Abstraction

Located in `core/ai_provider.py`, the system uses an abstraction layer `AIProvider`.

### Supported Providers
1. **Mistral AI**: Default primary provider for text generation. Cost-effective and highly capable for creative writing.
2. **Pixtral**: Used specifically for image generation (cover art, character portraits).
3. **OpenAI**: Maintained as a fallback/alternative provider if requested.

### Features
- **Caching**: Responses are cached in Redis (`core/cache.py`) to save costs on identical prompts during development and testing.
- **Rate Limiting**: Intelligent backoff and rate limiting (`core/rate_limiter.py`) to prevent 429 errors from upstream providers.
- **Cost Tracking**: (`core/cost_tracker.py`) calculates estimated token costs per request and logs them, allowing budget monitoring per project.
- **Retry Logic**: (`core/retry.py`) Exponential backoff for transient network or API errors.

## Agents

The system implements 18 distinct agents in `agents/`. Each agent inherits from `agents/base.py` and has a specific system prompt defined in `utils/prompts.py`.

### Anatomy of an Agent
```python
class CharacterDesignerAgent(BaseAgent):
    def __init__(self, provider: AIProvider):
        super().__init__(provider)
        self.role = "Character Designer"
    
    async def process(self, input_data: dict) -> dict:
        prompt = CHARACTER_DESIGN_PROMPT.format(**input_data)
        response = await self.provider.generate(prompt)
        return self.parse_response(response)
```

## Image Generation

Located in `agents/ai_image_generator.py`, the image generation pipeline:
1. Receives a semantic description of the scene or character.
2. Translates it into an optimized image prompt.
3. Calls the Pixtral API via the Image Provider.
4. Compresses and saves the resulting image to local storage (or cloud bucket).
5. Stores metadata (URL, prompt used) in the MySQL database.

## Best Practices for Modifying Prompts
- Always update `utils/prompts.py`.
- Keep prompts structured (JSON output requested where needed).
- Use few-shot examples within prompts if an agent's output format drifts.
- Run `make test` after prompt changes, as agent tests validate prompt rendering.
