import argparse
import asyncio
import os
import sys
from pathlib import Path

from pydantic_ai_harness.docker_container import DockerContainer, DockerContainerBackend

from ._cli_args import CliArgs


def validate_path_str(path_str: str) -> None:
    if "," in path_str:
        sys.exit(path_str + " has a comma. This will break Docker. Exiting.")


def destroy_docker_sandbox(backend: DockerContainerBackend) -> None:
    if backend.ref is not None:
        # pyrefly: ignore[partially-unknown-type]
        asyncio.run(DockerContainer().destroy(backend.ref))


def add_docker_ro(docker_args: list[str], base_path: Path, pattern: str) -> None:
    for match in base_path.rglob(pattern):
        abs_path = match.resolve().as_posix()
        rel_path = match.relative_to(base_path).as_posix()
        validate_path_str(abs_path)
        validate_path_str(rel_path)

        docker_args.extend(
            [
                "--mount",
                "type=bind,source="
                + abs_path
                + ",target=/workspace/"
                + rel_path
                + ",readonly",
            ]
        )


def get_docker_args(publish_ports: list[str], source_dir: str) -> list[str]:
    ret = ["--mount", "type=bind,source=" + source_dir + ",target=/workspace"]
    validate_path_str(source_dir)
    base_path = Path(source_dir).resolve(strict=True)
    add_docker_ro(ret, base_path, ".git")
    add_docker_ro(ret, base_path, ".gitignore")

    for ports in publish_ports:
        ret.extend(["--publish", "127.0.0.1:" + ports])

    user_id_str = str(os.getuid())
    group_id_str = str(os.getgid())

    ret.extend(["--user", user_id_str + ":" + group_id_str])
    ret.extend(
        ["--tmpfs", "/home/feather:exec,uid=" + user_id_str + ",gid=" + group_id_str]
    )
    ret.extend(["--env", "HOME=/home/feather"])
    return ret


def get_cli_args() -> CliArgs:
    parser = argparse.ArgumentParser()

    _ = parser.add_argument(
        "--source-dir",
        type=str,
        required=True,
        help="The directory that will be mounted to the Docker sandbox. The directory must exist."
        + " If you use a relative path, it will be relative to wherever you are running this from."
        + " Example = /foo/bar/source/code",
    )

    _ = parser.add_argument(
        "--model",
        type=str,
        required=True,
        help="The name of the model in accordance with Pydantic AI conventions."
        + " Example = google:gemini-3.5-flash-lite",
    )

    _ = parser.add_argument(
        "--docker-image",
        type=str,
        required=True,
        help="The name of the Docker image that will be used for the sandbox."
        + " The Docker image must be Linux-based."
        + " Example = python:3.13-slim",
    )

    _ = parser.add_argument(
        "--docker-publish-ports",
        type=str,
        nargs="+",
        help="A list of strings in the format HOST_PORT:SANDBOX_PORT for publishing the Docker sandbox."
        + " The published IP address will be 127.0.0.1 on the host machine no matter what."
        + " Example = 8000:7000 7000:6000 6000:5000",
        default=[],
    )

    _ = parser.add_argument(
        "--retry-limit",
        type=int,
        default=5,
        help="Retry limit per prompt. Defaults to 5.",
    )

    _ = parser.add_argument(
        "--request-limit",
        type=int,
        default=100,
        help="Request limit per prompt. Defaults to 100.",
    )

    _ = parser.add_argument(
        "--mcp-file",
        type=str,
        help="Path to a mcpServers JSON file. This is the same JSON shape used "
        + " for MCP by Claude Desktop, Claude Code, and Cursor.",
    )

    return parser.parse_args(namespace=CliArgs())
