"""Custom scheduler implementations compatible with Mesa 3.x."""

from __future__ import annotations

from contextlib import suppress
from typing import Iterable, List


class RandomActivation:
    """Simplified drop-in replacement for Mesa <3 RandomActivation.

    Mesa 3.x removed the built-in schedulers module. For our use case we only
    need to activate all registered agents once per model step in random order,
    so we implement the minimal interface expected by the project code.
    """

    def __init__(self, model) -> None:
        self.model = model
        self._agents: List[object] = []

    def add(self, agent) -> None:
        """Register an agent with the scheduler if not already present."""
        if agent not in self._agents:
            self._agents.append(agent)

    def remove(self, agent) -> None:
        """Remove an agent from the scheduler if present."""
        with suppress(ValueError):
            self._agents.remove(agent)

    def step(self) -> None:
        """Activate each agent once in a randomized order."""
        agents = list(self._agents)
        self.model.random.shuffle(agents)
        for agent in agents:
            agent.step()

    def get_agent_count(self) -> int:
        """Return the number of scheduled agents."""
        return len(self._agents)

    @property
    def agents(self) -> Iterable[object]:
        """Return an iterable over the scheduled agents."""
        return tuple(self._agents)
