"""
Blockchain chat mode functionality
"""
import logging
import json
import time
from typing import Any, List, Dict, Optional, Tuple
from game_sdk.game.agent import Agent, WorkerConfig
from game_sdk.game.custom_types import Function, FunctionResult, FunctionResultStatus

# Import at the top to avoid circular imports
from src.utils.state import get_payment_processor_worker_state_fn

from src.cdp_integration.actions import (
    cdp_get_wallet_details,
    cdp_request_funds,
    cdp_check_balance,
    cdp_process_payment,
    cdp_swap_tokens,
    cdp_transfer_tokens,
    cdp_get_token_price,
    cdp_explore_defi_options
)

# Get the module logger
logger = logging.getLogger(__name__)

# Mode constants
BLOCKCHAIN_CHAT_MODE = "blockchain_chat"

def get_user_input(prompt_message: str) -> str:
    """Get input from user with the given prompt message."""
    return input(f"\n{prompt_message}: ")


def confirm_action(action_description: str) -> bool:
    """Ask user to confirm an action before execution."""
    response = input(f"\n⚠️ Confirm action: {action_description} (y/n): ").lower()
    return response == 'y' or response == 'yes'


def display_worker_options(workers: List[WorkerConfig]) -> None:
    """Display available workers and their possible actions."""
    print("\n🧰 Available Workers:")
    for i, worker in enumerate(workers, 1):
        print(f"{i}. {worker.id.upper()} - {worker.worker_description}")
        print("   Actions:")
        for j, action in enumerate(worker.action_space, 1):
            print(f"   {j}. {action.fn_name} - {action.fn_description}")
        print()


def select_worker_and_action(workers: List[WorkerConfig]) -> Tuple[Optional[WorkerConfig], Optional[Function]]:
    """Allow user to select a worker and action."""
    display_worker_options(workers)
    
    try:
        worker_idx = int(get_user_input("Select worker (number)")) - 1
        if worker_idx < 0 or worker_idx >= len(workers):
            print("Invalid worker selection.")
            return None, None
        
        selected_worker = workers[worker_idx]
        
        action_idx = int(get_user_input(f"Select action for {selected_worker.id} (number)")) - 1
        if action_idx < 0 or action_idx >= len(selected_worker.action_space):
            print("Invalid action selection.")
            return selected_worker, None
        
        selected_action = selected_worker.action_space[action_idx]
        return selected_worker, selected_action
    except ValueError:
        print("Please enter a valid number.")
        return None, None


def get_action_parameters(action: Function) -> Dict[str, Any]:
    """Get parameters for the selected action from user input."""
    params = {}
    for arg in action.args:
        value = get_user_input(f"Enter {arg.name} ({arg.description})")
        params[arg.name] = value
    return params


def update_agent_state_with_feedback(current_state: dict) -> dict:
    """Update agent state based on optional user feedback."""
    print("\n📝 Provide feedback (optional, press Enter to skip):")
    
    satisfaction_str = get_user_input("Additional customer satisfaction points (0-10)")
    if satisfaction_str:
        try:
            satisfaction = int(satisfaction_str)
            if 0 <= satisfaction <= 10:
                current_state["agent_state"]["customer_satisfaction"] += satisfaction
                print(f"Updated satisfaction to {current_state['agent_state']['customer_satisfaction']}")
        except ValueError:
            print("Invalid input, feedback ignored.")
        
    completion_str = get_user_input("Additional trip completeness percentage (0-10)")
    if completion_str:
        try:
            completion = int(completion_str)
            if 0 <= completion <= 10:
                current_state["agent_state"]["trip_completeness"] += completion
                print(f"Updated trip completeness to {current_state['agent_state']['trip_completeness']}%")
        except ValueError:
            print("Invalid input, feedback ignored.")
        
    return current_state


