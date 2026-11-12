# Feather

Feather is a BYOK (bring-your-own-key) agentic coding CLI harness built on top of [Pydantic AI](https://pydantic.dev/docs/ai/overview/). It securely executes AI-driven coding tasks inside isolated Docker sandboxes with mounted source code directories and optional port publishing. It also fully manages the sandbox lifecycle from creation to destruction.

<img width="1015" height="584" alt="Feather Screenshot" src="https://github.com/user-attachments/assets/de3243e3-f370-40de-baf2-7217fc40241c" />

## Supported Models

Any model compatible with Pydantic AI can be used. For details and naming conventions across different providers, see the [Pydantic AI Models Overview](https://pydantic.dev/docs/ai/models/overview/). Select the provider that you are looking to use and you should be able to find what you need to pass into Feather either through CLI arguments or through environment variables (more on that below).

## Requirements

- uv (which will automatically deal with Python versioning and dependencies)
- Docker (running and accessible)

## Installation

Clone the repository and install via uv:

```bash
uv tool install .
```

For a clean install/update you can just pull down the latest code and run the command again.

Run `feather --help` to confirm that it was properly installed. If you cannot run that command, run the following and restart your shell:

```bash
uv tool update-shell
```

## API Keys & Environment Variables

Depending on which model provider you specify via `--model`, you must provide the corresponding API key as an environment variable in standard Pydantic AI format:

- **Anthropic**: `ANTHROPIC_API_KEY`
- **Google / Gemini**: `GOOGLE_API_KEY`
- **OpenAI**: `OPENAI_API_KEY`

Pydantic AI supports many other providers as well.

*Note: If you use a local model like Ollama, no API key is required.*

## CLI Usage

Feather exposes a command-line interface via `feather`. Usage is detailed below. After you run the command, you will enter a simple chat interface akin to the example screenshot at the top of the README.

### Command-Line Arguments

- `--source-dir` *(string, required)*: Path to the directory that will be mounted into the Docker sandbox workspace. Can be absolute or relative (e.g., `/foo/bar/source/code` or `../project`).
- `--model` *(string, required)*: The name of the LLM model following Pydantic AI conventions (e.g., `google:gemini-3.5-flash-lite`, `anthropic:claude-sonnet-5-5`, `openai:gpt-6.1-sol`).
- `--docker-image` *(string, required)*: The name of the Docker image that will be used for the sandbox (e.g., `python:3.13-slim`).
- `--docker-publish-ports` *(strings, optional)*: A list of strings in the format `HOST_PORT:SANDBOX_PORT` for publishing the Docker sandbox to `127.0.0.1` on the host machine (e.g., `8000:7000 7000:6000 6000:5000`).
- `--retry-limit` *(integer, optional)*: Retry limit per prompt. Defaults to `5`.
- `--request-limit` *(integer, optional)*: Request limit per prompt. Defaults to `100`.

### Example

```bash
feather \
  --source-dir . \
  --model google:gemini-3.5-flash \
  --docker-image python:3.13-slim \
  --docker-publish-ports 8000:7000 7000:6000
```
