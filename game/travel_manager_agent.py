from game_sdk.game.agent import Agent, WorkerConfig
from game_sdk.game.custom_types import Function, Argument, FunctionResult, FunctionResultStatus
from typing import Tuple, Optional, List, Dict, Any
import os
from dotenv import load_dotenv
import json
import time

load_dotenv()

game_api_key = os.environ.get("GAME_API_KEY")

# Worker IDs
TRAVEL_CONSULTANT_ID = "travel_consultant"
FLIGHT_CONSULTANT_ID = "flight_consultant"
HOTEL_RESERVATIONIST_ID = "hotel_reservationist"
EXPERIENCE_CURATOR_ID = "experience_curator"
LOCATION_CURATOR_ID = "location_curator"

# ---- Mode Configuration ----
AUTOMATIC_MODE = "automatic"  # AI makes all decisions autonomously
INTERACTIVE_MODE = "interactive"  # User provides input and guidance

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


# ---- User Interaction Functions ----
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


# ---- Initial State ----
init_state = {
    "agent_state": {
        "customer_satisfaction": 0,
        "budget_remaining": 1000,
        "trip_completeness": 0,
        "interaction_mode": None,  # Will be set based on selected mode
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
        }
    }
}


# ----- Worker State Functions -----
def get_travel_consultant_worker_state_fn(function_result: FunctionResult, current_state: dict) -> dict:
    if current_state is None:
        print("[WORKER STATE INIT] Initialized new worker state.")
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
        print("[WORKER STATE INIT] Initialized new worker state.")
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
        print("[WORKER STATE INIT] Initialized new worker state.")
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
        print("[WORKER STATE INIT] Initialized new worker state.")
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
        print("[WORKER STATE INIT] Initialized new worker state.")
        return init_state

    if function_result and function_result.info.get("action") == "research_location":
        current_state["worker_states"][LOCATION_CURATOR_ID]["locations_researched"] += 1

    return update_worker_state(
        LOCATION_CURATOR_ID,
        function_result,
        current_state,
        updates={"energy": -15}
    )


# ----- Agent State Management -----
def get_agent_state_fn(function_result: FunctionResult, current_state: dict) -> dict:
    print(f"\n\n 🧳🧳🧳 Using get agent state → current state: {current_state}🧳🧳🧳")

    if current_state is None:
        print("[AGENT STATE INIT] Initialized new agent state...")
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

    log_state_change("Updated Agent State", current_state["agent_state"])
    return current_state


# ----- Worker Functions -----
def gather_preferences(preference_type: str, **kwargs) -> Tuple[FunctionResultStatus, str, dict]:
    print(f"\n\n🧳 [gather_preferences] ➡️ Gathering {preference_type} preferences 🧳\n")
    return FunctionResultStatus.DONE, f"Preferences for {preference_type} gathered!", {
        "action": "gather_preferences",
        "status": "completed",
        "preference_type": preference_type,
        "satisfaction_points": 5,
        "completion_percentage": 10
    }


def book_flight(destination: str, departure_date: str, return_date: str, **kwargs) -> Tuple[FunctionResultStatus, str, dict]:
    print(f"\n\n✈️ [book_flight] Booking flight to {destination} ({departure_date} - {return_date}) ✈️\n")
    return FunctionResultStatus.DONE, f"Flight to {destination} booked successfully!", {
        "action": "book_flight",
        "destination": destination,
        "departure_date": departure_date,
        "return_date": return_date,
        "cost": 300,
        "satisfaction_points": 15,
        "completion_percentage": 25
    }


def book_hotel(hotel_name: str, check_in: str, check_out: str, **kwargs) -> Tuple[FunctionResultStatus, str, dict]:
    print(f"\n\n🏨 [book_hotel] Booking {hotel_name} ({check_in} - {check_out}) 🏨\n")
    return FunctionResultStatus.DONE, f"Hotel {hotel_name} booked successfully!", {
        "action": "book_hotel",
        "hotel_name": hotel_name,
        "check_in": check_in,
        "check_out": check_out,
        "cost": 200,
        "satisfaction_points": 10,
        "completion_percentage": 20
    }


