# File Organization Workflow

1. Load provider settings from environment variables if you want to generate an LLM prompt.
2. Scan the target directory to build a file inventory.
3. Build a request using the system prompt and the organization prompt.
4. Review the proposed folder structure and plan before making changes.
5. Run in dry-run mode first; only perform moves after confirmation.
