"""
Blockchain automatic mode functionality
"""
import logging
from typing import Any
from game_sdk.game.agent import Agent

from src.cdp_integration.actions import (
    cdp_get_wallet_details, 
    cdp_request_funds, 
    cdp_check_balance
)

# Get the module logger
logger = logging.getLogger(__name__)

# Mode constants
BLOCKCHAIN_AUTO_MODE = "blockchain_auto"

def run_blockchain_auto_mode(agent: Agent, cdp_agent: Any, cdp_config: Any, agentkit: Any) -> None:
    """
    Run the agent in automatic mode with blockchain capabilities.
    Agent will use CDP AgentKit for blockchain operations.
    """
    logger.info("Running in BLOCKCHAIN AUTO MODE")
    print("\n🤖🔗 Running in BLOCKCHAIN AUTO MODE - AI will make travel and blockchain decisions\n")
    
    # Update the initial state to indicate blockchain auto mode
    state = agent.get_agent_state_fn(None, None)
    state["agent_state"]["interaction_mode"] = BLOCKCHAIN_AUTO_MODE
    state["agent_state"]["blockchain_enabled"] = True
    
    # Get CDP wallet details and request funds
    logger.info("Initializing blockchain wallet")
    cdp_get_wallet_details(cdp_agent, cdp_config)
    cdp_request_funds(cdp_agent, cdp_config)
    cdp_check_balance(cdp_agent, cdp_config)
    
    # Update state with blockchain connection
    state["worker_states"]["payment_processor"]["blockchain_connected"] = True
    
    # Run the GAME agent in automatic mode
    logger.info("Starting automatic travel planning with blockchain capabilities")
    agent.run()
