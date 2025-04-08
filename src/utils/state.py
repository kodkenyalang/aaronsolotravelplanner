"""
State management utilities for the Travel Manager CDP application
"""
from typing import Dict, Any
from game_sdk.game.custom_types import FunctionResult, FunctionResultStatus
import json
import logging

# Get the module logger
logger = logging.getLogger(__name__)

# Worker IDs
TRAVEL_CONSULTANT_ID = "travel_consultant"
FLIGHT_CONSULTANT_ID = "flight_consultant"
HOTEL_RESERVATIONIST_ID = "hotel_reservationist"
EXPERIENCE_CURATOR_ID = "experience_curator"
LOCATION_CURATOR_ID = "location_curator"
PAYMENT_PROCESSOR_ID = "payment_processor"

# ---- Initial State ----
init_state = {
    "agent_state": {
        "customer_satisfaction": 0,
        "budget_remaining": 1000,
        "trip_completeness": 0,
        "interaction_mode": None,  # Will be set based on selected mode
        "blockchain_enabled": False,  # Tracks whether blockchain payments are enabled
        "wallet_balance": 0,  # Tracks CDP wallet balance
        "wallet_tokens": {
            "ETH": "0",
            "USDC": "0",
            "USDT": "0",
            "DAI": "0"
        }
    },
    "worker_states": {
        TRAVEL_CONSULTANT_ID: {
            "energy": 100,
            "consultation_status": "not_started",
        },
        FLIGHT_CONSULTANT_ID: {
            "energy": 100,
            "flight_booked": False
        },
        HOTEL_RESERVATIONIST_ID: {
            "energy": 100,
            "hotel_booked": False
        },
        EXPERIENCE_CURATOR_ID: {
            "energy": 100,
            "experiences_booked": 0
        },
        LOCATION_CURATOR_ID: {
            "energy": 100,
            "locations_researched": 0
        },
        PAYMENT_PROCESSOR_ID: {
            "energy": 100,
            "payments_processed": 0,
            "blockchain_connected": False,
            "tokens_swapped": 0,
            "transfers_made": 0
        }
    }
}

# ---- Logging Utility ----
def log_state_change(title: str, state: dict):
    print("\n" + "═" * 60)
    print(f"📦  STATE UPDATE → {title.upper()}".center(60))
    print("═" * 60)
    for key, value in state.items():
        print(f"   • {key:<18} → {value}")
    print("═" * 60 + "\n")


def log_action_info(action: str, info: dict):
    print("\n" + "-" * 60)
    print(f"🔧 {action.upper()} WORKER UPDATE".center(60))
    print("-" * 60)
    print("📤 Action Info:")
    print(json.dumps(info, indent=4))


# ---- Shared Worker State Update ----
def update_worker_state(worker_id: str, function_result: FunctionResult, current_state: dict, updates: dict):
    if function_result is not None:
        info = function_result.info
        log_action_info(worker_id, info)

        if function_result.action_status == FunctionResultStatus.DONE:
            worker_state = current_state["worker_states"][worker_id]

            for key, change in updates.items():
                if key in worker_state:
                    worker_state[key] = max(0, worker_state[key] + change)

            log_state_change(f"Updated Worker State ({worker_id})", worker_state)

    return current_state


# ----- Worker State Functions -----
def get_travel_consultant_worker_state_fn(function_result: FunctionResult, current_state: dict) -> dict:
    if current_state is None:
        logger.info("Initializing travel consultant worker state")
        return init_state

    if function_result and function_result.info.get("action") == "gather_preferences":
        status = function_result.info.get("status", "in_progress")
        current_state["worker_states"][TRAVEL_CONSULTANT_ID]["consultation_status"] = status

    return update_worker_state(
        TRAVEL_CONSULTANT_ID,
        function_result,
        current_state,
        updates={"energy": -10}
    )


def get_flight_consultant_worker_state_fn(function_result: FunctionResult, current_state: dict) -> dict:
    if current_state is None:
        logger.info("Initializing flight consultant worker state")
        return init_state

    if function_result and function_result.info.get("action") == "book_flight":
        current_state["worker_states"][FLIGHT_CONSULTANT_ID]["flight_booked"] = True

    return update_worker_state(
        FLIGHT_CONSULTANT_ID,
        function_result,
        current_state,
        updates={"energy": -20}
    )


def get_hotel_reservationist_worker_state_fn(function_result: FunctionResult, current_state: dict) -> dict:
    if current_state is None:
        logger.info("Initializing hotel reservationist worker state")
        return init_state

    if function_result and function_result.info.get("action") == "book_hotel":
        current_state["worker_states"][HOTEL_RESERVATIONIST_ID]["hotel_booked"] = True

    return update_worker_state(
        HOTEL_RESERVATIONIST_ID,
        function_result,
        current_state,
        updates={"energy": -15}
    )


