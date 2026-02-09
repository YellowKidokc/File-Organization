# File Organization Workflow

1. Load provider settings from environment variables.
2. Read prompt templates from the `prompts/` directory.
3. Build a request using the system prompt and the organization prompt.
4. Send the request to the configured model provider.
5. Review the proposed folder structure and plan before making changes.
6. Apply changes in a dry-run mode first; only perform moves after confirmation.
