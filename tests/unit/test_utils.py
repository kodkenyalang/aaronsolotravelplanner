"""Unit tests for the utils module."""

import pytest
from unittest.mock import MagicMock, patch

from src.utils.state import StateManager
from src.utils.llm import get_openrouter_llm
from src.utils.config import load_config

class TestStateManager:
    """Tests for the StateManager class."""
    
    def test_initialization(self):
        """Test state manager initialization."""
        state_manager = StateManager()
        assert state_manager is not None
        assert state_manager.get_state() is not None
    
    def test_update_state(self, sample_state):
        """Test updating state."""
        state_manager = StateManager(initial_state=sample_state)
        state_manager.update_state({
            "customer_satisfaction": 5,
            "selected_destination": "Tokyo"
        })
        updated_state = state_manager.get_state()
        assert updated_state["customer_satisfaction"] == 5
        assert updated_state["selected_destination"] == "Tokyo"
        assert updated_state["budget_remaining"] == 1000  # Unchanged
    
    def test_reset_state(self, sample_state):
        """Test resetting state."""
        state_manager = StateManager(initial_state=sample_state)
        state_manager.update_state({"customer_satisfaction": 5})
        state_manager.reset_state()
        assert state_manager.get_state()["customer_satisfaction"] == 0

class TestLLMUtils:
    """Tests for the LLM utility functions."""
    
    def test_get_openrouter_llm(self, mock_env):
        """Test getting OpenRouter LLM client."""
        with patch("src.utils.llm.openrouter") as mock_openrouter:
            mock_openrouter.OpenRouter.return_value = MagicMock()
            llm = get_openrouter_llm()
            assert llm is not None
            mock_openrouter.OpenRouter.assert_called_once()

class TestConfigUtils:
    """Tests for the config utility functions."""
    
    def test_load_config(self):
        """Test loading configuration."""
        with patch("src.utils.config.load_dotenv") as mock_load_dotenv:
            with patch("src.utils.config.os.getenv") as mock_getenv:
                mock_getenv.side_effect = lambda key, default=None: {
                    "GAME_API_KEY": "test_key",
                    "OPENROUTER_API_KEY": "test_key",
                    "CDP_API_KEY": "test_key"
                }.get(key, default)
                
                config = load_config()
                assert config is not None
                assert "GAME_API_KEY" in config
                assert "OPENROUTER_API_KEY" in config
                assert "CDP_API_KEY" in config
                mock_load_dotenv.assert_called_once()