def get_experience_curator_worker_state_fn(function_result: FunctionResult, current_state: dict) -> dict:
    if current_state is None:
        logger.info("Initializing experience curator worker state")
        return init_state

    if function_result and function_result.info.get("action") == "book_experience":
        current_state["worker_states"][EXPERIENCE_CURATOR_ID]["experiences_booked"] += 1

    return update_worker_state(
        EXPERIENCE_CURATOR_ID,
        function_result,
        current_state,
        updates={"energy": -10}
    )


def get_location_curator_worker_state_fn(function_result: FunctionResult, current_state: dict) -> dict:
    if current_state is None:
        logger.info("Initializing location curator worker state")
        return init_state

    if function_result and function_result.info.get("action") == "research_location":
        current_state["worker_states"][LOCATION_CURATOR_ID]["locations_researched"] += 1

    return update_worker_state(
        LOCATION_CURATOR_ID,
        function_result,
        current_state,
        updates={"energy": -15}
    )


def get_payment_processor_worker_state_fn(function_result: FunctionResult, current_state: dict) -> dict:
    """State management for the blockchain payment processor worker."""
    if current_state is None:
        logger.info("Initializing payment processor worker state")
        return init_state

    if function_result:
        action = function_result.info.get("action", "")
        
        if action == "process_payment":
            current_state["worker_states"][PAYMENT_PROCESSOR_ID]["payments_processed"] += 1
            
            # Update blockchain connection status if provided
            if "blockchain_connected" in function_result.info:
                current_state["worker_states"][PAYMENT_PROCESSOR_ID]["blockchain_connected"] = function_result.info.get("blockchain_connected")
                current_state["agent_state"]["blockchain_enabled"] = function_result.info.get("blockchain_connected")
                
            # Update wallet balance if provided
            if "wallet_balance" in function_result.info:
                current_state["agent_state"]["wallet_balance"] = function_result.info.get("wallet_balance")
                
            # Update wallet tokens if provided
            if "wallet_tokens" in function_result.info:
                current_state["agent_state"]["wallet_tokens"] = function_result.info.get("wallet_tokens")
                
        elif action == "swap_tokens":
            current_state["worker_states"][PAYMENT_PROCESSOR_ID]["tokens_swapped"] += 1
            
            # Update wallet tokens if provided
            if "wallet_tokens" in function_result.info:
                current_state["agent_state"]["wallet_tokens"] = function_result.info.get("wallet_tokens")
                
        elif action == "check_token_balance":
            # Update wallet tokens if provided
            if "wallet_tokens" in function_result.info:
                current_state["agent_state"]["wallet_tokens"] = function_result.info.get("wallet_tokens")
                
        elif action == "transfer_tokens":
            current_state["worker_states"][PAYMENT_PROCESSOR_ID]["transfers_made"] += 1
            
            # Update wallet tokens if provided
            if "wallet_tokens" in function_result.info:
                current_state["agent_state"]["wallet_tokens"] = function_result.info.get("wallet_tokens")

    return update_worker_state(
        PAYMENT_PROCESSOR_ID,
        function_result,
        current_state,
        updates={"energy": -15}
    )


# ----- Agent State Management -----
def get_agent_state_fn(function_result: FunctionResult, current_state: dict) -> dict:
    if current_state is None:
        logger.info("Initializing agent state")
        return init_state

    if function_result is not None:
        info = function_result.info
        print("\n" + "=" * 60)
        print(f"🧠 AGENT UPDATE ({info.get('action', '').upper()})".center(60))
        print("=" * 60)
        print("📤 Action Info:")
        print(json.dumps(info, indent=4))

        # Update budget and satisfaction based on actions
        if "cost" in info:
            cost = info.get("cost", 0)
            current_state["agent_state"]["budget_remaining"] -= cost
            print(f"\n   💰 budget_remaining -{cost} → {current_state['agent_state']['budget_remaining']}")
            
        if "satisfaction_points" in info:
            sat_pts = info.get("satisfaction_points", 0)
            current_state["agent_state"]["customer_satisfaction"] += sat_pts
            print(f"   😊 customer_satisfaction +{sat_pts} → {current_state['agent_state']['customer_satisfaction']}")
            
        if "completion_percentage" in info:
            completion = info.get("completion_percentage", 0)
            current_state["agent_state"]["trip_completeness"] += completion
            print(f"   ✅ trip_completeness +{completion} → {current_state['agent_state']['trip_completeness']}")
            
        # Handle blockchain updates
        if "blockchain_enabled" in info:
            current_state["agent_state"]["blockchain_enabled"] = info.get("blockchain_enabled")
            print(f"   🔗 blockchain_enabled → {current_state['agent_state']['blockchain_enabled']}")
            
        if "wallet_balance" in info:
            current_state["agent_state"]["wallet_balance"] = info.get("wallet_balance")
            print(f"   💼 wallet_balance → {current_state['agent_state']['wallet_balance']}")
            
        if "wallet_tokens" in info:
            current_state["agent_state"]["wallet_tokens"] = info.get("wallet_tokens")
            print(f"   🪙 wallet_tokens → {current_state['agent_state']['wallet_tokens']}")

    log_state_change("Updated Agent State", current_state["agent_state"])
    return current_state
