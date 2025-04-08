"""
GAME Framework agent definitions for the Travel Manager CDP system.

This module contains:
- The main Travel Manager agent definition
- Worker definitions for specialized travel tasks
- Function implementations for travel-related actions
- State management for travel planning

These components implement the core travel planning functionality using the GAME
Framework's agent architecture with specialized workers that handle different
aspects of travel planning.
"""

from src.game_agents.travel_agent import create_travel_manager
from src.game_agents.workers import (
    travel_consultant,
    flight_consultant,
    hotel_reservationist,
    experience_curator,
    location_curator,
    payment_processor,
    TRAVEL_CONSULTANT_ID,
    FLIGHT_CONSULTANT_ID,
    HOTEL_RESERVATIONIST_ID,
    EXPERIENCE_CURATOR_ID,
    LOCATION_CURATOR_ID,
    PAYMENT_PROCESSOR_ID
)

__all__ = [
    'create_travel_manager',
    'travel_consultant',
    'flight_consultant',
    'hotel_reservationist', 
    'experience_curator',
    'location_curator',
    'payment_processor',
    'TRAVEL_CONSULTANT_ID',
    'FLIGHT_CONSULTANT_ID',
    'HOTEL_RESERVATIONIST_ID',
    'EXPERIENCE_CURATOR_ID',
    'LOCATION_CURATOR_ID',
    'PAYMENT_PROCESSOR_ID'
]
