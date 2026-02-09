"""Organize files with prompt-driven or heuristic plans."""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from pathlib import Path

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

DEFAULT_CATEGORY_MAP = {
    "Images": {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".svg"},
    "Audio": {".mp3", ".wav", ".flac", ".aac", ".m4a", ".ogg"},
    "Video": {".mp4", ".mov", ".avi", ".mkv", ".webm"},
    "Documents": {".txt", ".md", ".pdf", ".doc", ".docx", ".rtf"},
    "Spreadsheets": {".xls", ".xlsx", ".csv"},
    "Presentations": {".ppt", ".pptx", ".key"},
    "Archives": {".zip", ".tar", ".gz", ".bz2", ".7z", ".rar"},
    "Code": {
        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".rb",
        ".go",
        ".rs",
        ".java",
        ".c",
        ".cpp",
        ".h",
        ".cs",
    },
    "Data": {".json", ".yaml", ".yml", ".toml", ".xml"},
}


@dataclass(frozen=True)
class ModelConfig:
    provider: str
    model_name: str
    openai_api_key: str | None
    anthropic_api_key: str | None


@dataclass(frozen=True)
class MoveAction:
    source: Path
    destination: Path


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


def iter_files(root: Path, exclude_dirs: set[str]) -> list[Path]:
    """Return a list of files under root, excluding specified directories."""
    files: list[Path] = []
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if any(part in exclude_dirs for part in path.parts):
            continue
        files.append(path)
    return files


def categorize_file(path: Path) -> str:
    """Assign a category based on file extension."""
    suffix = path.suffix.lower()
    for category, extensions in DEFAULT_CATEGORY_MAP.items():
        if suffix in extensions:
            return category
    return "Other"


def build_move_plan(root: Path, files: list[Path]) -> list[MoveAction]:
    """Build a move plan that groups files by category."""
    plan: list[MoveAction] = []
    for file_path in files:
        category = categorize_file(file_path)
        destination_dir = root / category
        destination_path = destination_dir / file_path.name
        if destination_path == file_path:
            continue
        plan.append(MoveAction(source=file_path, destination=destination_path))
    return plan


def format_plan(plan: list[MoveAction]) -> str:
    """Format the plan for display."""
    if not plan:
        return "No moves required."
    lines = ["Proposed move plan:"]
    for action in plan:
        lines.append(f"- {action.source} -> {action.destination}")
    return "\n".join(lines)


def apply_plan(plan: list[MoveAction]) -> None:
    """Apply the move plan on disk."""
    for action in plan:
        action.destination.parent.mkdir(parents=True, exist_ok=True)
        action.source.rename(action.destination)


def build_file_list(files: list[Path], root: Path) -> str:
    """Build a newline-separated inventory list relative to root."""
    return "\n".join(str(path.relative_to(root)) for path in files)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Organize files into category folders.")
    parser.add_argument("root", nargs="?", default=".", help="Root folder to scan")
    parser.add_argument(
        "--exclude",
        action="append",
        default=[".git", "__pycache__"],
        help="Directory name to exclude (can repeat)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply the plan instead of running a dry run",
    )
    parser.add_argument(
        "--show-prompt",
        action="store_true",
        help="Print the LLM prompt payload built from the inventory",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(args.root).resolve()
    exclude_dirs = set(args.exclude)
    files = iter_files(root, exclude_dirs)
    file_list = build_file_list(files, root)

    if args.show_prompt:
        request = build_request(file_list)
        print("Generated request payload:")
        print(request)

    plan = build_move_plan(root, files)
    print(format_plan(plan))

    if plan and args.apply:
        apply_plan(plan)
        print("Plan applied.")
    elif plan:
        print("Dry run only. Re-run with --apply to move files.")


if __name__ == "__main__":
    main()
