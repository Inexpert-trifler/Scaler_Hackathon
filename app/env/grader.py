"""Grading helpers for PromptGym."""

from __future__ import annotations

import json
import re
from difflib import SequenceMatcher


def _semantic_similarity(text1: str, text2: str) -> float:
    """Calculate semantic similarity using SequenceMatcher."""
    text1_clean = text1.lower().strip()
    text2_clean = text2.lower().strip()
    
    if not text1_clean or not text2_clean:
        return 0.0
    
    return SequenceMatcher(None, text1_clean, text2_clean).ratio()


def grade_summarization(expected: str, output: str) -> float:
    """
    Grade summarization task.
    
    Metrics:
    - Semantic similarity (50%)
    - Key concept coverage (30%)
    - Length appropriateness (20%)
    """
    expected_str = str(expected).lower().strip()
    output_str = str(output).lower().strip()
    
    # 1. Semantic similarity
    semantic_score = _semantic_similarity(expected_str, output_str)
    
    # 2. Key concept coverage (words from expected appearing in output)
    expected_words = set(expected_str.split())
    output_words = set(output_str.split())
    if expected_words:
        coverage = len(expected_words & output_words) / len(expected_words)
    else:
        coverage = 0.0
    
    # 3. Length appropriateness (5-15 words is good for summary)
    word_count = len(output_str.split())
    if 3 <= word_count <= 20:
        length_score = 1.0
    elif 1 <= word_count <= 30:
        length_score = 0.7
    else:
        length_score = 0.3
    
    # Weighted combination
    score = 0.5 * semantic_score + 0.3 * coverage + 0.2 * length_score
    return min(1.0, max(0.0, score))


def grade_json_conversion(expected: str, output: str) -> float:
    """
    Grade JSON conversion task.
    
    Metrics:
    - JSON validity (40%)
    - Key-value accuracy (40%)
    - Structure match (20%)
    """
    # 1. Try parsing both
    try:
        if isinstance(expected, str):
            expected_dict = json.loads(expected)
        else:
            expected_dict = expected
    except (json.JSONDecodeError, TypeError):
        expected_dict = None
    
    try:
        output_dict = json.loads(output)
    except (json.JSONDecodeError, TypeError):
        return 0.0  # Invalid JSON gets 0
    
    if not expected_dict:
        return 0.0
    
    # 2. Check key match
    expected_keys = set(expected_dict.keys())
    output_keys = set(output_dict.keys())
    
    if not expected_keys:
        return 0.0
    
    key_match_ratio = len(expected_keys & output_keys) / len(expected_keys)
    
    # 3. Value accuracy for matching keys
    value_accuracy = 0.0
    matching_keys = expected_keys & output_keys
    
    if matching_keys:
        matches = 0
        for key in matching_keys:
            exp_val = str(expected_dict[key]).lower().strip()
            out_val = str(output_dict[key]).lower().strip()
            if exp_val == out_val:
                matches += 1
        value_accuracy = matches / len(matching_keys)
    
    # Weighted combination
    score = 0.4 + 0.4 * key_match_ratio + 0.2 * value_accuracy
    return min(1.0, max(0.0, score))


def grade_reasoning(expected: str, output: str) -> float:
    """
    Grade reasoning/problem-solving task.
    
    Metrics:
    - Final answer correctness (50%)
    - Reasoning presence (30%)
    - Semantic alignment (20%)
    """
    expected_str = str(expected).lower().strip()
    output_str = str(output).lower().strip()
    
    # 1. Check if expected is contained in output (final answer check)
    answer_present = expected_str in output_str
    if answer_present:
        answer_score = 1.0
    else:
        # Fuzzy match for numerical answers
        answer_score = _semantic_similarity(expected_str, output_str)
    
    # 2. Reasoning indicators
    reasoning_keywords = [
        'step', 'first', 'second', 'third', 'finally', 'therefore', 
        'thus', 'because', 'since', 'hence', 'calculation', 'multiply', 
        'add', 'subtract', 'divide'
    ]
    reasoning_score = 0.0
    if any(keyword in output_str for keyword in reasoning_keywords):
        reasoning_indicators = sum(1 for kw in reasoning_keywords if kw in output_str)
        reasoning_score = min(1.0, reasoning_indicators / 3)
    
    # 3. Semantic similarity
    semantic_score = _semantic_similarity(expected_str, output_str)
    
    # Weighted combination
    score = 0.5 * answer_score + 0.3 * reasoning_score + 0.2 * semantic_score
    return min(1.0, max(0.0, score))


def grade_output(task: dict[str, object], output: str) -> float:
    """
    Grade output based on task difficulty and expected format.
    
    Returns a score between 0.0 and 1.0.
    """
    if not output or not isinstance(output, str):
        return 0.0
    
    difficulty = str(task.get("difficulty", "")).upper()
    expected = task.get("expected_output", "")
    
    if difficulty == "EASY":
        return grade_summarization(expected, output)
    elif difficulty == "MEDIUM":
        return grade_json_conversion(expected, output)
    elif difficulty == "HARD":
        return grade_reasoning(expected, output)
    else:
        # Fallback to semantic similarity
        return _semantic_similarity(str(expected), output)
