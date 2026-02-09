# File-Organization

This project provides a lightweight workflow for organizing files with help from LLM prompts.

## Quick start

1. Copy `.env.example` to `.env` and fill in your API keys.
2. Review the prompts in `prompts/` and the workflow in `workflow.md`.
3. Run the organizer entrypoint:

```bash
python src/file_organizer.py
```

The script currently validates configuration and assembles the prompt payload.
