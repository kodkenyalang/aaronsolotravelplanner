"""
Mode-specific execution functions for the Travel Manager CDP application.

This module contains implementations for the different operational modes:
- Automatic Mode: AI makes all travel decisions
- Interactive Mode: User guides the AI travel decisions
- Blockchain Auto Mode: AI makes travel & blockchain decisions
- Blockchain Chat Mode: User guides travel & blockchain decisions

Each mode provides a different user experience while leveraging the same
underlying travel planning and blockchain capabilities.
"""

from src.modes.automatic import run_automatic_mode, AUTOMATIC_MODE
from src.modes.interactive import (
    run_interactive_mode,
    get_user_input,
    confirm_action,
    display_worker_options,
    select_worker_and_action,
    get_action_parameters,
    update_agent_state_with_feedback, 
    INTERACTIVE_MODE
)
from src.modes.blockchain_auto import run_blockchain_auto_mode, BLOCKCHAIN_AUTO_MODE
from src.modes.blockchain_chat import (
    run_blockchain_chat_mode,
    display_blockchain_options,
    BLOCKCHAIN_CHAT_MODE
)

__all__ = [
    'run_automatic_mode',
    'run_interactive_mode',
    'run_blockchain_auto_mode',
    'run_blockchain_chat_mode',
    'get_user_input',
    'confirm_action',
    'display_worker_options',
    'select_worker_and_action',
    'get_action_parameters',
    'update_agent_state_with_feedback',
    'display_blockchain_options',
    'AUTOMATIC_MODE',
    'INTERACTIVE_MODE',
    'BLOCKCHAIN_AUTO_MODE',
    'BLOCKCHAIN_CHAT_MODE'
]
