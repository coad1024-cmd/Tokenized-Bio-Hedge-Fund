"""
Base Agent Architecture
=======================
Standard interface for all L3 Frontier Intelligence agents.

Every agent follows the 'OODA' loop:
1. Observe: Receive sensor data and fund status.
2. Orient: Compare against Biological Policy and Economic constraints.
3. Decide: Formulate a reasoning 'Thought' and select a Tool.
4. Act: Execute the Tool and log the result.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Callable, Dict, List

from pydantic import BaseModel, Field

from bioalpha.bridge import SerialBridge
from bioalpha.ledger import Vault
from bioalpha.sensors.simulator import SensorReading

log = logging.getLogger("bioalpha.agents")


class AgentAction(BaseModel):
    """Encapsulates a decision made by an agent."""
    agent_name: str
    thought: str
    tool: str | None = None
    params: Dict[str, Any] = {}
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))


class BaseAgent(ABC):
    """Abstract base class for all Bio-Alpha agents."""

    def __init__(self, name: str, vault: Vault, bridge: SerialBridge):
        self.name = name
        self.vault = vault
        self.bridge = bridge
        self.tools: Dict[str, Callable] = {}
        self._register_default_tools()

    def _register_default_tools(self):
        self.tools["get_balance"] = lambda: self.vault.balance
        self.tools["get_latest_reading"] = lambda: self.bridge.last_reading

    def register_tool(self, name: str, func: Callable):
        self.tools[name] = func

    @abstractmethod
    async def think(self, reading: SensorReading) -> AgentAction:
        pass

    async def execute(self, action: AgentAction):
        """Run the chosen tool and log the result.
        
        NOTE: Agents using an ActuatorDispatcher execute tools directly
        in think(). In that case, action.tool is for logging only and
        won't be found in self.tools — which is fine.
        """
        if not action.tool or action.tool not in self.tools:
            return

        log.info(f"[{self.name}] Acting: {action.tool} with {action.params}")
        try:
            result = self.tools[action.tool](**action.params)
            self.vault.log_actuator(
                actuator=f"agent:{self.name}",
                action=f"{action.tool}({action.params})",
                cost=0
            )
            return result
        except Exception as e:
            log.error(f"[{self.name}] Action failed: {e}")
            return None
