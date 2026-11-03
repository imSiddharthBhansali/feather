import asyncio
import atexit
from typing import override

from pydantic_ai import RunContext
from pydantic_ai.capabilities import AbstractCapability
from pydantic_ai.run import AgentRunResult
from pydantic_ai.workspaces import WorkspaceRef
from pydantic_ai_harness.docker_sandbox import DockerSandbox


class DockerSandboxDestroyer(AbstractCapability):
    def __init__(self) -> None:
        self.registered_ids = set()

    def destroy_docker_sandbox(self, ref: WorkspaceRef) -> None:
        asyncio.run(DockerSandbox().destroy(ref))

    def register_docker_sandbox(self, ref: WorkspaceRef | None) -> None:
        if ref != None:
            id_to_destroy = ref.id

            if id_to_destroy not in self.registered_ids:
                self.registered_ids.add(id_to_destroy)
                _ = atexit.register(self.destroy_docker_sandbox, ref)

    @override
    async def after_run(
        self, ctx: RunContext, *, result: AgentRunResult
    ) -> AgentRunResult:
        self.register_docker_sandbox(ctx.workspace.ref)
        return result
