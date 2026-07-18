"""Cost tracking for AI provider API usage."""

import logging
from typing import Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class APICall:
    """Record of a single API call."""
    timestamp: datetime
    provider: str
    model: str
    operation: str  # "text_generation", "image_generation", etc.
    tokens_used: int
    estimated_cost: float
    success: bool
    error: Optional[str] = None


@dataclass
class UsageStats:
    """Aggregated usage statistics."""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    total_tokens: int = 0
    total_cost: float = 0.0
    calls_by_provider: Dict[str, int] = field(default_factory=dict)
    tokens_by_provider: Dict[str, int] = field(default_factory=dict)
    cost_by_provider: Dict[str, float] = field(default_factory=dict)
    calls_by_model: Dict[str, int] = field(default_factory=dict)


class CostTracker:
    """
    Tracks AI API usage and costs.
    
    Records all API calls with token usage and estimated costs.
    Provides aggregated statistics and can export usage reports.
    """
    
    # Cost per 1M tokens (approximate, as of 2024)
    COST_PER_MILLION_TOKENS = {
        "mistral": {
            "mistral-large-latest": {"input": 3.0, "output": 9.0},
            "mistral-medium-latest": {"input": 2.5, "output": 7.5},
            "mistral-small-latest": {"input": 1.0, "output": 3.0},
            "pixtral-large-latest": {"input": 0.0, "output": 0.0},  # Free tier
        },
        "openai": {
            "gpt-4o": {"input": 5.0, "output": 15.0},
            "gpt-3.5-turbo": {"input": 0.5, "output": 1.5},
            "dall-e-3": {"per_image": 0.04},  # $0.04 per image (1024x1024)
        }
    }
    
    def __init__(self, log_file: Optional[Path] = None):
        """
        Initialize cost tracker.
        
        Args:
            log_file: Optional file path to persist usage logs
        """
        self.log_file = log_file
        self._calls: List[APICall] = []
        self._stats = UsageStats()
        
        if log_file and log_file.exists():
            self._load_from_file()
    
    def record_call(
        self,
        provider: str,
        model: str,
        operation: str,
        tokens_used: int,
        success: bool = True,
        error: Optional[str] = None,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None
    ) -> float:
        """
        Record an API call and calculate cost.
        
        Args:
            provider: Provider name (e.g., "mistral", "openai")
            model: Model name
            operation: Operation type
            tokens_used: Total tokens used
            success: Whether call succeeded
            error: Error message if failed
            input_tokens: Input tokens (for separate pricing)
            output_tokens: Output tokens (for separate pricing)
            
        Returns:
            Estimated cost in USD
        """
        # Calculate cost
        cost = self._calculate_cost(
            provider,
            model,
            tokens_used,
            input_tokens,
            output_tokens
        )
        
        # Create call record
        call = APICall(
            timestamp=datetime.now(),
            provider=provider,
            model=model,
            operation=operation,
            tokens_used=tokens_used,
            estimated_cost=cost,
            success=success,
            error=error
        )
        
        # Store call
        self._calls.append(call)
        
        # Update stats
        self._update_stats(call)
        
        # Log
        if success:
            logger.info(
                f"API call recorded: {provider}/{model} - "
                f"{tokens_used} tokens, ${cost:.4f}"
            )
        else:
            logger.warning(
                f"Failed API call: {provider}/{model} - {error}"
            )
        
        # Persist if log file configured
        if self.log_file:
            self._append_to_file(call)
        
        return cost
    
    def _calculate_cost(
        self,
        provider: str,
        model: str,
        total_tokens: int,
        input_tokens: Optional[int] = None,
        output_tokens: Optional[int] = None
    ) -> float:
        """
        Calculate estimated cost for API call.
        
        Args:
            provider: Provider name
            model: Model name
            total_tokens: Total tokens
            input_tokens: Input tokens (if separate pricing)
            output_tokens: Output tokens (if separate pricing)
            
        Returns:
            Estimated cost in USD
        """
        provider_lower = provider.lower()
        
        if provider_lower not in self.COST_PER_MILLION_TOKENS:
            logger.warning(f"Unknown provider for cost calculation: {provider}")
            return 0.0
        
        provider_costs = self.COST_PER_MILLION_TOKENS[provider_lower]
        
        if model not in provider_costs:
            logger.warning(f"Unknown model for cost calculation: {model}")
            return 0.0
        
        model_costs = provider_costs[model]
        
        # Handle image generation (per-image pricing)
        if "per_image" in model_costs:
            return model_costs["per_image"]
        
        # Handle text generation (per-token pricing)
        if input_tokens is not None and output_tokens is not None:
            # Separate input/output pricing
            input_cost = (input_tokens / 1_000_000) * model_costs["input"]
            output_cost = (output_tokens / 1_000_000) * model_costs["output"]
            return input_cost + output_cost
        else:
            # Use average of input/output for total tokens
            avg_cost = (model_costs["input"] + model_costs["output"]) / 2
            return (total_tokens / 1_000_000) * avg_cost
    
    def _update_stats(self, call: APICall) -> None:
        """Update aggregated statistics."""
        self._stats.total_calls += 1
        
        if call.success:
            self._stats.successful_calls += 1
        else:
            self._stats.failed_calls += 1
        
        self._stats.total_tokens += call.tokens_used
        self._stats.total_cost += call.estimated_cost
        
        # By provider
        self._stats.calls_by_provider[call.provider] = \
            self._stats.calls_by_provider.get(call.provider, 0) + 1
        self._stats.tokens_by_provider[call.provider] = \
            self._stats.tokens_by_provider.get(call.provider, 0) + call.tokens_used
        self._stats.cost_by_provider[call.provider] = \
            self._stats.cost_by_provider.get(call.provider, 0.0) + call.estimated_cost
        
        # By model
        model_key = f"{call.provider}/{call.model}"
        self._stats.calls_by_model[model_key] = \
            self._stats.calls_by_model.get(model_key, 0) + 1
    
    def get_stats(self) -> Dict[str, any]:
        """
        Get current usage statistics.
        
        Returns:
            Dictionary with aggregated stats
        """
        return {
            "total_calls": self._stats.total_calls,
            "successful_calls": self._stats.successful_calls,
            "failed_calls": self._stats.failed_calls,
            "success_rate": (
                (self._stats.successful_calls / self._stats.total_calls * 100)
                if self._stats.total_calls > 0 else 0.0
            ),
            "total_tokens": self._stats.total_tokens,
            "total_cost_usd": round(self._stats.total_cost, 4),
            "calls_by_provider": self._stats.calls_by_provider,
            "tokens_by_provider": self._stats.tokens_by_provider,
            "cost_by_provider": {
                k: round(v, 4) for k, v in self._stats.cost_by_provider.items()
            },
            "calls_by_model": self._stats.calls_by_model,
            "average_tokens_per_call": (
                self._stats.total_tokens // self._stats.total_calls
                if self._stats.total_calls > 0 else 0
            ),
            "average_cost_per_call": (
                self._stats.total_cost / self._stats.total_calls
                if self._stats.total_calls > 0 else 0.0
            )
        }
    
    def get_recent_calls(self, limit: int = 10) -> List[Dict[str, any]]:
        """
        Get recent API calls.
        
        Args:
            limit: Maximum number of calls to return
            
        Returns:
            List of recent calls
        """
        recent = self._calls[-limit:] if len(self._calls) > limit else self._calls
        
        return [
            {
                "timestamp": call.timestamp.isoformat(),
                "provider": call.provider,
                "model": call.model,
                "operation": call.operation,
                "tokens": call.tokens_used,
                "cost_usd": round(call.estimated_cost, 4),
                "success": call.success,
                "error": call.error
            }
            for call in reversed(recent)
        ]
    
    def export_report(self, output_file: Path) -> None:
        """
        Export detailed usage report to JSON file.
        
        Args:
            output_file: Path to output file
        """
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": self.get_stats(),
            "recent_calls": self.get_recent_calls(limit=100),
            "all_calls_count": len(self._calls)
        }
        
        output_file.write_text(json.dumps(report, indent=2))
        logger.info(f"Usage report exported to: {output_file}")
    
    def _append_to_file(self, call: APICall) -> None:
        """Append call to log file."""
        try:
            with open(self.log_file, 'a') as f:
                call_data = {
                    "timestamp": call.timestamp.isoformat(),
                    "provider": call.provider,
                    "model": call.model,
                    "operation": call.operation,
                    "tokens": call.tokens_used,
                    "cost": call.estimated_cost,
                    "success": call.success,
                    "error": call.error
                }
                f.write(json.dumps(call_data) + "\n")
        except Exception as e:
            logger.error(f"Failed to append to log file: {e}")
    
    def _load_from_file(self) -> None:
        """Load previous calls from log file."""
        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        call = APICall(
                            timestamp=datetime.fromisoformat(data["timestamp"]),
                            provider=data["provider"],
                            model=data["model"],
                            operation=data["operation"],
                            tokens_used=data["tokens"],
                            estimated_cost=data["cost"],
                            success=data["success"],
                            error=data.get("error")
                        )
                        self._calls.append(call)
                        self._update_stats(call)
            
            logger.info(f"Loaded {len(self._calls)} calls from log file")
        except Exception as e:
            logger.error(f"Failed to load from log file: {e}")
    
    def reset_stats(self) -> None:
        """Reset all statistics (keeps log file intact)."""
        self._calls.clear()
        self._stats = UsageStats()
        logger.info("Cost tracker stats reset")
