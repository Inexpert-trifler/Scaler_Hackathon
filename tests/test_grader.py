"""Tests for the grader module."""

import json

import pytest

from app.grader import Grader
from app.tasks.loader import TaskLoader


@pytest.fixture
def grader():
    """Create grader instance."""
    return Grader()


@pytest.fixture
def task_loader():
    """Create task loader instance."""
    return TaskLoader()


def test_perfect_score_summarization(grader, task_loader):
    """Test perfect score for summarization task."""
    task = task_loader.get_task("easy")
    # Assume task type is summarization
    task["type"] = "summarization"

    # Perfect output matches expected
    output = task.get("expected_output", "")
    score, signals = grader.grade(output, task)

    assert 0.0 <= score <= 1.0
    assert score >= 0.8  # Should be high score


def test_empty_output(grader, task_loader):
    """Test grading empty output."""
    task = task_loader.get_task("easy")
    score, signals = grader.grade("", task)

    assert 0.0 <= score <= 1.0
    assert score < 0.5  # Empty output should have low score


def test_json_valid_structure(grader, task_loader):
    """Test JSON extraction with valid structure."""
    task = task_loader.get_task("medium")
    task["type"] = "json_extraction"
    
    if "required_keys" in task:
        # Create valid JSON output
        output = json.dumps({key: "value" for key in task.get("required_keys", [])})
        score, signals = grader.grade(output, task)

        assert 0.0 <= score <= 1.0
        assert "json_structure" in signals


def test_json_invalid_structure(grader, task_loader):
    """Test JSON extraction with invalid structure."""
    task = task_loader.get_task("medium")
    task["type"] = "json_extraction"
    
    # Invalid JSON
    output = "this is not valid json {{"
    score, signals = grader.grade(output, task)

    assert 0.0 <= score <= 1.0
    assert score < 0.5


def test_reasoning_with_answer_variants(grader, task_loader):
    """Test reasoning task with answer variants."""
    task = task_loader.get_task("hard")
    task["type"] = "reasoning"

    # Try to match one of the answer variants
    answer_variants = task.get("answer_variants", [])
    if answer_variants:
        output = str(answer_variants[0])
        score, signals = grader.grade(output, task)

        assert 0.0 <= score <= 1.0
        assert "answer_match" in signals


def test_score_bounds(grader, task_loader):
    """Test that all scores are properly bounded."""
    for difficulty in ["easy", "medium", "hard"]:
        task = task_loader.get_task(difficulty)
        
        # Test with various outputs
        outputs = [
            "",
            "a",
            "short output",
            "This is a much longer output that contains more information and details about the topic",
            json.dumps({"key": "value"}),
        ]

        for output in outputs:
            score, signals = grader.grade(output, task)
            
            # Main score must be in [0.0, 1.0]
            assert 0.0 <= score <= 1.0
            
            # All signal scores must be in [0.0, 1.0]
            for signal_value in signals.values():
                assert 0.0 <= signal_value <= 1.0


def test_keyword_coverage(grader, task_loader):
    """Test keyword coverage scoring."""
    task = task_loader.get_task("easy")
    keywords = task.get("keywords", [])

    if keywords:
        # Output with all keywords
        output_with_keywords = " ".join(keywords) + " additional text"
        score1, signals1 = grader.grade(output_with_keywords, task)

        # Output with no keywords
        output_without_keywords = "completely different text that has nothing to do with the task"
        score2, signals2 = grader.grade(output_without_keywords, task)

        # Output with keywords should score better
        assert score1 > score2


def test_length_penalty(grader, task_loader):
    """Test length penalty scoring."""
    task = task_loader.get_task("easy")
    original_output = task.get("expected_output", "")

    if original_output:
        # Output with correct length should score well
        output_correct_length = original_output
        score1, signals1 = grader.grade(output_correct_length, task)

        # Very short output
        output_very_short = "too short"
        score2, signals2 = grader.grade(output_very_short, task)

        # Very long output (2x expected)
        output_very_long = original_output * 2
        score3, signals3 = grader.grade(output_very_long, task)

        # Correct length should be best
        assert score1 >= score2
        assert score1 >= score3
