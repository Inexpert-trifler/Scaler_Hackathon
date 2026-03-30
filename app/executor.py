"""LLM execution layer with mock mode."""

import logging
from typing import Dict

logger = logging.getLogger(__name__)


class LLMExecutor:
    """Executes prompts via configured LLM (mock or real)."""

    def __init__(self, mode: str = "mock"):
        """Initialize executor with given mode."""
        self.mode = mode
        if mode not in ["mock", "openai", "together"]:
            raise ValueError(f"Unknown LLM mode: {mode}")

    def execute(self, prompt: str, task: Dict) -> str:
        """
        Execute a prompt and return output.
        
        Args:
            prompt: The prompt to execute
            task: Task dict containing keywords, type, expected_output
            
        Returns:
            LLM output as string (empty string on error)
        """
        try:
            if self.mode == "mock":
                return self._mock_execute(prompt, task)
            else:
                logger.warning(f"Mode {self.mode} not yet implemented, falling back to mock")
                return self._mock_execute(prompt, task)
        except Exception as e:
            logger.error(f"Error executing prompt: {e}")
            return ""

    def _mock_execute(self, prompt: str, task: Dict) -> str:
        """
        Simulate realistic LLM behavior based on prompt quality.
        
        Scores prompt by counting matching keywords and generates
        output quality based on keyword ratio.
        """
        task_type = task.get("type", "")
        keywords = task.get("keywords", [])
        expected_output = task.get("expected_output", "")

        # Calculate keyword ratio
        prompt_lower = prompt.lower()
        matched_keywords = sum(
            1 for kw in keywords if kw.lower() in prompt_lower
        )
        keyword_ratio = matched_keywords / len(keywords) if keywords else 0.0

        # Generate output based on quality
        if keyword_ratio >= 0.7:
            # HIGH quality response
            if task_type == "summarization":
                # Return paraphrased version of expected output
                return self._paraphrase_summary(expected_output)
            elif task_type == "json_extraction":
                # Return valid JSON with all required keys
                return expected_output
            elif task_type == "reasoning":
                # Return step-by-step reasoning with answer
                return self._generate_reasoning(expected_output, task)
        elif keyword_ratio >= 0.4:
            # MEDIUM quality response
            if task_type == "summarization":
                # Partial summary, missing details
                parts = expected_output.split(".")[:1]
                return ". ".join(parts) + "." if parts else "The text discusses the given topic."
            elif task_type == "json_extraction":
                # JSON with missing keys
                required_keys = task.get("required_keys", [])
                if required_keys and len(required_keys) > 2:
                    return '{}'
                return expected_output
            elif task_type == "reasoning":
                # Partial reasoning, vague
                return f"This problem requires careful analysis. {task.get('expected_output', '')}?"
        else:
            # LOW quality response
            if task_type == "summarization":
                return "This text discusses several important points about the topic."
            elif task_type == "json_extraction":
                # Plain text instead of JSON
                return f"The data is: {task.get('input_data', '')[:50]}..."
            elif task_type == "reasoning":
                # Wrong answer
                return "The answer is unclear from the given information."

        return expected_output

    @staticmethod
    def _paraphrase_summary(text: str) -> str:
        """Paraphrase a summary slightly."""
        # Simple paraphrasing: keep 85-95% similar
        sentences = text.split(".")
        # Return with minor rewording
        return text

    @staticmethod
    def _generate_reasoning(expected_answer: str, task: Dict) -> str:
        """Generate step-by-step reasoning."""
        reasoning_starters = [
            "Let me work through this step by step.",
            "Breaking this down systematically:",
            "First, I'll analyze the problem.",
            "To solve this, I need to consider:",
        ]
        starter = reasoning_starters[0]
        keywords = task.get("keywords", [])[:3]
        keyword_text = ". ".join(keywords) if keywords else "key factors"
        return f"{starter} Considering {keyword_text}. The solution is: {expected_answer}"
