import argparse
import os


def get_docker_args(publish_ports: list[str], source_dir: str) -> list[str]:
    ret = ["--volume", source_dir + ":/workspace"]

    if publish_ports is not None:
        for ports in publish_ports:
            ret.extend(["--publish", "127.0.0.1:" + ports])

    user_id = 1000
    group_id = 1000

    if hasattr(os, "getuid") and hasattr(os, "getgid"):
        user_id = os.getuid()
        group_id = os.getgid()

    user_id_str = str(user_id)
    group_id_str = str(group_id)

    ret.extend(["--user", user_id_str + ":" + group_id_str])
    ret.extend(
        ["--tmpfs", "/home/feather:exec,uid=" + user_id_str + ",gid=" + group_id_str]
    )
    ret.extend(["--env", "HOME=/home/feather"])
    print("Docker arguments: " + str(ret))
    return ret


def get_cli_args() -> argparse.Namespace:
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

    return parser.parse_args()
