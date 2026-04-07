"""PyTorch-based reward model for scoring prompt quality."""

import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

# Try to import torch, but don't fail if not available
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch not available. Reward scorer will use fallback mode.")


class PromptFeatureExtractor:
    """Extracts numerical features from prompt/output/task."""

    @staticmethod
    def extract(prompt: str, output: str, task: dict) -> list:
        """
        Extract features as list of 6 floats.
        
        Returns: [prompt_len, output_len, keyword_ratio, instruction_words,
                  output_non_empty, overlap]
        """
        # Feature 1: prompt length (normalized)
        prompt_len = min(len(prompt.split()) / 100.0, 1.0)

        # Feature 2: output length (normalized)
        output_len = min(len(output.split()) / 100.0, 1.0)

        # Feature 3: keyword ratio
        keywords = task.get("keywords", [])
        matched = sum(1 for kw in keywords if kw.lower() in prompt.lower())
        keyword_ratio = matched / len(keywords) if keywords else 0.0

        # Feature 4: has instruction words
        instruction_words = [
            "please", "you are", "task:", "step", "format", "json",
            "summarize", "analyze", "explain", "extract", "solve"
        ]
        has_instructions = 1.0 if any(
            word in prompt.lower() for word in instruction_words
        ) else 0.0

        # Feature 5: output non-empty
        output_non_empty = 1.0 if len(output.split()) > 5 else 0.0

        # Feature 6: prompt-output overlap
        prompt_words = set(prompt.lower().split())
        output_words = set(output.lower().split())
        if prompt_words and output_words:
            overlap = len(prompt_words & output_words) / max(
                len(prompt_words), len(output_words)
            )
        else:
            overlap = 0.0

        return [
            prompt_len,
            output_len,
            keyword_ratio,
            has_instructions,
            output_non_empty,
            overlap,
        ]


if TORCH_AVAILABLE:

    class RewardMLP(nn.Module):
        """Multi-layer perceptron for reward prediction."""

        def __init__(self, input_size: int = 6):
            """Initialize MLP architecture."""
            super().__init__()
            self.net = nn.Sequential(
                nn.Linear(input_size, 32),
                nn.ReLU(),
                nn.Dropout(0.1),
                nn.Linear(32, 16),
                nn.ReLU(),
                nn.Linear(16, 1),
                nn.Sigmoid(),
            )

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            """Forward pass returns scalar in (0, 1)."""
            return self.net(x)


class TorchRewardScorer:
    """Optional PyTorch-based reward scorer."""

    def __init__(self):
        """Initialize scorer."""
        self.available = TORCH_AVAILABLE
        if self.available:
            self.model = RewardMLP()
            self.model.eval()
            logger.info("TorchRewardScorer initialized")
        else:
            self.model = None

    def score(self, prompt: str, output: str, task: dict) -> float:
        """
        Score using PyTorch model if available.
        
        Returns: float in [0.0, 1.0]
        """
        if not self.available:
            return 0.5

        try:
            features = PromptFeatureExtractor.extract(prompt, output, task)
            x = torch.tensor(features, dtype=torch.float32).unsqueeze(0)

            with torch.no_grad():
                score = self.model(x).item()

            return float(score)
        except Exception as e:
            logger.error(f"Error in torch scorer: {e}")
            return 0.5

    @staticmethod
    def blend_with_grader(
        grader_score: float, torch_score: float, alpha: float = 0.7
    ) -> float:
        """Blend grader and torch scores."""
        blended = alpha * grader_score + (1 - alpha) * torch_score
        return min(0.9999, max(0.0001, blended))


def pretrain_on_synthetic_data(scorer: TorchRewardScorer) -> None:
    """Pretrain model on synthetic data."""
    if not TORCH_AVAILABLE or scorer.model is None:
        logger.info("Skipping PyTorch pretraining (torch not available)")
        return

    logger.info("Pretraining PyTorch reward model on synthetic data...")

    # Generate synthetic data
    num_samples = 200
    X = torch.rand(num_samples, 6)

    # Generate labels based on heuristic
    labels = (
        0.4 * X[:, 2]  # keyword_ratio
        + 0.3 * X[:, 3]  # has_instructions
        + 0.2 * X[:, 4]  # output_non_empty
        + 0.1 * torch.randn(num_samples).abs()  # random noise
    )
    labels = torch.clamp(labels, 0.0, 1.0).unsqueeze(1)

    # Train
    optimizer = optim.Adam(scorer.model.parameters(), lr=0.01)
    criterion = nn.MSELoss()

    scorer.model.train()
    for epoch in range(50):
        optimizer.zero_grad()
        y_pred = scorer.model(X)
        loss = criterion(y_pred, labels)
        loss.backward()
        optimizer.step()

        if (epoch + 1) % 10 == 0:
            logger.debug(f"Epoch {epoch + 1}/50, Loss: {loss.item():.4f}")

    scorer.model.eval()
    logger.info(f"Pretraining complete. Final loss: {loss.item():.4f}")
