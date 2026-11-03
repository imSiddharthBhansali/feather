import os
from pathlib import Path

from pydantic_ai import Agent
from pydantic_ai.usage import UsageLimits
from pydantic_ai_harness import RepoContext
from pydantic_ai_harness.coder import Coder
from pydantic_ai_harness.docker_sandbox import DockerSandbox

from ._capabilities import DockerSandboxDestroyer
from ._utils import get_cli_args, get_docker_args


def main() -> None:
    os.environ["PYDANTIC_AI_NO_BANNER"] = "1"
    cli_args = get_cli_args()
    source_dir = cli_args.source_dir
    model = cli_args.model
    docker_image = cli_args.docker_image
    docker_publish_ports = cli_args.docker_publish_ports
    retry_limit = cli_args.retry_limit
    request_limit = cli_args.request_limit

    if (
        source_dir is None
        or model is None
        or docker_image is None
        or docker_publish_ports is None
        or retry_limit is None
        or request_limit is None
    ):
        print("Fatal: There was no value found for one or more parameters.")
        return

    try:
        source_path = Path(source_dir).resolve(strict=True)

        if not source_path.is_dir():
            print("The source directory must be a directory.")
            return

        normalized_source_dir = source_path.as_posix()
    except FileNotFoundError:
        print("Invalid source directory: " + source_dir)
        return

    docker_args = get_docker_args(docker_publish_ports, normalized_source_dir)
    docker_sandbox = DockerSandbox(
        image=docker_image, docker_args=docker_args, working_dir="/workspace"
    )

    agent = Agent(
        model=model,
        retries=retry_limit,
        capabilities=[
            Coder(repo_context=False),
            docker_sandbox,
            DockerSandboxDestroyer(),
            RepoContext(nested_traversal=True),
        ],
    )

    print()
    agent.to_cli_sync(
        prog_name="Feather", usage_limits=UsageLimits(request_limit=request_limit)
    )
