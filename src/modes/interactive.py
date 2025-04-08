"""
Interactive mode functionality for the Travel Manager agent
"""
import logging
import json
import time
from typing import List, Optional, Tuple, Dict, Any
from game_sdk.game.agent import Agent, WorkerConfig
from game_sdk.game.custom_types import Function, FunctionResult, FunctionResultStatus

# Get the module logger
logger = logging.getLogger(__name__)

# Mode constants
INTERACTIVE_MODE = "interactive"

def get_user_input(prompt_message: str) -> str:
    """
    Get input from user with the given prompt message.
    Used in Interactive Mode to gather user decisions.
    """
    return input(f"\n{prompt_message}: ")


def confirm_action(action_description: str) -> bool:
    """
    Ask user to confirm an action before execution.
    Used in Interactive Mode for user approval of actions.
    """
    response = input(f"\n⚠️ Confirm action: {action_description} (y/n): ").lower()
    return response == 'y' or response == 'yes'


def display_worker_options(workers: List[WorkerConfig]) -> None:
    """
    Display available workers and their possible actions.
    Provides a menu-like interface for Interactive Mode.
    """
    print("\n🧰 Available Workers:")
    for i, worker in enumerate(workers, 1):
        print(f"{i}. {worker.id.upper()} - {worker.worker_description}")
        print("   Actions:")
        for j, action in enumerate(worker.action_space, 1):
            print(f"   {j}. {action.fn_name} - {action.fn_description}")
        print()


def select_worker_and_action(workers: List[WorkerConfig]) -> Tuple[Optional[WorkerConfig], Optional[Function]]:
    """
    Allow user to select a worker and action in Interactive Mode.
    Returns the selected worker and action objects.
    """
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
    """
    Get parameters for the selected action from user input.
    Used in Interactive Mode to gather action parameters.
    """
    params = {}
    for arg in action.args:
        value = get_user_input(f"Enter {arg.name} ({arg.description})")
        params[arg.name] = value
    return params


def update_agent_state_with_feedback(current_state: dict) -> dict:
    """
    Update agent state based on optional user feedback.
    Allows users to provide subjective input on satisfaction and completion.
    """
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


def run_interactive_mode(agent: Agent, workers: List[WorkerConfig]) -> None:
    """
    Run the agent in interactive mode with user input and guidance.
    This mode allows users to select workers, actions, and provide parameters.
    """
    logger.info("Running in INTERACTIVE MODE")
    print("\n👤 Running in INTERACTIVE MODE - You'll guide the AI decisions\n")
    
    # Update the initial state to indicate interactive mode
    current_state = agent.get_agent_state_fn(None, None)
    current_state["agent_state"]["interaction_mode"] = INTERACTIVE_MODE
    
    print("\n📊 Initial State:")
    print(json.dumps(current_state["agent_state"], indent=4))
    
    while True:
        # Check termination conditions
        all_depleted = all(worker_state["energy"] == 0 
                          for worker_state in current_state["worker_states"].values())
        
        if all_depleted:
            print("\n⚠️ All workers are depleted. Planning terminated.")
            break
            
        if current_state["agent_state"]["trip_completeness"] >= 100:
            print("\n🎉 Trip planning is complete!")
            break
            
        if current_state["agent_state"]["budget_remaining"] <= 0:
            print("\n💸 Budget is exhausted. Planning terminated.")
            break
        
        # Display current state summary
        print("\n📊 Current Status:")
        print(f"Budget: ${current_state['agent_state']['budget_remaining']}")
        print(f"Satisfaction: {current_state['agent_state']['customer_satisfaction']}")
        print(f"Trip Completeness: {current_state['agent_state']['trip_completeness']}%")
        
        # Display AI recommendations
        print("\n🤔 AI Recommendation:")
        print("Based on the current state, the AI would recommend the next steps...")
        time.sleep(1)  # Simulate AI thinking
        
        # Option to get AI recommendation
        if confirm_action("Would you like to see what the AI recommends?"):
            print("\n💡 AI Recommends: Based on the current state of planning, you should:")
            # This would ideally query the AI model for recommendations
            # For now, we'll provide generic advice based on trip completeness
            if current_state["agent_state"]["trip_completeness"] < 20:
                print("- Gather customer preferences first")
                print("- Research potential destinations")
            elif current_state["worker_states"]["flight_consultant"]["flight_booked"] == False:
                print("- Book flights to lock in your travel dates")
            elif current_state["worker_states"]["hotel_reservationist"]["hotel_booked"] == False:
                print("- Book accommodations for your stay")
            else:
                print("- Add experiences to enhance the trip")
                
        # Get user action selection
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
        
        # Allow user to provide feedback
        current_state = update_agent_state_with_feedback(current_state)
        
        # Display result
        print(f"\n✅ Action Result: {result_message}")
