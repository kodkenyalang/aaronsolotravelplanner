"""
CDP AgentKit Agent Initialization
"""
import logging
import os
from typing import Tuple, Any
from coinbase_agentkit import AgentKit, AgentKitConfig
from coinbase_agentkit import (
    cdp_api_action_provider,
    cdp_wallet_action_provider,
    erc20_action_provider,
    pyth_action_provider,
    wallet_action_provider,
    weth_action_provider,
    allora_action_provider,
)
from coinbase_agentkit_langchain import get_langchain_tools
from langchain_openrouter import ChatOpenRouter
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from src.cdp_integration.wallet import initialize_wallet_provider

# Get the module logger
logger = logging.getLogger(__name__)

def initialize_cdp_agent() -> Tuple[Any, Any, Any]:
    """
    Initialize the CDP AgentKit agent with blockchain capabilities.
    Returns a tuple containing (agent_executor, config, agentkit)
    """
    logger.info("Initializing CDP AgentKit agent with DeepSeek V3")
    
    # Check for required API key
    if not os.environ.get("OPENROUTER_API_KEY"):
        logger.error("OPENROUTER_API_KEY environment variable is not set")
        raise ValueError("OPENROUTER_API_KEY environment variable is required for CDP agent")
        
    if not os.environ.get("CDP_API_KEY"):
        logger.warning("CDP_API_KEY environment variable is not set. Some CDP features may be limited.")
    
    # Initialize LLM with OpenRouter using DeepSeek V3
    llm = ChatOpenRouter(
        model="deepseek/deepseek-v3",
        api_key=os.environ.get("OPENROUTER_API_KEY"),
        max_tokens=4096
    )

    # Initialize CDP Wallet Provider
    wallet_provider = initialize_wallet_provider()

    # Initialize AgentKit with action providers
    agentkit = AgentKit(
        AgentKitConfig(
            wallet_provider=wallet_provider,
            action_providers=[
                cdp_api_action_provider(),
                cdp_wallet_action_provider(),
                erc20_action_provider(),
                pyth_action_provider(),
                wallet_action_provider(),
                weth_action_provider(),
                allora_action_provider(),
            ],
        )
    )

    # Get Langchain tools from AgentKit
    tools = get_langchain_tools(agentkit)

    # Store buffered conversation history in memory
    memory = MemorySaver()
    config = {"configurable": {"thread_id": "Travel Agent with CDP Integration"}}

    # Create ReAct Agent using the LLM and CDP Agentkit tools
    agent_executor = create_react_agent(
        llm,
        tools=tools,
        checkpointer=memory,
        state_modifier=(
            "You are a Travel Payment Processor that can interact onchain using the Coinbase Developer Platform AgentKit. "
            "You are integrated with a comprehensive Travel Management System to handle blockchain payments for travel bookings. "
            "You can process payments for flights, hotels, and experiences. You can swap tokens, check balances, and transfer funds. "
            "If you ever need funds, you can request them from the faucet if you are on network ID 'base-sepolia'. "
            "Before executing your first action, get the wallet details to see what network you're on. "
            "If there is a 5XX (internal) HTTP error code, ask the user to try again later. Be concise and helpful with your "
            "responses while focusing on travel-related payment processing."
        ),
    )
    
    logger.info("CDP AgentKit agent initialized with DeepSeek V3")
    return agent_executor, config, agentkit
