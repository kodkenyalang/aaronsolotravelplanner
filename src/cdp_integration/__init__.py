"""
Coinbase Developer Platform integration components.

This module handles all blockchain-related functionality through CDP AgentKit:
- Wallet initialization and management
- Blockchain actions (payments, swaps, transfers)
- CDP agent setup and configuration
- Token management and balance tracking

The CDP integration enables the travel management system to process cryptocurrency
payments, swap between different tokens, and interact with blockchain networks
through the Coinbase Developer Platform.
"""

from src.cdp_integration.agent import initialize_cdp_agent
from src.cdp_integration.wallet import initialize_wallet_provider
from src.cdp_integration.actions import (
    cdp_get_wallet_details,
    cdp_request_funds,
    cdp_check_balance,
    cdp_process_payment,
    cdp_swap_tokens,
    cdp_transfer_tokens,
    cdp_get_token_price,
    cdp_explore_defi_options,
    process_cdp_message
)

__all__ = [
    'initialize_cdp_agent',
    'initialize_wallet_provider',
    'cdp_get_wallet_details',
    'cdp_request_funds',
    'cdp_check_balance',
    'cdp_process_payment',
    'cdp_swap_tokens',
    'cdp_transfer_tokens',
    'cdp_get_token_price',
    'cdp_explore_defi_options',
    'process_cdp_message'
]
