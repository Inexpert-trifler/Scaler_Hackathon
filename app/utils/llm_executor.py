"""LLM execution helpers with real and mock implementations."""

from __future__ import annotations

import logging
import os
from abc import ABC, abstractmethod
from typing import Optional

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def execute(self, prompt: str, input_data: str) -> str:
        """Execute a prompt with input data and return the result."""
        pass


class MockExecutor(LLMProvider):
    """Mock LLM executor for testing without API calls."""

    def execute(self, prompt: str, input_data: str) -> str:
        """Simulate LLM response based on keywords."""
        prompt_lower = prompt.lower()
        
        # Summarization
        if "summarize" in prompt_lower or "summary" in prompt_lower:
            return "Prompt engineering improves AI reliability through clearer instructions and reduced ambiguity."
        
        # JSON conversion
        if "json" in prompt_lower or "convert" in prompt_lower:
            return '{"name": "John", "age": 25, "city": "Bangalore"}'
        
        # Reasoning/calculation
        if "step" in prompt_lower or "calculate" in prompt_lower or "solve" in prompt_lower:
            return "Step 1: 60 km/hour × 3 hours = 180 km. Therefore, the train travels 180 km in 3 hours."
        
        # Default
        return "Unable to determine task type. Please provide a clearer prompt with instructions."


class OpenAIExecutor(LLMProvider):
    """OpenAI GPT executor for real LLM integration."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4-turbo",
        temperature: float = 0.7,
        max_tokens: int = 500,
        timeout: int = 10,
    ):
        """Initialize OpenAI executor."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY not provided. Set it via parameter or environment variable."
            )

        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout

        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("OpenAI package not installed. Run: pip install openai")

    def execute(self, prompt: str, input_data: str) -> str:
        """Execute prompt via OpenAI API."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful assistant designed to solve tasks precisely. "
                            "Respond concisely and directly to the task requirements."
                        ),
                    },
                    {
                        "role": "user",
                        "content": f"{prompt}\n\nInput data: {input_data}",
                    },
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            return f"Error: {str(e)}"


def get_executor(provider: str = "openai", **kwargs) -> LLMProvider:
    """
    Factory function to get appropriate LLM executor.

    Args:
        provider: "openai" or "mock"
        **kwargs: Additional arguments for the executor

    Returns:
        LLMProvider instance
    """
    provider_lower = provider.lower()

    if provider_lower == "openai":
        return OpenAIExecutor(**kwargs)
    elif provider_lower == "mock":
        return MockExecutor()
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")


def run_prompt(prompt: str, input_data: str, provider: str = "mock") -> str:
    """
    Execute a prompt using the specified provider.

    Args:
        prompt: The prompt to execute
        input_data: Input data for the prompt
        provider: LLM provider to use ("mock" or "openai")

    Returns:
        LLM output as string
    """
    executor = get_executor(provider)
    return executor.execute(prompt, input_data)
