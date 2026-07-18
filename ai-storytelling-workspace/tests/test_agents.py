"""Tests for base agent classes."""

import pytest
from storytelling_workspace.agents.base import BaseAgent, MockAgent
from storytelling_workspace.story_bible import StoryBible


class TestAgent(BaseAgent):
    """Concrete test implementation of BaseAgent."""
    
    def execute(self, bible: StoryBible):
        """Test execution."""
        self.log_start()
        self.log_action("Performing test action")
        self.record_changes(bible, {"test": True}, "Test execution")
        self.log_end()
        return {"success": True}


def test_base_agent_initialization():
    """Test BaseAgent can be initialized."""
    agent = TestAgent(name="TestAgent")
    
    assert agent.name == "TestAgent"
    assert agent.logger is not None


def test_base_agent_logging():
    """Test BaseAgent logging methods."""
    agent = TestAgent(name="TestAgent")
    
    # These should not raise exceptions
    agent.log_start()
    agent.log_action("Test action")
    agent.log_end(success=True)
    agent.log_end(success=False)


def test_base_agent_record_changes():
    """Test BaseAgent can record changes to Story Bible."""
    agent = TestAgent(name="TestAgent")
    bible = StoryBible(project_name="Test")
    
    initial_deltas = len(bible.deltas)
    
    agent.record_changes(
        bible,
        changes={"added": "something"},
        summary="Test change"
    )
    
    assert len(bible.deltas) == initial_deltas + 1
    assert bible.deltas[-1].agent_name == "TestAgent"
    assert bible.deltas[-1].summary == "Test change"


def test_base_agent_execute():
    """Test BaseAgent execute method."""
    agent = TestAgent(name="TestAgent")
    bible = StoryBible(project_name="Test")
    
    result = agent.execute(bible)
    
    assert result["success"] is True
    assert len(bible.deltas) == 1


def test_mock_agent_initialization():
    """Test MockAgent can be initialized."""
    agent = MockAgent(name="MockAgent")
    
    assert agent.name == "MockAgent"
    assert agent.mock_output == "Mock output from MockAgent"


def test_mock_agent_custom_output():
    """Test MockAgent with custom output."""
    custom_output = "Custom mock output"
    agent = MockAgent(name="MockAgent", mock_output=custom_output)
    
    assert agent.mock_output == custom_output


def test_mock_agent_execute():
    """Test MockAgent execute method."""
    agent = MockAgent(name="MockAgent")
    bible = StoryBible(project_name="Test")
    
    result = agent.execute(bible)
    
    assert result["success"] is True
    assert "output" in result
    assert "timestamp" in result
    assert result["output"] == "Mock output from MockAgent"


def test_mock_agent_records_execution():
    """Test MockAgent records its execution in Story Bible."""
    agent = MockAgent(name="MockAgent")
    bible = StoryBible(project_name="Test")
    
    agent.execute(bible)
    
    assert len(bible.deltas) == 1
    assert bible.deltas[0].agent_name == "MockAgent"
    assert "executed with mock output" in bible.deltas[0].summary


def test_mock_agent_generate_mock_text():
    """Test MockAgent can generate mock text from templates."""
    agent = MockAgent(name="MockAgent")
    
    template = "Hello {name}, welcome to {place}!"
    result = agent.generate_mock_text(template, name="Alice", place="Wonderland")
    
    assert result == "Hello Alice, welcome to Wonderland!"


def test_multiple_agents_execution():
    """Test multiple agents can execute and record changes."""
    bible = StoryBible(project_name="Test")
    
    agent1 = MockAgent(name="Agent1")
    agent2 = MockAgent(name="Agent2")
    agent3 = MockAgent(name="Agent3")
    
    agent1.execute(bible)
    agent2.execute(bible)
    agent3.execute(bible)
    
    assert len(bible.deltas) == 3
    assert bible.deltas[0].agent_name == "Agent1"
    assert bible.deltas[1].agent_name == "Agent2"
    assert bible.deltas[2].agent_name == "Agent3"


def test_agent_execution_updates_version():
    """Test agent execution increments Story Bible version."""
    bible = StoryBible(project_name="Test")
    initial_version = bible.version
    
    agent = MockAgent(name="MockAgent")
    agent.execute(bible)
    
    assert bible.version > initial_version
