"""
GAME Framework Worker Definitions
"""
from game_sdk.game.custom_types import Function, Argument
from game_sdk.game.agent import WorkerConfig

from src.game_agents.functions import (
    gather_preferences,
    book_flight,
    book_hotel,
    book_experience,
    research_location,
    connect_blockchain,
    process_crypto_payment,
    swap_tokens,
    check_token_balance,
    transfer_tokens
)
from src.utils.state import (
    get_travel_consultant_worker_state_fn,
    get_flight_consultant_worker_state_fn,
    get_hotel_reservationist_worker_state_fn,
    get_experience_curator_worker_state_fn,
    get_location_curator_worker_state_fn,
    get_payment_processor_worker_state_fn
)

# Worker IDs
TRAVEL_CONSULTANT_ID = "travel_consultant"
FLIGHT_CONSULTANT_ID = "flight_consultant"
HOTEL_RESERVATIONIST_ID = "hotel_reservationist"
EXPERIENCE_CURATOR_ID = "experience_curator"
LOCATION_CURATOR_ID = "location_curator"
PAYMENT_PROCESSOR_ID = "payment_processor"

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

connect_blockchain_fn = Function(
    fn_name="connect_blockchain",
    fn_description="Connect to blockchain payment system",
    args=[],
    executable=connect_blockchain
)

process_crypto_payment_fn = Function(
    fn_name="process_crypto_payment",
    fn_description="Process a crypto payment for travel services",
    args=[
        Argument(name="amount", type="string", description="Amount to pay"),
        Argument(name="currency", type="string", description="Cryptocurrency to use (e.g., ETH, USDC)"),
        Argument(name="service_type", type="string", description="Type of service being paid for (flight, hotel, experience)")
    ],
    executable=process_crypto_payment
)

swap_tokens_fn = Function(
    fn_name="swap_tokens",
    fn_description="Swap one token for another using a DEX",
    args=[
        Argument(name="from_token", type="string", description="Token to swap from (e.g., ETH)"),
        Argument(name="to_token", type="string", description="Token to swap to (e.g., USDC)"),
        Argument(name="amount", type="string", description="Amount to swap")
    ],
    executable=swap_tokens,
    return_empty_info_if_error=True  # Added this line
)

check_token_balance_fn = Function(
    fn_name="check_token_balance",
    fn_description="Check token balance in the wallet",
    args=[
        Argument(name="token", type="string", description="Token to check balance for (e.g., ETH, USDC)")
    ],
    executable=check_token_balance
)

transfer_tokens_fn = Function(
    fn_name="transfer_tokens",
    fn_description="Transfer tokens to another address",
    args=[
        Argument(name="to_address", type="string", description="Recipient address"),
        Argument(name="token", type="string", description="Token to transfer (e.g., ETH, USDC)"),
        Argument(name="amount", type="string", description="Amount to transfer")
    ],
    executable=transfer_tokens
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

payment_processor = WorkerConfig(
    id=PAYMENT_PROCESSOR_ID,
    worker_description="Processes blockchain payments for travel services using CDP wallet integration.",
    get_state_fn=get_payment_processor_worker_state_fn,
    action_space=[
        connect_blockchain_fn, 
        process_crypto_payment_fn, 
        swap_tokens_fn,
        check_token_balance_fn,
        transfer_tokens_fn
    ]
)
