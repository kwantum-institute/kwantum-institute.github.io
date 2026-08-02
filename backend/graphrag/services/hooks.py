"""Hook chain for asymmetric retrieval routing and policy enforcement.

Implements the architecture-skill principles:
1. conflict-detection hook (blocks unsafe/unstable states)
2. cascade/routing hook (temperature-scaled probabilities over fixed targets)
3. policy/data hook (privacy/policy filtering before generation)
"""

import logging
import math
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class HookEvent:
    """Structured input/output for a hook decision."""

    decision_id: str
    query: str
    context: dict[str, Any] = field(default_factory=dict)
    routing_targets: list[str] = field(default_factory=lambda: ["LOCAL", "HYBRID", "CLOUD"])
    routing_logits: list[float] | None = None
    temperature: float = 1.0
    conflict_threshold: float = 0.75
    privacy_score: float = 0.5
    blocked: bool = False
    block_reason: str = ""
    selected_target: str | None = None
    probability_vector: dict[str, float] = field(default_factory=dict)
    audit_log: list[dict[str, Any]] = field(default_factory=list)
    filtered_context: list[dict[str, Any]] = field(default_factory=list)

    def log(self, hook_name: str, details: dict[str, Any]) -> None:
        """Append an audit entry for this hook decision."""
        self.audit_log.append(
            {
                "hook": hook_name,
                "timestamp": None,  # populated by caller if needed
                "details": details,
            }
        )


