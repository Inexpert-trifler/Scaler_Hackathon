"""Multi-signal grading system."""

import json
import logging
import re
from typing import Tuple, Dict

logger = logging.getLogger(__name__)


class Grader:
    """Multi-signal grading system for evaluating LLM outputs."""

    def grade(self, output: str, task: Dict) -> Tuple[float, Dict]:
        """
        Grade output against task.
        
        Returns:
            (final_score, signals_dict) where final_score in [0.0, 1.0]
        """
        task_type = task.get("type", "")
        expected_output = task.get("expected_output", "")
        signals = {}

        # Compute all signals
        signals["token_f1"] = self._token_f1(output, expected_output)
        signals["keyword_coverage"] = self._keyword_coverage(output, task)
        signals["length_penalty"] = self._length_penalty(output, expected_output)

        if task_type == "json_extraction":
            signals["json_structure"] = self._json_structure_score(output, task)
            final_score = (
                0.50 * signals["json_structure"]
                + 0.30 * signals["token_f1"]
                + 0.20 * signals["keyword_coverage"]
            )
        elif task_type == "reasoning":
            signals["answer_match"] = self._answer_match_score(output, task)
            final_score = (
                0.60 * signals["answer_match"]
                + 0.25 * signals["keyword_coverage"]
                + 0.15 * signals["token_f1"]
            )
        else:  # summarization
            final_score = (
                0.35 * signals["token_f1"]
                + 0.35 * signals["keyword_coverage"]
                + 0.30 * signals["length_penalty"]
            )

        # Clip and round strictly within (0, 1)
        final_score = max(0.01, min(0.99, final_score))
        final_score = round(final_score, 4)

        return final_score, signals

    @staticmethod
    def _token_f1(output: str, expected: str) -> float:
        """Compute F1 over word-level tokens."""
        output_tokens = set(Grader._tokenize(output))
        expected_tokens = set(Grader._tokenize(expected))

        if not output_tokens or not expected_tokens:
            return 0.0

        intersection = len(output_tokens & expected_tokens)
        precision = intersection / len(output_tokens) if output_tokens else 0.0
        recall = intersection / len(expected_tokens) if expected_tokens else 0.0

        if precision + recall == 0:
            return 0.0
        f1 = 2 * (precision * recall) / (precision + recall)
        return f1

    @staticmethod
    def _tokenize(text: str) -> list:
        """Tokenize text to words (lowercase, no punctuation)."""
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", "", text)
        return text.split()

    @staticmethod
    def _keyword_coverage(output: str, task: Dict) -> float:
        """Fraction of keywords found in output."""
        keywords = task.get("keywords", [])
        if not keywords:
            return 0.0

        output_lower = output.lower()
        matched = sum(1 for kw in keywords if kw.lower() in output_lower)
        return matched / len(keywords)

    @staticmethod
    def _length_penalty(output: str, expected: str) -> float:
        """Penalize unusual length ratios."""
        output_len = len(output.split())
        expected_len = max(len(expected.split()), 1)

        ratio = output_len / expected_len
        if 0.5 <= ratio <= 2.0:
            return 1.0
        return max(0.0, 1.0 - abs(ratio - 1.0))

    @staticmethod
    def _json_structure_score(output: str, task: Dict) -> float:
        """Score JSON structure validity and key presence."""
        try:
            parsed = json.loads(output)
            if not isinstance(parsed, dict):
                return 0.0
        except (json.JSONDecodeError, ValueError):
            return 0.0

        required_keys = task.get("required_keys", [])
        if not required_keys:
            return 0.5

        matched = sum(1 for key in required_keys if key in parsed)
        return matched / len(required_keys)

    @staticmethod
    def _answer_match_score(output: str, task: Dict) -> float:
        """Score if answer appears in output."""
        answer_variants = task.get("answer_variants", [])
        expected = task.get("expected_output", "")

        output_lower = output.lower()

        # Check for exact variant match
        for variant in answer_variants:
            if variant.lower() in output_lower:
                return 1.0

        # Check for partial expected output match
        if expected.lower() in output_lower:
            return 0.8

        # Check if words from expected appear
        expected_words = set(Grader._tokenize(expected))
        output_words = set(Grader._tokenize(output))
        if expected_words and output_words:
            overlap = len(expected_words & output_words) / len(expected_words)
            if overlap >= 0.5:
                return 0.5

        return 0.0
