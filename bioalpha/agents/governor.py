"""
The Governor (Orchestrator)
===========================
The Chief Investment Officer (CIO) of the Bio-Alpha Fund.
"""

from __future__ import annotations

import logging
from typing import List

from bioalpha.agents.base import BaseAgent, AgentAction
from bioalpha.bridge import SerialBridge
from bioalpha.ledger import Vault
from bioalpha.sensors.simulator import SensorReading

log = logging.getLogger("bioalpha.governor")


class Governor(BaseAgent):
    """The central orchestrator for the Bio-Alpha multi-agent system."""

    def __init__(self, vault: Vault, bridge: SerialBridge):
        super().__init__("The Governor", vault, bridge)
        self.workers: List[BaseAgent] = []

    def add_worker(self, worker: BaseAgent):
        self.workers.append(worker)

    async def run_cycle(self) -> List[AgentAction]:
        reading = self.bridge.read()
        actions_taken = []
        log.info(f"--- Fund Cycle Start [{reading.timestamp}] ---")
        log.info(f"Balance: ${self.vault.balance:,} ALPHA")
        for worker in self.workers:
            action = await worker.think(reading)
            if action.thought:
                log.info(f"[{worker.name}] Thinking: {action.thought}")
            if action.tool:
                await worker.execute(action)
                actions_taken.append(action)
        return actions_taken

    async def think(self, reading: SensorReading) -> AgentAction:
        balance = self.vault.balance
        if balance < 10000:
            thought = "CRITICAL: Fund balance is below safety threshold. Priority: Survival over Growth."
        else:
            thought = "Fund is healthy. Priority: Optimization of biomass per $ALPHA spent."
        return AgentAction(agent_name=self.name, thought=thought)
