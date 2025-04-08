"""
Automatic mode functionality for the Travel Manager agent
"""
import logging
from game_sdk.game.agent import Agent

# Get the module logger
logger = logging.getLogger(__name__)

# Mode constants
AUTOMATIC_MODE = "automatic"

def run_automatic_mode(agent: Agent) -> None:
    """
    Run the agent in fully automatic mode.
    In this mode, the AI makes all decisions without user input.
    """
    logger.info("Running in AUTOMATIC MODE")
    print("\n🤖 Running in AUTOMATIC MODE - AI will make all decisions\n")
    
    # Update the initial state to indicate automatic mode
    agent.get_agent_state_fn(None, None)["agent_state"]["interaction_mode"] = AUTOMATIC_MODE
    
    # Run the agent with standard execution
    agent.run()