def book_experience(experience_name: str, date: str, **kwargs) -> Tuple[FunctionResultStatus, str, dict]:
    print(f"\n\n🎭 [book_experience] Booking experience: {experience_name} on {date} 🎭\n")
    return FunctionResultStatus.DONE, f"Experience {experience_name} booked successfully!", {
        "action": "book_experience",
        "experience_name": experience_name,
        "date": date,
        "cost": 50,
        "satisfaction_points": 8,
        "completion_percentage": 5
    }


def research_location(location: str, **kwargs) -> Tuple[FunctionResultStatus, str, dict]:
    print(f"\n\n🗺️ [research_location] Researching location: {location} 🗺️\n")
    return FunctionResultStatus.DONE, f"Research on {location} completed!", {
        "action": "research_location",
        "location": location,
        "satisfaction_points": 3,
        "completion_percentage": 5
    }


# ----- Function Declarations -----
gather_preferences_fn = Function(
    fn_name="gather_preferences",
    fn_description="Gather travel preferences from the customer",
    args=[Argument(name="preference_type", type="string", description="Type of preferences to gather (accommodation, activities, budget, etc.)")],
    executable=gather_preferences
)

book_flight_fn = Function(
    fn_name="book_flight",
    fn_description="Book a flight for the trip",
    args=[
        Argument(name="destination", type="string", description="Destination city/airport"),
        Argument(name="departure_date", type="string", description="Date of departure"),
        Argument(name="return_date", type="string", description="Date of return")
    ],
    executable=book_flight
)

book_hotel_fn = Function(
    fn_name="book_hotel",
    fn_description="Book a hotel for the trip",
    args=[
        Argument(name="hotel_name", type="string", description="Name of the hotel"),
        Argument(name="check_in", type="string", description="Check-in date"),
        Argument(name="check_out", type="string", description="Check-out date")
    ],
    executable=book_hotel
)

book_experience_fn = Function(
    fn_name="book_experience",
    fn_description="Book an experience or activity",
    args=[
        Argument(name="experience_name", type="string", description="Name of the experience/activity"),
        Argument(name="date", type="string", description="Date for the experience")
    ],
    executable=book_experience
)

research_location_fn = Function(
    fn_name="research_location",
    fn_description="Research information about a location",
    args=[Argument(name="location", type="string", description="Location to research")],
    executable=research_location
)


# ----- Workers -----
travel_consultant = WorkerConfig(
    id=TRAVEL_CONSULTANT_ID,
    worker_description="Collects and analyzes customer travel preferences and requirements.",
    get_state_fn=get_travel_consultant_worker_state_fn,
    action_space=[gather_preferences_fn]
)

flight_consultant = WorkerConfig(
    id=FLIGHT_CONSULTANT_ID,
    worker_description="Specializes in finding and booking optimal flights based on customer preferences.",
    get_state_fn=get_flight_consultant_worker_state_fn,
    action_space=[book_flight_fn]
)

hotel_reservationist = WorkerConfig(
    id=HOTEL_RESERVATIONIST_ID,
    worker_description="Expert in hotel accommodations and booking the best options for customers.",
    get_state_fn=get_hotel_reservationist_worker_state_fn,
    action_space=[book_hotel_fn]
)

experience_curator = WorkerConfig(
    id=EXPERIENCE_CURATOR_ID,
    worker_description="Discovers and books unique experiences and activities for travelers.",
    get_state_fn=get_experience_curator_worker_state_fn,
    action_space=[book_experience_fn]
)

location_curator = WorkerConfig(
    id=LOCATION_CURATOR_ID,
    worker_description="Researches destinations and provides detailed information about locations.",
    get_state_fn=get_location_curator_worker_state_fn,
    action_space=[research_location_fn]
)

