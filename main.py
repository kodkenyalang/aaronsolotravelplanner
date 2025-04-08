#!/usr/bin/env python3
"""
Travel Manager CDP - Main Entry Point
Integrates GAME Framework with Coinbase Developer Platform AgentKit
"""
import os
import sys
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.game_agents import create_travel_manager
from src.cdp_integration.agent import initialize_cdp_agent
from src.modes import (
    run_automatic_mode,
    run_interactive_mode, 
    run_blockchain_auto_mode,
    run_blockchain_chat_mode,
    AUTOMATIC_MODE,
    INTERACTIVE_MODE,
    BLOCKCHAIN_AUTO_MODE,
    BLOCKCHAIN_CHAT_MODE
)
from src.utils.logging import setup_logging

def get_user_input(prompt_message: str) -> str:
    """Get input from user with the given prompt message."""
    return input(f"\n{prompt_message}: ")

def select_operating_mode() -> str:
    """Allow user to select the operating mode."""
    print("\n🔄 Select Operating Mode:")
    print("1. Automatic Mode - AI makes all travel decisions")
    print("2. Interactive Mode - You guide the AI travel decisions")
    print("3. Blockchain Auto Mode - AI makes travel & blockchain decisions")
    print("4. Blockchain Chat Mode - You guide travel & blockchain decisions")
    
    choice = get_user_input("Enter choice (1-4)")
    
    if choice == "1":
        return AUTOMATIC_MODE
    elif choice == "2":
        return INTERACTIVE_MODE
    elif choice == "3":
        return BLOCKCHAIN_AUTO_MODE
    else:
        return BLOCKCHAIN_CHAT_MODE

def main():
    """Main program entry point."""
    # Setup logging
    logger = setup_logging()
    logger.info("Starting Travel Manager CDP")
    
    # Load environment variables
    load_dotenv()
    
    # Check for OpenRouter API key
    if not os.environ.get("OPENROUTER_API_KEY"):
        logger.error("OPENROUTER_API_KEY environment variable is not set")
        print("\n⚠️ ERROR: OPENROUTER_API_KEY environment variable is required.")
        print("Please add your OpenRouter API key to the .env file and restart.")
        sys.exit(1)
    
    # Create the GAME Travel Manager agent
    logger.info("Initializing Travel Manager Agent")
    travel_manager, workers = create_travel_manager()
    travel_manager.compile()
    
    # Select operating mode
    operating_mode = select_operating_mode()
    
    # Initialize CDP agent if needed for blockchain modes
    cdp_agent = None
    cdp_config = None
    agentkit = None
    
    if operating_mode in [BLOCKCHAIN_AUTO_MODE, BLOCKCHAIN_CHAT_MODE]:
        logger.info("Initializing CDP Agent")
        cdp_agent, cdp_config, agentkit = initialize_cdp_agent()
    
    # Run the appropriate mode
    if operating_mode == AUTOMATIC_MODE:
        run_automatic_mode(travel_manager)
    elif operating_mode == INTERACTIVE_MODE:
        run_interactive_mode(travel_manager, workers)
    elif operating_mode == BLOCKCHAIN_AUTO_MODE:
        run_blockchain_auto_mode(travel_manager, cdp_agent, cdp_config, agentkit)
    else:  # BLOCKCHAIN_CHAT_MODE
        run_blockchain_chat_mode(travel_manager, workers, cdp_agent, cdp_config, agentkit)

if __name__ == "__main__":
    main()
