import asyncio
import atexit
import sys
from pathlib import Path

import logfire
from pydantic_ai import Agent
from pydantic_ai.usage import UsageLimits
from pydantic_ai.workspaces import WorkspaceError
from pydantic_ai_harness import RepoContext
from pydantic_ai_harness.coder import Coder
from pydantic_ai_harness.docker_sandbox import DockerSandbox, DockerSandboxBackend

from ._cli import run_cli
from ._utils import destroy_docker_sandbox, get_cli_args, get_docker_args


def main() -> None:
    _ = logfire.configure(send_to_logfire=False)
    logfire.instrument_pydantic_ai()

    cli_args = get_cli_args()
    source_dir = cli_args.source_dir
    model = cli_args.model
    docker_image = cli_args.docker_image
    docker_publish_ports = cli_args.docker_publish_ports
    retry_limit = cli_args.retry_limit
    request_limit = cli_args.request_limit

    if retry_limit < 0:
        sys.exit("The retry limit must be at least 0.")

    if request_limit < 1:
        sys.exit("The request limit must be at least 1.")

    try:
        source_path = Path(source_dir).resolve(strict=True)

        if not source_path.is_dir():
            sys.exit("The source directory must be a directory.")

        normalized_source_dir = source_path.as_posix()
    except OSError:
        sys.exit("Unable to find/access source directory: " + source_dir)

    if "," in normalized_source_dir or '"' in normalized_source_dir:
        sys.exit(
            'The source directory path cannot contain a comma (,) or a double quote (").'
        )

    docker_args = get_docker_args(docker_publish_ports, normalized_source_dir)
    docker_sandbox_backend = DockerSandboxBackend(
        image=docker_image, docker_args=docker_args, working_dir="/workspace"
    )
    _ = atexit.register(destroy_docker_sandbox, docker_sandbox_backend)

    try:
        probe = asyncio.run(docker_sandbox_backend.run("ls", shell=True))
    except WorkspaceError as e:
        sys.exit("Failed to create Docker sandbox: " + str(e))

    docker_ref = docker_sandbox_backend.ref

    if docker_ref is None or probe.exit_code != 0:
        sys.exit("Failed to create Docker sandbox: " + probe.stderr.strip())

    agent = Agent(
        model=model,
        retries=retry_limit,
        capabilities=[
            Coder(repo_context=False),
            RepoContext(nested_traversal=True),
            DockerSandbox(),
        ],
    )

    run_cli(agent, UsageLimits(request_limit=request_limit), docker_ref)
