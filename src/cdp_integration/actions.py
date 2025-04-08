"""
CDP AgentKit Blockchain Actions
"""
import logging
from typing import List, Dict, Any
from langchain_core.messages import HumanMessage

# Get the module logger
logger = logging.getLogger(__name__)

def process_cdp_message(cdp_agent, cdp_config, message: str) -> List[str]:
    """Process a message through the CDP agent."""
    logger.info(f"Processing CDP message: {message}")
    
    results = []
    
    try:
        for chunk in cdp_agent.stream(
            {"messages": [HumanMessage(content=message)]}, cdp_config
        ):
            content = None
            
            if "agent" in chunk and chunk["agent"]["messages"]:
                content = chunk["agent"]["messages"][0].content
            elif "tools" in chunk and chunk["tools"]["messages"]:
                content = chunk["tools"]["messages"][0].content
                
            if content:
                print(content)
                results.append(content)
                
    except Exception as e:
        logger.error(f"Error processing CDP message: {e}")
        error_message = f"Error communicating with CDP: {str(e)}"
        print(error_message)
        results.append(error_message)
            
    return results


def cdp_get_wallet_details(cdp_agent, cdp_config) -> List[str]:
    """Get wallet details through CDP AgentKit."""
    logger.info("Fetching wallet details")
    return process_cdp_message(cdp_agent, cdp_config, "Get my wallet details and check what network I'm on.")


def cdp_request_funds(cdp_agent, cdp_config) -> List[str]:
    """Request funds from faucet through CDP AgentKit."""
    logger.info("Requesting funds from faucet")
    return process_cdp_message(cdp_agent, cdp_config, "Request funds from the faucet for my travel payment system.")


def cdp_check_balance(cdp_agent, cdp_config, token: str = "ETH") -> List[str]:
    """Check wallet balance through CDP AgentKit."""
    logger.info(f"Checking wallet balance for {token}")
    return process_cdp_message(cdp_agent, cdp_config, f"Check my wallet balance for {token}.")


def cdp_process_payment(cdp_agent, cdp_config, amount: str, currency: str, service: str) -> List[str]:
    """Process a payment through CDP AgentKit."""
    logger.info(f"Processing payment of {amount} {currency} for {service}")
    return process_cdp_message(
        cdp_agent, 
        cdp_config, 
        f"Process a payment of {amount} {currency} for {service}. Explain the transaction details."
    )


def cdp_swap_tokens(cdp_agent, cdp_config, from_token: str, to_token: str, amount: str) -> List[str]:
    """Swap tokens using CDP AgentKit."""
    logger.info(f"Swapping {amount} {from_token} to {to_token}")
    return process_cdp_message(
        cdp_agent,
        cdp_config,
        f"Swap {amount} {from_token} to {to_token} and report the details of the transaction."
    )


def cdp_transfer_tokens(cdp_agent, cdp_config, to_address: str, token: str, amount: str) -> List[str]:
    """Transfer tokens to another address using CDP AgentKit."""
    logger.info(f"Transferring {amount} {token} to {to_address}")
    return process_cdp_message(
        cdp_agent,
        cdp_config,
        f"Transfer {amount} {token} to the address {to_address} and confirm the transaction details."
    )


def cdp_get_token_price(cdp_agent, cdp_config, token: str) -> List[str]:
    """Get the current price of a token using CDP AgentKit."""
    logger.info(f"Getting price for {token}")
    return process_cdp_message(
        cdp_agent,
        cdp_config,
        f"Get the current price of {token} and provide the information."
    )


def cdp_explore_defi_options(cdp_agent, cdp_config) -> List[str]:
    """Explore DeFi options like staking or providing liquidity using CDP AgentKit."""
    logger.info("Exploring DeFi options")
    return process_cdp_message(
        cdp_agent,
        cdp_config,
        "What DeFi options are available on this network for earning yield? Provide information about staking or liquidity provision."
    )