class ConflictDetectionHook:
    """Detect oscillatory or contradictory states and block unsafe routing."""

    def __init__(self, threshold: float = 0.75) -> None:
        """Initialize the conflict-detection hook.

        Args:
            threshold: Normalized amplitude threshold for flagging conflicts.
        """
        self.threshold = threshold

    def run(self, event: HookEvent) -> HookEvent:
        """Run conflict detection on the event context.

        Args:
            event: The hook event to evaluate.

        Returns:
            The same event, possibly marked as blocked with a reason.
        """
        signal = event.context.get("permission_signal", [])
        if not signal:
            event.log("conflict_detection", {"status": "no_signal", "blocked": False})
            return event

        # Simple FFT-based conflict detection using a basic DFT.
        n = len(signal)
        if n < 2:
            event.log("conflict_detection", {"status": "signal_too_short", "blocked": False})
            return event

        magnitudes = []
        for k in range(n // 2):
            real = sum(signal[t] * math.cos(2 * math.pi * k * t / n) for t in range(n))
            imag = sum(signal[t] * math.sin(2 * math.pi * k * t / n) for t in range(n))
            magnitudes.append(math.sqrt(real**2 + imag**2))

        max_amp = max(magnitudes) if magnitudes else 0.0
        normalized = max_amp / n if n > 0 else 0.0
        conflicting_nodes = [
            event.context.get("node_a", ""),
            event.context.get("node_b", ""),
        ]

        event.log(
            "conflict_detection",
            {
                "status": "analyzed",
                "max_amplitude": normalized,
                "threshold": self.threshold,
                "conflicting_nodes": conflicting_nodes,
            },
        )

        if normalized > self.threshold:
            event.blocked = True
            event.block_reason = (
                f"Conflict detected: normalized amplitude {normalized:.3f} "
                f"exceeds threshold {self.threshold}"
            )
            event.log("conflict_detection", {"blocked": True, "reason": event.block_reason})
            logger.warning("Conflict hook blocked decision %s: %s", event.decision_id, event.block_reason)

        return event


class CascadeRoutingHook:
    """Temperature-scaled softmax routing over fixed targets."""

    def __init__(self, temperature: float = 1.0) -> None:
        """Initialize the cascade routing hook.

        Args:
            temperature: Softmax temperature. Lower = sharper, higher = softer.
        """
        self.temperature = temperature

    @staticmethod
    def _softmax(logits: list[float], temperature: float) -> list[float]:
        """Compute temperature-scaled softmax probabilities."""
        scaled = [x / temperature for x in logits]
        max_scaled = max(scaled)
        exp_shifted = [math.exp(x - max_scaled) for x in scaled]
        total = sum(exp_shifted)
        return [x / total for x in exp_shifted] if total > 0 else [1.0 / len(logits)] * len(logits)

    def run(self, event: HookEvent) -> HookEvent:
        """Run cascade routing on the event.

        Args:
            event: The hook event with optional routing_logits.

        Returns:
            The event with selected_target and probability_vector populated.
        """
        if event.blocked:
            event.log("cascade_routing", {"status": "skipped_because_blocked"})
            return event

        targets = event.routing_targets
        logits = event.routing_logits or [0.0] * len(targets)
        if len(logits) != len(targets):
            logits = [0.0] * len(targets)

        probs = self._softmax(logits, event.temperature)
        event.probability_vector = {target: round(p, 4) for target, p in zip(targets, probs)}
        event.selected_target = targets[probs.index(max(probs))]

        event.log(
            "cascade_routing",
            {
                "temperature": event.temperature,
                "logits": logits,
                "probability_vector": event.probability_vector,
                "selected_target": event.selected_target,
            },
        )
        logger.info(
            "Cascade routing selected %s for decision %s",
            event.selected_target,
            event.decision_id,
        )
        return event


class PolicyFilterHook:
    """Apply privacy/policy filtering to retrieved context before generation."""

    def __init__(self, privacy_threshold: float = 0.7) -> None:
        """Initialize the policy filter hook.

        Args:
            privacy_threshold: Score above which full PII is stripped.
        """
        self.privacy_threshold = privacy_threshold

    def run(self, event: HookEvent) -> HookEvent:
        """Filter context based on the event's privacy_score.

        Args:
            event: The hook event with retrieved context and privacy_score.

        Returns:
            The event with filtered_context populated.
        """
        if event.blocked:
            event.log("policy_filter", {"status": "skipped_because_blocked"})
            return event

        raw_context = event.context.get("retrieved_chunks", [])
        filtered: list[dict[str, Any]] = []

        for chunk in raw_context:
            if event.privacy_score > self.privacy_threshold:
                # High privacy: strip PII and reduce to anonymized summary.
                filtered_chunk = {
                    "id": chunk.get("id"),
                    "source_id": chunk.get("source_id"),
                    "summary": "Anonymized summary",
                    "pii_stripped": True,
                }
            elif event.privacy_score <= 0.4:
                # Low privacy: allow full chunk content.
                filtered_chunk = {**chunk, "pii_stripped": False}
            else:
                # Medium privacy: partial redaction placeholder.
                filtered_chunk = {
                    "id": chunk.get("id"),
                    "source_id": chunk.get("source_id"),
                    "text": chunk.get("text", ""),
                    "redacted": True,
                }
            filtered.append(filtered_chunk)

        event.filtered_context = filtered
        event.log(
            "policy_filter",
            {
                "privacy_score": event.privacy_score,
                "threshold": self.privacy_threshold,
                "input_chunks": len(raw_context),
                "output_chunks": len(filtered),
            },
        )
        return event


class HookChain:
    """Orchestrate conflict, cascade, and policy hooks in order."""

    def __init__(
        self,
        conflict_hook: ConflictDetectionHook | None = None,
        cascade_hook: CascadeRoutingHook | None = None,
        policy_hook: PolicyFilterHook | None = None,
    ) -> None:
        """Initialize the hook chain.

        Args:
            conflict_hook: Conflict detection hook.
            cascade_hook: Cascade routing hook.
            policy_hook: Policy filter hook.
        """
        self.conflict_hook = conflict_hook or ConflictDetectionHook()
        self.cascade_hook = cascade_hook or CascadeRoutingHook()
        self.policy_hook = policy_hook or PolicyFilterHook()

    def run(self, event: HookEvent) -> HookEvent:
        """Run all hooks in order: conflict → cascade → policy.

        Args:
            event: The initial hook event.

        Returns:
            The fully processed event.
        """
        event = self.conflict_hook.run(event)
        event = self.cascade_hook.run(event)
        event = self.policy_hook.run(event)
        return event
