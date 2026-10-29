"""Ticketing-system adapter boundary.

The mock adapter is deliberately local. A real Orbit 360 adapter must not be
implemented until the bank/vendor provides an approved API contract and security
requirements. No external system is contacted by this module.
"""
import os
import uuid
from typing import Protocol


class TicketingAdapter(Protocol):
    def create_ticket(self, ticket: dict) -> dict:
        """Create a ticket in the target system and return its external reference."""
        ...


class MockTicketingAdapter:
    """Local stand-in for contract testing; it does not contact Orbit 360."""

    def create_ticket(self, ticket: dict) -> dict:
        return {
            "external_ticket_id": "MOCK-" + uuid.uuid4().hex[:10].upper(),
            "adapter": "mock",
            "result": "SIMULATED_ONLY",
        }


def get_ticketing_adapter() -> TicketingAdapter:
    mode = os.environ.get("TICKETING_ADAPTER", "mock").strip().lower()
    if mode == "mock":
        return MockTicketingAdapter()
    if mode == "orbit360":
        raise RuntimeError(
            "Orbit 360 adapter is not configured. Obtain an approved API contract "
            "and credentials before enabling live integration."
        )
    raise ValueError("TICKETING_ADAPTER must be 'mock' or 'orbit360'.")
