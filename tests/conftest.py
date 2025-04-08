"""Pytest fixtures for testing Travel Manager CDP."""

import os
import pytest
from unittest.mock import MagicMock, patch

@pytest.fixture
def mock_env():
    """Mock environment variables needed for testing."""
    with patch.dict(os.environ, {
        "GAME_API_KEY": "test_game_api_key",
        "OPENROUTER_API_KEY": "test_openrouter_api_key",
        "CDP_API_KEY": "test_cdp_api_key"
    }):
        yield

@pytest.fixture
def mock_game_sdk():
    """Mock the GAME SDK for testing."""
    with patch("src.game_agents.agent.GameAgent") as mock:
        agent = MagicMock()
        mock.return_value = agent
        yield agent

@pytest.fixture
def mock_cdp_sdk():
    """Mock the CDP SDK for testing."""
    with patch("src.cdp_integration.client.CDPClient") as mock:
        client = MagicMock()
        # Setup common mock responses
        client.get_wallet_balance.return_value = {
            "ETH": "0.1",
            "USDC": "100",
            "USDT": "100",
            "DAI": "100"
        }
        client.process_payment.return_value = "0x1234567890abcdef"
        mock.return_value = client
        yield client

@pytest.fixture
def mock_openrouter():
    """Mock OpenRouter API for testing."""
    with patch("src.utils.llm.get_openrouter_llm") as mock:
        llm = MagicMock()
        llm.invoke.return_value = "AI response"
        mock.return_value = llm
        yield llm

@pytest.fixture
def sample_state():
    """Sample application state for testing."""
    return {
        "customer_satisfaction": 0,
        "budget_remaining": 1000,
        "trip_completeness": 0,
        "interaction_mode": "interactive",
        "blockchain_enabled": False,
        "wallet_balance": 0,
        "wallet_tokens": {
            "ETH": "0",
            "USDC": "0", 
            "USDT": "0",
            "DAI": "0"
        },
        "selected_destination": None,
        "selected_dates": None,
        "flight_details": None,
        "hotel_details": None,
        "experiences": []
    }

@pytest.fixture
def blockchain_state():
    """Sample blockchain-enabled application state for testing."""
    return {
        "customer_satisfaction": 0,
        "budget_remaining": 1000,
        "trip_completeness": 0,
        "interaction_mode": "blockchain_chat",
        "blockchain_enabled": True,
        "wallet_balance": 100,
        "wallet_tokens": {
            "ETH": "0.1",
            "USDC": "100",
            "USDT": "100",
            "DAI": "100"
        },
        "selected_destination": "Tokyo",
        "selected_dates": {"start": "2023-11-15", "end": "2023-11-25"},
        "flight_details": None,
        "hotel_details": None,
        "experiences": []
    }
