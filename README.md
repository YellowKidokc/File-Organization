# File-Organization

This project provides a lightweight workflow for organizing files with help from LLM prompts.

## Quick start

1. Copy `.env.example` to `.env` and fill in your API keys (optional, only needed if you want prompt output).
2. Review the prompts in `prompts/` and the workflow in `workflow.md`.
3. Run a dry run to see the plan:

```bash
python src/file_organizer.py /path/to/folder
```

4. Apply the plan once you're ready:

```bash
python src/file_organizer.py /path/to/folder --apply
```

You can also print the prompt payload that would be sent to an LLM:

```bash
python src/file_organizer.py /path/to/folder --show-prompt
```
