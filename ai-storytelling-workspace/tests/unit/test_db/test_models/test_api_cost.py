"""
Unit tests for APICost model.
"""

import pytest
from decimal import Decimal

from storytelling_workspace.db.models import APICost, APIType


def test_api_cost_creation():
    """Test creating an APICost instance."""
    cost = APICost(
        project_id="test-project-id",
        provider="mistral",
        model="mistral-large-latest",
        api_type=APIType.TEXT,
        tokens_used=1000,
        cost=Decimal("0.0100"),
        success=True,
    )
    
    assert cost.project_id == "test-project-id"
    assert cost.provider == "mistral"
    assert cost.model == "mistral-large-latest"
    assert cost.api_type == APIType.TEXT
    assert cost.tokens_used == 1000
    assert cost.cost == Decimal("0.0100")
    assert cost.success is True


def test_api_cost_type_properties():
    """Test API type properties."""
    text_cost = APICost(
        project_id="test-id",
        provider="openai",
        model="gpt-4o",
        api_type=APIType.TEXT,
        tokens_used=500,
        cost=Decimal("0.0050"),
    )
    
    assert text_cost.is_text_api
    assert not text_cost.is_image_api
    
    image_cost = APICost(
        project_id="test-id",
        provider="mistral",
        model="pixtral-large-latest",
        api_type=APIType.IMAGE,
        images_generated=1,
        cost=Decimal("0.0400"),
    )
    
    assert image_cost.is_image_api
    assert not image_cost.is_text_api


def test_api_cost_per_token():
    """Test cost_per_token property."""
    cost = APICost(
        project_id="test-id",
        provider="mistral",
        model="mistral-large-latest",
        api_type=APIType.TEXT,
        tokens_used=1000,
        cost=Decimal("0.0100"),
    )
    
    assert cost.cost_per_token == Decimal("0.0000100")
    
    # Test with no tokens
    cost_no_tokens = APICost(
        project_id="test-id",
        provider="mistral",
        model="test",
        api_type=APIType.TEXT,
        tokens_used=None,
        cost=Decimal("0.0100"),
    )
    
    assert cost_no_tokens.cost_per_token is None


def test_api_cost_per_image():
    """Test cost_per_image property."""
    cost = APICost(
        project_id="test-id",
        provider="mistral",
        model="pixtral-large-latest",
        api_type=APIType.IMAGE,
        images_generated=2,
        cost=Decimal("0.0800"),
    )
    
    assert cost.cost_per_image == Decimal("0.0400")
    
    # Test with no images
    cost_no_images = APICost(
        project_id="test-id",
        provider="mistral",
        model="test",
        api_type=APIType.IMAGE,
        images_generated=None,
        cost=Decimal("0.0400"),
    )
    
    assert cost_no_images.cost_per_image is None


def test_api_cost_failed_request():
    """Test failed API request."""
    cost = APICost(
        project_id="test-id",
        provider="openai",
        model="gpt-4o",
        api_type=APIType.TEXT,
        tokens_used=0,
        cost=Decimal("0.0000"),
        success=False,
        error_message="Rate limit exceeded",
    )
    
    assert cost.success is False
    assert cost.error_message == "Rate limit exceeded"


def test_api_cost_repr():
    """Test string representation."""
    cost = APICost(
        project_id="test-id",
        provider="mistral",
        model="mistral-large-latest",
        api_type=APIType.TEXT,
        tokens_used=500,
        cost=Decimal("0.0050"),
    )
    
    repr_str = repr(cost)
    
    assert "APICost" in repr_str
    assert "mistral" in repr_str
    assert "mistral-large-latest" in repr_str
    assert "0.0050" in repr_str
