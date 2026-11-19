import argparse


class CliArgs(argparse.Namespace):
    source_dir: str
    model: str
    docker_image: str
    docker_publish_ports: list[str]
    retry_limit: int
    request_limit: int
