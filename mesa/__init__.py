"""
Tiny Mesa compatibility layer.

This project only relies on a minimal subset of Mesa's API. The real Mesa
package pulls in large numerical dependencies that can be problematic in
restricted environments, so we provide a lightweight drop-in replacement
that exposes just the pieces we need: ``Model`` with a RNG and ``Agent``
providing access to the model reference.
"""

from __future__ import annotations

import random
from typing import Any


class Model:
    """Simplified stand-in for :class:`mesa.Model`."""

    def __init__(self) -> None:
        self.random = random.Random()
        self.running = True
        self.steps = 0
        # In Mesa the user's step implementation is wrapped so that
        # framework utilities can hook into it. Replicate that behaviour so
        # instrumentation in the project keeps working.
        self._user_step = self.step
        self.step = self._wrapped_step

    def _wrapped_step(self, *args: Any, **kwargs: Any) -> Any:
        """Call the user-defined step method and track step count."""
        self.steps += 1
        return self._user_step(*args, **kwargs)

    def _user_step(self, *args: Any, **kwargs: Any) -> Any:
        """Default implementation overridden by user models."""
        return None

    def step(self, *args: Any, **kwargs: Any) -> Any:
        """Placeholder expected to be overridden by subclasses."""
        raise NotImplementedError("Model.step() must be overridden")


class Agent:
    """Simplified stand-in for :class:`mesa.Agent`."""

    def __init__(self, model: Model) -> None:
        self.model = model
        self.random = model.random

    def step(self) -> None:
        """Agents override this to implement per-tick behaviour."""
        return None
