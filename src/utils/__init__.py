"""
Utility functions for the Travel Manager CDP application.

This module provides:
- Logging configuration and utilities
- State management helpers for both travel planning and blockchain operations
- Common functions used across different parts of the application

These utilities support the core functionality of the application by providing
consistent logging, state management, and helper functions.
"""

from src.utils.logging import setup_logging
from src.utils.state import (
    log_state_change,
    log_action_info,
    update_worker_state,
    get_agent_state_fn,
    get_travel_consultant_worker_state_fn,
    get_flight_consultant_worker_state_fn,
    get_hotel_reservationist_worker_state_fn,
    get_experience_curator_worker_state_fn,
    get_location_curator_worker_state_fn,
    get_payment_processor_worker_state_fn,
    init_state
)

__all__ = [
    'setup_logging',
    'log_state_change',
    'log_action_info',
    'update_worker_state',
    'get_agent_state_fn',
    'get_travel_consultant_worker_state_fn',
    'get_flight_consultant_worker_state_fn',
    'get_hotel_reservationist_worker_state_fn',
    'get_experience_curator_worker_state_fn',
    'get_location_curator_worker_state_fn',
    'get_payment_processor_worker_state_fn',
    'init_state'
]
