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
from pydantic_ai_harness.docker_container import DockerContainer, DockerContainerBackend

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

    try:
        source_path = Path(source_dir).resolve(strict=True)

        if not source_path.is_dir():
            sys.exit("The source directory must be a directory.")

        normalized_source_dir = source_path.as_posix()
    except OSError:
        sys.exit("Unable to find/access source directory: " + source_dir)

    for prohibited_char in ',"\n':
        if prohibited_char in normalized_source_dir:
            sys.exit('Source directory path cannot contain , or " or \\n.')

    if normalized_source_dir[-1].isspace():
        sys.exit("Source directory path cannot end with whitespace.")

    docker_args = get_docker_args(docker_publish_ports, normalized_source_dir)
    docker_sandbox_backend = DockerContainerBackend(
        image=docker_image, docker_args=docker_args, working_dir="/workspace"
    )
    _ = atexit.register(destroy_docker_sandbox, docker_sandbox_backend)

    try:
        probe = asyncio.run(docker_sandbox_backend.run("echo $PATH", shell=True))
    except WorkspaceError as e:
        sys.exit("Failed to create Docker sandbox: " + str(e))

    docker_ref = docker_sandbox_backend.ref

    if docker_ref is None or probe.exit_code != 0:
        sys.exit("Failed to create Docker sandbox: " + probe.stderr.strip())

    path_dirs = []
    path_dirs.append("/home/feather/.local/bin")

    if len(probe.stdout.strip()) > 0:
        path_dirs.append(probe.stdout.strip())

    agent = Agent(
        model=model,
        retries=retry_limit,
        capabilities=[
            Coder(repo_context=False),
            RepoContext(nested_traversal=True),
            DockerContainer(env={"PATH": ":".join(path_dirs)}),
        ],
    )

    run_cli(agent, UsageLimits(request_limit=request_limit), docker_ref)
