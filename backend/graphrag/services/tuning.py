"""Manual fine-tuning config and checkpoint logic for architecture-skill models.

Implements the principle:
- config-first training loop
- fixed input schema and output targets
- checkpoint every epoch for rollback and comparison
- separate training-time tuning from inference-time routing
"""

import json
import logging
import math
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class TuningConfig:
    """Human-controlled training configuration."""

    learning_rate: float = 0.01
    grad_clip: float = 1.0
    epochs: int = 5
    hidden_dims: list[int] | None = None
    checkpoint_dir: str = "checkpoints"
    seed: int = 42
    loss_family: str = "cross_entropy"
    input_schema: list[str] | None = None
    output_targets: list[str] | None = None

    def __post_init__(self) -> None:
        if self.hidden_dims is None:
            self.hidden_dims = [16, 8]
        if self.input_schema is None:
            self.input_schema = ["privacy_spectrum", "utility_preference", "data_sensitivity"]
        if self.output_targets is None:
            self.output_targets = ["LOCAL", "HYBRID", "CLOUD"]

    def to_dict(self) -> dict[str, Any]:
        """Serialize the config to a dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TuningConfig":
        """Load a config from a dictionary."""
        return cls(**data)

    def save(self, path: Path) -> None:
        """Save the config to a JSON file."""
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "TuningConfig":
        """Load a config from a JSON file."""
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls.from_dict(data)


class ManualTuner:
    """Small deterministic MLP trainer for routing logits.

    This is a teaching-scale implementation that demonstrates the architecture
    skill's fine-tuning contract: fixed schema, fixed targets, cross-entropy
    loss, gradient clipping, and epoch checkpoints.
    """

    def __init__(self, config: TuningConfig | None = None) -> None:
        """Initialize the tuner.

        Args:
            config: Training configuration. Defaults to a sensible baseline.
        """
        self.config = config or TuningConfig()
        self._weights: list[list[float]] = []
        self._biases: list[float] = []
        self._setup()

    def _setup(self) -> None:
        """Initialize weights deterministically from the seed."""
        random.seed(self.config.seed)
        input_dim = len(self.config.input_schema)
        output_dim = len(self.config.output_targets)
        self._weights = [
            [random.uniform(-0.1, 0.1) for _ in range(input_dim)]
            for _ in range(output_dim)
        ]
        self._biases = [0.0 for _ in range(output_dim)]

    def _forward(self, x: list[float]) -> list[float]:
        """Compute logits for a single input vector."""
        logits: list[float] = []
        for w, b in zip(self._weights, self._biases):
            logit = sum(wi * xi for wi, xi in zip(w, x)) + b
            logits.append(logit)
        return logits

    @staticmethod
    def _softmax(logits: list[float]) -> list[float]:
        """Compute softmax probabilities."""
        max_logit = max(logits)
        exp_shifted = [math.exp(x - max_logit) for x in logits]
        total = sum(exp_shifted)
        return [x / total for x in exp_shifted]

    def _cross_entropy(self, logits: list[float], target: int) -> float:
        """Compute cross-entropy loss for a single example."""
        probs = self._softmax(logits)
        eps = 1e-12
        return -math.log(probs[target] + eps)

    def train(
        self,
        X: list[list[float]],
        y: list[int],
        *,
        baseline_only: bool = False,
    ) -> dict[str, Any]:
        """Run a deterministic training loop with epoch checkpoints.

        Args:
            X: Training input vectors.
            y: Training target indices.
            baseline_only: If True, only run the baseline evaluation.

        Returns:
            A dictionary with metrics, checkpoint paths, and final weights.
        """
        checkpoint_dir = Path(self.config.checkpoint_dir)
        checkpoint_dir.mkdir(parents=True, exist_ok=True)

        history: list[dict[str, Any]] = []
        checkpoint_paths: list[str] = []

        epochs = 1 if baseline_only else self.config.epochs
        for epoch in range(1, epochs + 1):
            total_loss = 0.0
            correct = 0

            for x, target in zip(X, y):
                logits = self._forward(x)
                loss = self._cross_entropy(logits, target)
                total_loss += loss
                probs = self._softmax(logits)
                if probs.index(max(probs)) == target:
                    correct += 1

                # Manual backprop + gradient clipping for output weights.
                for i, (w, b) in enumerate(zip(self._weights, self._biases)):
                    prob = probs[i]
                    indicator = 1.0 if i == target else 0.0
                    grad = prob - indicator
                    # Clip gradients
                    grad = max(-self.config.grad_clip, min(self.config.grad_clip, grad))
                    for j in range(len(w)):
                        w[j] -= self.config.learning_rate * grad * x[j]
                    self._biases[i] -= self.config.learning_rate * grad

            avg_loss = total_loss / len(X) if X else 0.0
            accuracy = correct / len(X) if X else 0.0
            history.append({"epoch": epoch, "loss": avg_loss, "accuracy": accuracy})

            checkpoint_path = checkpoint_dir / f"epoch_{epoch}.json"
            self._save_checkpoint(checkpoint_path)
            checkpoint_paths.append(str(checkpoint_path))
            logger.info("Epoch %s: loss=%.4f accuracy=%.4f", epoch, avg_loss, accuracy)

        return {
            "config": self.config.to_dict(),
            "history": history,
            "checkpoints": checkpoint_paths,
            "final_weights": self._weights,
            "final_biases": self._biases,
        }

    def _save_checkpoint(self, path: Path) -> None:
        """Save the current weights and config as a checkpoint."""
        payload = {
            "config": self.config.to_dict(),
            "weights": self._weights,
            "biases": self._biases,
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def load_checkpoint(self, path: Path) -> None:
        """Load weights and config from a checkpoint file."""
        data = json.loads(path.read_text(encoding="utf-8"))
        self.config = TuningConfig.from_dict(data["config"])
        self._weights = data["weights"]
        self._biases = data["biases"]

    def predict(self, x: list[float]) -> dict[str, Any]:
        """Predict routing logits and probabilities for a single input."""
        logits = self._forward(x)
        probs = self._softmax(logits)
        return {
            "logits": logits,
            "probabilities": {target: p for target, p in zip(self.config.output_targets, probs)},
            "selected": self.config.output_targets[probs.index(max(probs))],
        }

    def compare_checkpoints(self, paths: list[Path]) -> dict[str, Any]:
        """Compare metrics across checkpoints for keep/revert decisions."""
        summaries: list[dict[str, Any]] = []
        for path in paths:
            data = json.loads(path.read_text(encoding="utf-8"))
            summaries.append(
                {
                    "path": str(path),
                    "config": data["config"],
                    "weights_sample": data["weights"][0][:3],
                }
            )
        return {"checkpoint_count": len(summaries), "summaries": summaries}
