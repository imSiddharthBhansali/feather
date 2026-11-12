import sys
import time

from pydantic_ai import Agent, ModelMessage
from pydantic_ai.exceptions import AgentRunError
from pydantic_ai.usage import UsageLimits
from pydantic_ai.workspaces import WorkspaceRef
from rich.console import Console
from rich.markdown import Markdown

from ._constants import WELCOME_MESSAGE


def run_cli(agent: Agent, usage_limits: UsageLimits, docker_ref: WorkspaceRef) -> None:
    message_history: list[ModelMessage] = []
    console = Console()
    console.print()
    console.print(Markdown(WELCOME_MESSAGE))
    console.print()

    while True:
        try:
            user_prompt = console.input("Feather > ").strip()
            console.print()

            if len(user_prompt) == 0:
                continue

            if user_prompt == "/exit":
                sys.exit(0)

            if user_prompt == "/clear":
                message_history.clear()
                console.print("Context has been cleared.")
                console.print()
                continue

            if user_prompt == "/help":
                console.print(Markdown(WELCOME_MESSAGE))
                console.print()
                continue

            start_time = time.perf_counter()
            agent_response = agent.run_sync(
                user_prompt=user_prompt,
                usage_limits=usage_limits,
                message_history=message_history,
                workspace=docker_ref,
            )
            end_time = time.perf_counter()

            message_history.clear()
            message_history.extend(agent_response.all_messages())

            console.print()
            console.print(Markdown(agent_response.output))
            console.print()

            usage = agent_response.usage
            console.print("Input tokens: " + str(usage.input_tokens))
            console.print("Output tokens: " + str(usage.output_tokens))
            console.print("Cache read tokens: " + str(usage.cache_read_tokens))
            console.print("Cache write tokens: " + str(usage.cache_write_tokens))
            console.print("Time elapsed: " + str(end_time - start_time) + " seconds")
            console.print()
        except KeyboardInterrupt:
            console.print()
            console.print()
            console.print("Interrupted. Type /exit to quit.")
            console.print()
        except EOFError:
            console.print()
            sys.exit(0)
        except AgentRunError as e:
            console.print()
            console.print(e, markup=False)
            console.print()
