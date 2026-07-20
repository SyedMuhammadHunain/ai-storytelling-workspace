import os
import glob
import re

agent_files = glob.glob('src/storytelling_workspace/agents/*.py')
for file in agent_files:
    with open(file, 'r') as f:
        content = f.read()
    
    # Change def execute to async def execute
    content = re.sub(r'(\s+)def execute\(self,\s*bible:\s*StoryBible\)', r'\1async def execute(self, bible: StoryBible)', content)
    
    # Change asyncio.run to await
    content = re.sub(r'asyncio\.run\((self\._[^)]+\(.*?)\)', r'await \1', content)
    
    # For ai_agent.py, fix asyncio.run(cls._cache.get_stats())
    content = re.sub(r'asyncio\.run\(cls\._cache\.get_stats\(\)\)', r'await cls._cache.get_stats()', content)

    with open(file, 'w') as f:
        f.write(content)

print("Refactored agents.")