# ----- Travel Manager Agent -----
travel_manager = Agent(
    api_key=game_api_key,
    name="Travel Manager",
    agent_goal = """
    Maximize customer satisfaction by orchestrating a comprehensive travel planning experience 
    that includes flights, accommodations, and activities within budget constraints.

    IMPORTANT:
    1. ALWAYS check each worker's state BEFORE assigning a task.
    2. IF a worker's energy reaches ZERO, IMMEDIATELY STOP using that worker.
    3. IF **ALL** workers are depleted (energy at 0), **TERMINATE the planning** — do NOT attempt any further action.
    4. NEVER exceed the customer's budget - monitor remaining funds after each booking.
    5. Your decisions must prioritize customer preferences AND resource management.
    6. Ensure logical travel planning order: gather preferences → research locations → book flights → book accommodations → book experiences.

    Your role is to coordinate travel planning ONLY while resources and budget are available. Once all resources are depleted or the trip is complete, end the session.
    """,
    agent_description="""You are the meticulous Travel Manager.
    You orchestrate seamless travel experiences by coordinating specialized travel workers. You understand that successful trip planning requires careful 
    sequencing of actions - from gathering preferences and researching destinations to booking transportation, accommodations, and experiences. 
    You carefully monitor worker energy levels and customer budgets, ensuring neither is depleted prematurely. You excel at optimizing for customer 
    satisfaction while making efficient use of resources.
    
    You can operate in two modes:
    1. Automatic Mode: You make all decisions autonomously based on your goal and the current state.
    2. Interactive Mode: You receive guidance from users but still provide your expertise for optimal travel planning.
    """,
    get_agent_state_fn=get_agent_state_fn,
    workers=[travel_consultant, flight_consultant, hotel_reservationist, experience_curator, location_curator],
    model_name="Llama-3.1-405B-Instruct" 
)


# ----- Mode-specific Execution Functions -----
def run_automatic_mode(agent: Agent) -> None:
    """
    Run the agent in fully automatic mode.
    In this mode, the AI makes all decisions without user input.
    """
    print("\n🤖 Running in AUTOMATIC MODE - AI will make all decisions\n")
    
    # Update the initial state to indicate automatic mode
    init_state["agent_state"]["interaction_mode"] = AUTOMATIC_MODE
    
    # Run the agent with standard execution
    agent.run()


def run_interactive_mode(agent: Agent, workers: List[WorkerConfig]) -> None:
    """
    Run the agent in interactive mode with user input and guidance.
    This mode allows users to select workers, actions, and provide parameters.
    """
    print("\n👤 Running in INTERACTIVE MODE - You'll guide the AI decisions\n")
    
    # Update the initial state to indicate interactive mode
    init_state["agent_state"]["interaction_mode"] = INTERACTIVE_MODE
    
    # Initialize state
    current_state = agent.get_agent_state_fn(None, None)
    print("\n📊 Initial State:")
    log_state_change("Agent State", current_state["agent_state"])
    
    for worker_id, worker_state in current_state["worker_states"].items():
        log_state_change(f"Worker State ({worker_id})", worker_state)
    
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
            elif current_state["worker_states"][FLIGHT_CONSULTANT_ID]["flight_booked"] == False:
                print("- Book flights to lock in your travel dates")
            elif current_state["worker_states"][HOTEL_RESERVATIONIST_ID]["hotel_booked"] == False:
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


# ----- Mode Selection Function -----
def select_operating_mode() -> str:
    """
    Allow user to select the operating mode.
    Returns the selected mode identifier.
    """
    print("\n🔄 Select Operating Mode:")
    print("1. Automatic Mode - AI makes all decisions")
    print("2. Interactive Mode - You guide the AI decisions")
    
    choice = get_user_input("Enter choice (1 or 2)")
    
    if choice == "1":
        return AUTOMATIC_MODE
    else:
        return INTERACTIVE_MODE


# ----- Compile and Run -----
print("\n🧳 Launching Travel Planning System...\n")
travel_manager.compile()

# Ask user to select operating mode
operating_mode = select_operating_mode()

# Run the appropriate mode
if operating_mode == AUTOMATIC_MODE:
    run_automatic_mode(travel_manager)
else:
    run_interactive_mode(travel_manager, [
        travel_consultant, 
        flight_consultant, 
        hotel_reservationist, 
        experience_curator, 
        location_curator
    ])
