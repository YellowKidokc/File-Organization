"""Lightweight entrypoint for assembling prompts and validating configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


@dataclass(frozen=True)
class ModelConfig:
    provider: str
    model_name: str
    openai_api_key: str | None
    anthropic_api_key: str | None


def load_config() -> ModelConfig:
    """Load model configuration from environment variables."""
    provider = os.getenv("MODEL_PROVIDER", "openai").strip()
    model_name = os.getenv("MODEL_NAME", "gpt-4o-mini").strip()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    return ModelConfig(
        provider=provider,
        model_name=model_name,
        openai_api_key=openai_api_key,
        anthropic_api_key=anthropic_api_key,
    )


def load_prompt(name: str) -> str:
    """Load a prompt template from the prompts directory."""
    prompt_path = PROMPTS_DIR / f"{name}.md"
    return prompt_path.read_text(encoding="utf-8").strip()


def build_request(file_list: str) -> dict[str, str]:
    """Create a provider-agnostic request payload."""
    system_prompt = load_prompt("system")
    organize_prompt = load_prompt("organize").replace("{{FILE_LIST}}", file_list)
    return {
        "system": system_prompt,
        "user": organize_prompt,
    }


def validate_config(config: ModelConfig) -> list[str]:
    """Validate required keys for the selected provider."""
    issues: list[str] = []
    if config.provider == "openai" and not config.openai_api_key:
        issues.append("OPENAI_API_KEY is required for the OpenAI provider.")
    if config.provider == "anthropic" and not config.anthropic_api_key:
        issues.append("ANTHROPIC_API_KEY is required for the Anthropic provider.")
    return issues


def main() -> None:
    config = load_config()
    issues = validate_config(config)
    if issues:
        issue_text = "\n".join(f"- {issue}" for issue in issues)
        raise SystemExit(f"Configuration issues detected:\n{issue_text}")

    placeholder_file_list = "example.txt\nreport.pdf\nimages/photo.jpg"
    request = build_request(placeholder_file_list)
    print("Generated request payload:")
    print(request)


if __name__ == "__main__":
    main()
