"""Integration tests for travel planning functionality."""

import pytest
from unittest.mock import MagicMock, patch

from src.game_agents.agent import TravelManagerAgent
from src.game_agents.workers import TravelConsultantWorker, FlightWorker, HotelWorker
from src.utils.state import StateManager

class TestTravelPlanningFlow:
    """Tests for the travel planning workflow."""
    
    def test_full_travel_planning_flow(self, mock_game_sdk, mock_openrouter, sample_state):
        """Test a complete travel planning flow."""
        # Setup mocks for key components
        agent = TravelManagerAgent()
        state_manager = StateManager(initial_state=sample_state)
        
        travel_consultant = TravelConsultantWorker()
        flight_worker = FlightWorker()
        hotel_worker = HotelWorker()
        
        # Mock the worker operations
        with patch.object(travel_consultant, 'gather_preferences') as mock_gather:
            mock_gather.return_value = {
                "preferences": {
                    "destination": "Tokyo",
                    "budget": 1000,
                    "dates": {"start": "2023-11-15", "end": "2023-11-25"},
                    "interests": ["food", "culture", "shopping"]
                }
            }
            
            with patch.object(flight_worker, 'search_flights') as mock_flights:
                mock_flights.return_value = {
                    "flights": [
                        {
                            "airline": "Japan Airlines",
                            "departure": "2023-11-15 10:00",
                            "arrival": "2023-11-16 14:30",
                            "price": 800,
                            "class": "Economy"
                        }
                    ]
                }
                
                with patch.object(hotel_worker, 'search_hotels') as mock_hotels:
                    mock_hotels.return_value = {
                        "hotels": [
                            {
                                "name": "Tokyo Grand Hotel",
                                "location": "Shinjuku",
                                "check_in": "2023-11-16",
                                "check_out": "2023-11-25",
                                "price": 100,
                                "rating": 4.5
                            }
                        ]
                    }
                    
                    with patch.object(agent, 'get_next_step') as mock_next_step:
                        # First step - gather preferences
                        mock_next_step.return_value = {
                            "recommendation": "Gather customer preferences",
                            "workers": [
                                {
                                    "worker_name": "TRAVEL_CONSULTANT",
                                    "actions": [{"name": "gather_preferences"}]
                                }
                            ]
                        }
                        
                        # Simulate gathering preferences
                        next_step = agent.get_next_step(state_manager.get_state())
                        result = travel_consultant.gather_preferences("")
                        state_manager.update_state({
                            "selected_destination": result["preferences"]["destination"],
                            "selected_dates": result["preferences"]["dates"]
                        })
                        
                        # Now update mock to suggest flight search
                        mock_next_step.return_value = {
                            "recommendation": "Search for flights",
                            "workers": [
                                {
                                    "worker_name": "FLIGHT",
                                    "actions": [{"name": "search_flights"}]
                                }
                            ]
                        }
                        
                        # Simulate searching flights
                        next_step = agent.get_next_step(state_manager.get_state())
                        result = flight_worker.search_flights({
                            "origin": "NYC",
                            "destination": "Tokyo",
                            "departure_date": "2023-11-15",
                            "return_date": "2023-11-25"
                        })
                        state_manager.update_state({
                            "flight_details": result["flights"][0],
                            "budget_remaining": state_manager.get_state()["budget_remaining"] - result["flights"][0]["price"]
                        })
                        
                        # Update mock to suggest hotel search
                        mock_next_step.return_value = {
                            "recommendation": "Search for hotels",
                            "workers": [
                                {
                                    "worker_name": "HOTEL",
                                    "actions": [{"name": "search_hotels"}]
                                }
                            ]
                        }
                        
                        # Simulate searching hotels
                        next_step = agent.get_next_step(state_manager.get_state())
                        result = hotel_worker.search_hotels({
                            "destination": "Tokyo",
                            "check_in": "2023-11-16",
                            "check_out": "2023-11-25",
                            "guests": 2
                        })
                        state_manager.update_state({
                            "hotel_details": result["hotels"][0],
                            "budget_remaining": state_manager.get_state()["budget_remaining"] - result["hotels"][0]["price"],
                            "trip_completeness": 75,
                            "customer_satisfaction": 8
                        })
                        
                        # Verify final state
                        final_state = state_manager.get_state()
                        assert final_state["selected_destination"] == "Tokyo"
                        assert final_state["flight_details"] is not None
                        assert final_state["hotel_details"] is not None
                        assert final_state["budget_remaining"] == 100  # 1000 - 800 - 100
                        assert final_state["trip_completeness"] == 75
                        assert final_state["customer_satisfaction"] == 8
