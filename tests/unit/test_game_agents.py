"""Unit tests for the GAME agents module."""

import pytest
from unittest.mock import MagicMock, patch

from src.game_agents.agent import TravelManagerAgent
from src.game_agents.workers import (
    TravelConsultantWorker,
    FlightWorker,
    HotelWorker,
    ExperienceWorker,
    PaymentWorker
)

class TestTravelManagerAgent:
    """Tests for the TravelManagerAgent class."""
    
    def test_initialization(self, mock_game_sdk, mock_openrouter):
        """Test agent initialization."""
        agent = TravelManagerAgent()
        assert agent is not None
        assert hasattr(agent, "workers")
    
    def test_process_query(self, mock_game_sdk, mock_openrouter):
        """Test processing a user query."""
        agent = TravelManagerAgent()
        result = agent.process_query("I want to plan a trip to Tokyo")
        assert result is not None
        # Check that proper methods were called
        mock_game_sdk.submit_task.assert_called_once()
    
    def test_get_next_step(self, mock_game_sdk, mock_openrouter, sample_state):
        """Test getting the next step in travel planning."""
        agent = TravelManagerAgent()
        next_step = agent.get_next_step(sample_state)
        assert next_step is not None
        assert isinstance(next_step, dict)
        assert "recommendation" in next_step

class TestTravelWorkers:
    """Tests for the various travel worker classes."""
    
    def test_travel_consultant_worker(self, mock_openrouter):
        """Test the travel consultant worker."""
        worker = TravelConsultantWorker()
        result = worker.gather_preferences("I want to go somewhere warm")
        assert result is not None
        assert isinstance(result, dict)
        assert "preferences" in result
    
    def test_flight_worker(self, mock_openrouter):
        """Test the flight worker."""
        worker = FlightWorker()
        result = worker.search_flights({
            "origin": "NYC",
            "destination": "Tokyo",
            "departure_date": "2023-11-15",
            "return_date": "2023-11-25"
        })
        assert result is not None
        assert isinstance(result, dict)
        assert "flights" in result
    
    def test_hotel_worker(self, mock_openrouter):
        """Test the hotel worker."""
        worker = HotelWorker()
        result = worker.search_hotels({
            "destination": "Tokyo",
            "check_in": "2023-11-15",
            "check_out": "2023-11-25",
            "guests": 2
        })
        assert result is not None
        assert isinstance(result, dict)
        assert "hotels" in result
    
    def test_experience_worker(self, mock_openrouter):
        """Test the experience worker."""
        worker = ExperienceWorker()
        result = worker.find_experiences({
            "destination": "Tokyo",
            "dates": {"start": "2023-11-15", "end": "2023-11-25"},
            "preferences": ["cultural", "food"]
        })
        assert result is not None
        assert isinstance(result, dict)
        assert "experiences" in result
    
    def test_payment_worker(self, mock_openrouter):
        """Test the payment worker."""
        worker = PaymentWorker()
        result = worker.process_payment({
            "amount": 100,
            "currency": "USD",
            "service_type": "hotel"
        })
        assert result is not None
        assert isinstance(result, dict)
        assert "payment_status" in result
