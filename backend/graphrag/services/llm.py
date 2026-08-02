"""Local-first Qwen3-4B-Instruct-2507 orchestration client.

Prefers in-process transformers inference. An optional OpenAI-compatible
HTTP endpoint (vLLM/SGLang) can be used when QWEN_API_BASE is set, but no
cloud API key is required for local operation.
"""

import json
import logging
import os
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SamplingPreset:
    """Sampling parameters for a Qwen pass."""

    top_p: float
    temperature: float
    max_new_tokens: int


EXTRACTION_PRESET = SamplingPreset(top_p=0.10, temperature=0.2, max_new_tokens=2048)
HYPOTHESIS_PRESET = SamplingPreset(top_p=0.95, temperature=0.8, max_new_tokens=1024)


class QwenClient:
    """Orchestration client for Qwen3-4B-Instruct-2507.

    Default path: local transformers pipeline (no network API).
    Optional path: OpenAI-compatible local server via QWEN_API_BASE.
    """

    def __init__(
        self,
        model_name: str = "Qwen/Qwen3-4B-Instruct-2507",
        api_base: str | None = None,
        api_key: str | None = None,
    ) -> None:
        """Initialize the Qwen client.

        Args:
            model_name: Model identifier or API model name.
            api_base: Optional OpenAI-compatible API base URL. If omitted, the
                client loads the model locally via transformers.
            api_key: Optional API key for a local OpenAI-compatible endpoint.
        """
        self.model_name = model_name
        self.api_base = api_base or os.environ.get("QWEN_API_BASE")
        self.api_key = api_key or os.environ.get("QWEN_API_KEY")
        self._local_pipeline: Any | None = None

    def _load_local(self) -> Any:
        """Load the local transformers pipeline on first use."""
        if self._local_pipeline is not None:
            return self._local_pipeline
        try:
            from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
        except ImportError as exc:
            logger.error("transformers is not installed")
            raise RuntimeError(
                "Install transformers (see backend/requirements.txt) for local Qwen inference"
            ) from exc

        logger.info("Loading local Qwen model: %s", self.model_name)
        tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype="auto",
            device_map="auto",
        )
        self._local_pipeline = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
        )
        return self._local_pipeline

    def _call_api(self, messages: list[dict[str, str]], preset: SamplingPreset) -> str:
        """Call an optional OpenAI-compatible chat completions endpoint."""
        if not self.api_base:
            raise RuntimeError("No QWEN_API_BASE configured for API inference")

        try:
            import httpx
        except ImportError as exc:
            raise RuntimeError("Install httpx to use QWEN_API_BASE") from exc

        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": self.model_name,
            "messages": messages,
            "top_p": preset.top_p,
            "temperature": preset.temperature,
            "max_tokens": preset.max_new_tokens,
        }
        response = httpx.post(
            f"{self.api_base}/chat/completions",
            headers=headers,
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    def _call_local(self, messages: list[dict[str, str]], preset: SamplingPreset) -> str:
        """Call the local transformers pipeline."""
        pipeline = self._load_local()
        tokenizer = pipeline.tokenizer
        prompt = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        outputs = pipeline(
            prompt,
            max_new_tokens=preset.max_new_tokens,
            top_p=preset.top_p,
            temperature=preset.temperature,
            do_sample=True,
            return_full_text=False,
        )
        return outputs[0]["generated_text"]

    def chat(
        self, messages: list[dict[str, str]], preset: SamplingPreset
    ) -> str:
        """Run a chat completion with the given sampling preset.

        Args:
            messages: OpenAI-style message list.
            preset: Sampling parameters.

        Returns:
            The generated assistant message text.
        """
        if self.api_base:
            return self._call_api(messages, preset)
        return self._call_local(messages, preset)

    def generate_json(
        self, system_prompt: str, user_prompt: str, preset: SamplingPreset = EXTRACTION_PRESET
    ) -> dict[str, Any]:
        """Generate a JSON object from Qwen and parse it.

        Args:
            system_prompt: System instruction.
            user_prompt: User prompt.
            preset: Sampling preset; defaults to extraction mode.

        Returns:
            Parsed JSON object.

        Raises:
            ValueError: If the response cannot be parsed as JSON.
        """
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        content = self.chat(messages, preset)
        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            logger.warning("Failed to parse JSON response: %s", content[:200])
            raise ValueError("Qwen returned invalid JSON") from exc
