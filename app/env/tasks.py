"""Task definitions for the PromptGym environment."""

from __future__ import annotations


TASKS = [
    # EASY - Summarization
    {
        "difficulty": "EASY",
        "task_description": "Summarize the given text in one sentence",
        "input_data": (
            "Prompt engineering helps AI systems produce more reliable answers by "
            "making instructions clearer, reducing ambiguity, and specifying the "
            "format of the response."
        ),
        "expected_output": "Prompt engineering improves AI reliability through clearer instructions.",
    },
    {
        "difficulty": "EASY",
        "task_description": "Create a brief summary of the key points",
        "input_data": (
            "Machine learning models learn patterns from data. Deep learning uses neural networks "
            "with multiple layers. Transformers have become the state-of-the-art for NLP tasks."
        ),
        "expected_output": "Machine learning models learn patterns; deep learning uses neural networks; transformers excel at NLP.",
    },
    {
        "difficulty": "EASY",
        "task_description": "Condense this information into one sentence",
        "input_data": (
            "The Renaissance was a cultural movement spanning centuries. It originated in Italy during "
            "the 14th century and spread throughout Europe. It marked the transition from medieval to modern times."
        ),
        "expected_output": "The Renaissance was a cultural movement that originated in 14th-century Italy and marked the transition to modern times.",
    },
    # MEDIUM - JSON Conversion
    {
        "difficulty": "MEDIUM",
        "task_description": "Convert text into JSON format",
        "input_data": "John is 25 and lives in Bangalore",
        "expected_output": '{"name": "John", "age": 25, "city": "Bangalore"}',
    },
    {
        "difficulty": "MEDIUM",
        "task_description": "Parse the following into a JSON object",
        "input_data": "Product: Laptop, Price: 999.99, Stock: 45 units",
        "expected_output": '{"product": "Laptop", "price": 999.99, "stock": 45}',
    },
    {
        "difficulty": "MEDIUM",
        "task_description": "Convert to structured JSON format",
        "input_data": "Sarah works as a Software Engineer at TechCorp with salary 120000",
        "expected_output": '{"name": "Sarah", "position": "Software Engineer", "company": "TechCorp", "salary": 120000}',
    },
    # HARD - Reasoning/Problem Solving
    {
        "difficulty": "HARD",
        "task_description": "Solve reasoning problem step-by-step",
        "input_data": "If a train travels 60km in 1 hour, how far in 3 hours?",
        "expected_output": "180 km",
    },
    {
        "difficulty": "HARD",
        "task_description": "Calculate and explain the solution",
        "input_data": "A book costs 15 dollars. You buy 4 books and get 10% discount. How much do you pay?",
        "expected_output": "54 dollars",
    },
    {
        "difficulty": "HARD",
        "task_description": "Solve this step-by-step problem",
        "input_data": "If 5 workers can build a wall in 20 days, how many days does 10 workers need?",
        "expected_output": "10 days",
    },
]


def get_tasks() -> list[dict[str, object]]:
    """Return the available PromptGym tasks."""
    return TASKS.copy()


def get_tasks_by_difficulty(difficulty: str) -> list[dict[str, object]]:
    """Get tasks filtered by difficulty level."""
    return [t for t in TASKS if t.get("difficulty") == difficulty]