def display_blockchain_options() -> None:
    """Display blockchain action options."""
    print("\n💰 Blockchain Payment Options:")
    print("1. Check wallet balance")
    print("2. Request funds from faucet")
    print("3. Process payment for travel service")
    print("4. Swap tokens (e.g., ETH to USDC)")
    print("5. Transfer tokens to another address")
    print("6. Get token price")
    print("7. Explore DeFi options")


def run_blockchain_chat_mode(agent: Agent, workers: List[WorkerConfig], cdp_agent: Any, cdp_config: Any, agentkit: Any) -> None:
    """
    Run the agent in interactive mode with blockchain capabilities.
    Combines user interaction with CDP AgentKit blockchain operations.
    """
    logger.info("Running in BLOCKCHAIN CHAT MODE")
    print("\n👤🔗 Running in BLOCKCHAIN CHAT MODE - You'll guide AI decisions with blockchain options\n")
    
    # Update the initial state to indicate blockchain chat mode
    current_state = agent.get_agent_state_fn(None, None)
    current_state["agent_state"]["interaction_mode"] = BLOCKCHAIN_CHAT_MODE
    current_state["agent_state"]["blockchain_enabled"] = True
    
    # Initialize CDP wallet connection
    logger.info("Initializing blockchain wallet")
    print("\n🔗 Initializing blockchain connection through CDP AgentKit...")
    cdp_get_wallet_details(cdp_agent, cdp_config)
    cdp_request_funds(cdp_agent, cdp_config)
    cdp_check_balance(cdp_agent, cdp_config)
    
    # Extract balance from response (this would need more sophisticated parsing in a real implementation)
    balance = 100  # Default mock balance
    
    # Update state with blockchain connection
    current_state["agent_state"]["wallet_balance"] = balance
    current_state["worker_states"]["payment_processor"]["blockchain_connected"] = True
    
    logger.info("Blockchain wallet initialized")
    print("\n📊 Initial State:")
    print(json.dumps(current_state["agent_state"], indent=4))
    
    while True:
        # Check termination conditions
        all_depleted = all(worker_state["energy"] == 0 
                          for worker_state in current_state["worker_states"].values())
        
        if all_depleted:
            logger.info("All workers depleted. Terminating.")
            print("\n⚠️ All workers are depleted. Planning terminated.")
            break
            
        if current_state["agent_state"]["trip_completeness"] >= 100:
            logger.info("Trip planning complete.")
            print("\n🎉 Trip planning is complete!")
            break
            
        if current_state["agent_state"]["budget_remaining"] <= 0 and current_state["agent_state"]["wallet_balance"] <= 0:
            logger.info("Budget and wallet balance exhausted. Terminating.")
            print("\n💸 Both traditional budget and crypto wallet are exhausted. Planning terminated.")
            break
        
        # Display current state summary
        print("\n📊 Current Status:")
        print(f"Traditional Budget: ${current_state['agent_state']['budget_remaining']}")
        print(f"Crypto Wallet Balance: {current_state['agent_state']['wallet_balance']}")
        print(f"Token Balances: {json.dumps(current_state['agent_state']['wallet_tokens'], indent=2)}")
        print(f"Satisfaction: {current_state['agent_state']['customer_satisfaction']}")
        print(f"Trip Completeness: {current_state['agent_state']['trip_completeness']}%")
        
        # Display mode selection for this round
        print("\n🔄 For this action, would you like to:")
        print("1. Use standard GAME workers")
        print("2. Use CDP blockchain functions")
        mode_choice = get_user_input("Select mode (1 or 2)")
        
        if mode_choice == "1":
            # Standard GAME worker actions
            worker, action = select_worker_and_action(workers)
            if worker is None or action is None:
                print("Invalid selection. Try again.")
                continue
            
            # Check worker energy
            if current_state["worker_states"][worker.id]["energy"] <= 0:
                print(f"\n⚠️ {worker.id} has no energy left. Choose another worker.")
                continue
                
            # Get parameters for the action
            params = get_action_parameters(action)
            
            # Confirm action
            if not confirm_action(f"Use {worker.id} to {action.fn_name} with parameters {params}"):
                print("Action cancelled.")
                continue
                
            # Execute the action
            logger.info(f"Executing {worker.id}.{action.fn_name} with params {params}")
            result_status, result_message, result_info = action.executable(**params)
            
            function_result = FunctionResult(
                action_status=result_status,
                message=result_message,
                info=result_info
            )
            
            # Update worker state
            worker_state_fn = next(w.get_state_fn for w in workers if w.id == worker.id)
            current_state = worker_state_fn(function_result, current_state)
            
            # Update agent state
            current_state = agent.get_agent_state_fn(function_result, current_state)
            
        else:
            # CDP blockchain actions
            display_blockchain_options()
            
            blockchain_choice = get_user_input("Select blockchain action (1-7)")
            
            if blockchain_choice == "1":
                # Check wallet balance
                token = get_user_input("Enter token symbol (e.g., ETH, USDC)")
                logger.info(f"Checking balance for {token}")
                balance_info = cdp_check_balance(cdp_agent, cdp_config, token)
                
                # Update state with a mock balance update
                function_result = FunctionResult(
                    action_status=FunctionResultStatus.DONE,
                    message=f"Checked balance for {token}",
                    info={
                        "action": "check_token_balance",
                        "token": token,
                        "wallet_tokens": current_state["agent_state"]["wallet_tokens"],
                        "satisfaction_points": 1
                    }
                )
                
                # Update worker and agent state
                current_state = get_payment_processor_worker_state_fn(function_result, current_state)
                current_state = agent.get_agent_state_fn(function_result, current_state)
                
            elif blockchain_choice == "2":
                # Request funds from faucet
                logger.info("Requesting funds from faucet")
                cdp_request_funds(cdp_agent, cdp_config)
                
                # Update state with mock faucet results
                function_result = FunctionResult(
                    action_status=FunctionResultStatus.DONE,
                    message="Requested funds from faucet",
                    info={
                        "action": "process_payment",
                        "payment_type": "faucet",
                        "wallet_tokens": {
                            "ETH": "0.2",
                            "USDC": "200",
                            "USDT": "100",
                            "DAI": "100"
                        },
                        "satisfaction_points": 3
                    }
                )
                
                # Update worker and agent state
                current_state = get_payment_processor_worker_state_fn(function_result, current_state)
                current_state = agent.get_agent_state_fn(function_result, current_state)
                
            elif blockchain_choice == "3":
                # Process payment
                amount = get_user_input("Enter payment amount")
                currency = get_user_input("Enter currency (e.g., ETH, USDC)")
                service = get_user_input("Enter service type (flight, hotel, experience)")
                
                if confirm_action(f"Process payment of {amount} {currency} for {service}"):
                    logger.info(f"Processing payment: {amount} {currency} for {service}")
                    payment_result = cdp_process_payment(cdp_agent, cdp_config, amount, currency, service)
                    
                    # Update the payment processor state
                    function_result = FunctionResult(
                        action_status=FunctionResultStatus.DONE,
                        message=f"Processed {amount} {currency} payment for {service}!",
                        info={
                            "action": "process_payment",
                            "payment_type": "crypto",
                            "amount": float(amount),
                            "currency": currency,
                            "service_type": service,
                            "wallet_balance": current_state["agent_state"]["wallet_balance"] - float(amount),
                            "wallet_tokens": {
                                "ETH": "0.15" if currency == "ETH" else current_state["agent_state"]["wallet_tokens"]["ETH"],
                                "USDC": "150" if currency == "USDC" else current_state["agent_state"]["wallet_tokens"]["USDC"],
                                "USDT": current_state["agent_state"]["wallet_tokens"]["USDT"],
                                "DAI": current_state["agent_state"]["wallet_tokens"]["DAI"]
                            },
                            "satisfaction_points": 10,
                            "completion_percentage": 10
                        }
                    )
                    
                    # Update worker state
                    current_state = get_payment_processor_worker_state_fn(function_result, current_state)
                    
                    # Update agent state
                    current_state = agent.get_agent_state_fn(function_result, current_state)
                    
            elif blockchain_choice == "4":
                # Swap tokens
                from_token = get_user_input("Token to swap from (e.g., ETH)")
                to_token = get_user_input("Token to swap to (e.g., USDC)")
                amount = get_user_input("Amount to swap")
                
                if confirm_action(f"Swap {amount} {from_token} to {to_token}"):
                    logger.info(f"Swapping {amount} {from_token} to {to_token}")
                    swap_result = cdp_swap_tokens(cdp_agent, cdp_config, from_token, to_token, amount)
                    
                    # Update state with swap results
                    function_result = FunctionResult(
                        action_status=FunctionResultStatus.DONE,
                        message=f"Swapped {amount} {from_token} to {to_token}",
                        info={
                            "action": "swap_tokens",
                            "from_token": from_token,
                            "to_token": to_token,
                            "amount": float(amount),
                            "satisfaction_points": 5,
                            "wallet_tokens": {
                                "ETH": "0.05" if from_token == "ETH" else "0.15" if to_token == "ETH" else current_state["agent_state"]["wallet_tokens"]["ETH"],
                                "USDC": "250" if to_token == "USDC" else "50" if from_token == "USDC" else current_state["agent_state"]["wallet_tokens"]["USDC"],
                                "USDT": current_state["agent_state"]["wallet_tokens"]["USDT"],
                                "DAI": current_state["agent_state"]["wallet_tokens"]["DAI"]
                            }
                        }
                    )
                    
                    # Update worker and agent state
                    current_state = get_payment_processor_worker_state_fn(function_result, current_state)
                    current_state = agent.get_agent_state_fn(function_result, current_state)
                    
            elif blockchain_choice == "5":
                # Transfer tokens
                to_address = get_user_input("Recipient address")
                token = get_user_input("Token to transfer (e.g., ETH, USDC)")
                amount = get_user_input("Amount to transfer")
                
                if confirm_action(f"Transfer {amount} {token} to {to_address}"):
                    logger.info(f"Transferring {amount} {token} to {to_address}")
                    transfer_result = cdp_transfer_tokens(cdp_agent, cdp_config, to_address, token, amount)
                    
                    # Update state with transfer results
                    function_result = FunctionResult(
                        action_status=FunctionResultStatus.DONE,
                        message=f"Transferred {amount} {token} to {to_address}",
                        info={
                            "action": "transfer_tokens",
                            "to_address": to_address,
                            "token": token,
                            "amount": float(amount),
                            "transaction_hash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                            "satisfaction_points": 5,
                            "wallet_tokens": {
                                "ETH": "0.08" if token == "ETH" else current_state["agent_state"]["wallet_tokens"]["ETH"],
                                "USDC": "80" if token == "USDC" else current_state["agent_state"]["wallet_tokens"]["USDC"],
                                "USDT": "80" if token == "USDT" else current_state["agent_state"]["wallet_tokens"]["USDT"],
                                "DAI": "80" if token == "DAI" else current_state["agent_state"]["wallet_tokens"]["DAI"]
                            }
                        }
                    )
                    
                    # Update worker and agent state
                    current_state = get_payment_processor_worker_state_fn(function_result, current_state)
                    current_state = agent.get_agent_state_fn(function_result, current_state)
                    
            elif blockchain_choice == "6":
                # Get token price
                token = get_user_input("Token symbol (e.g., ETH, USDC)")
                logger.info(f"Getting price for {token}")
                price_info = cdp_get_token_price(cdp_agent, cdp_config, token)
                
                # No state update needed for price check
                
            elif blockchain_choice == "7":
                # Explore DeFi options
                logger.info("Exploring DeFi options")
                defi_info = cdp_explore_defi_options(cdp_agent, cdp_config)
                
                # No state update needed for exploration
                
            else:
                print("Invalid blockchain action selected.")
        
        # Allow user to provide feedback
        current_state = update_agent_state_with_feedback(current_state)
