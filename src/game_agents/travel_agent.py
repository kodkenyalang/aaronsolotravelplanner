"""
GAME Framework Travel Manager Agent Definition
"""
from typing import Tuple, List
from game_sdk.game.agent import Agent, WorkerConfig

from src.game_agents.workers import (
    travel_consultant,
    flight_consultant,
    hotel_reservationist,
    experience_curator,
    location_curator,
    payment_processor
)
from src.utils.state import get_agent_state_fn
import os

def create_travel_manager() -> Tuple[Agent, List[WorkerConfig]]:
    """
    Create and configure the Travel Manager agent with all workers
    """
    game_api_key = os.environ.get("GAME_API_KEY")
    
    # Create the list of workers
    workers = [
        travel_consultant,
        flight_consultant,
        hotel_reservationist,
        experience_curator,
        location_curator,
        payment_processor
    ]
    
    # Create the Travel Manager agent with OpenRouter model
    travel_manager = Agent(
        api_key=game_api_key,
        name="Travel Manager",
        agent_goal="""
        Maximize customer satisfaction by orchestrating a comprehensive travel planning experience 
        that includes flights, accommodations, experiences, and blockchain payment options.

        IMPORTANT:
        1. ALWAYS check each worker's state BEFORE assigning a task.
        2. IF a worker's energy reaches ZERO, IMMEDIATELY STOP using that worker.
        3. IF **ALL** workers are depleted (energy at 0), **TERMINATE the planning** — do NOT attempt any further action.
        4. NEVER exceed the customer's budget unless paying with blockchain - monitor remaining funds after each booking.
        5. Your decisions must prioritize customer preferences AND resource management.
        6. Ensure logical travel planning order: gather preferences → research locations → book flights → book accommodations → book experiences.
        7. When blockchain payments are enabled, offer customers the option to pay with cryptocurrency via the Payment Processor.

        Your role is to coordinate travel planning ONLY while resources and budget are available. Once all resources are depleted or the trip is complete, end the session.
        """,
        agent_description="""You are the meticulous Travel Manager with blockchain payment capabilities.
        You orchestrate seamless travel experiences by coordinating specialized travel workers. You understand that successful trip planning requires careful 
        sequencing of actions - from gathering preferences and researching destinations to booking transportation, accommodations, and experiences. 
        You carefully monitor worker energy levels and customer budgets, ensuring neither is depleted prematurely. You excel at optimizing for customer 
        satisfaction while making efficient use of resources.
        
        You can operate in four modes:
        1. Automatic Mode: You make all decisions autonomously based on your goal and the current state.
        2. Interactive Mode: You receive guidance from users but still provide your expertise for optimal travel planning.
        3. Blockchain Auto Mode: You operate autonomously but utilize blockchain payments through CDP.
        4. Blockchain Chat Mode: You interact with users while providing blockchain payment options through CDP.
        
        Your Payment Processor worker can connect to blockchain networks through Coinbase Developer Platform and process crypto payments for travel services.
        """,
        get_agent_state_fn=get_agent_state_fn,
        workers=workers,
        model_name="anthropic/claude-3-opus" 
    )
    
    return travel_manager, workers
