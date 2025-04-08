"""Unit tests for the modes module."""

import pytest
from unittest.mock import MagicMock, patch

from src.modes.automatic import AutomaticMode
from src.modes.interactive import InteractiveMode
from src.modes.blockchain_auto import BlockchainAutoMode
from src.modes.blockchain_chat import BlockchainChatMode

class TestAutomaticMode:
    """Tests for the AutomaticMode class."""
    
    def test_initialization(self, mock_game_sdk, mock_openrouter):
        """Test mode initialization."""
        mode = AutomaticMode()
        assert mode is not None
        assert hasattr(mode, "state_manager")
        assert hasattr(mode, "agent")
    
    def test_run(self, mock_game_sdk, mock_openrouter, sample_state):
        """Test running automatic mode."""
        with patch("src.modes.automatic.TravelManagerAgent") as mock_agent:
            agent_instance = MagicMock()
            mock_agent.return_value = agent_instance
            
            with patch("src.modes.automatic.StateManager") as mock_state:
                state_instance = MagicMock()
                state_instance.get_state.return_value = sample_state
                mock_state.return_value = state_instance
                
                mode = AutomaticMode()
                with patch("builtins.print"):  # Suppress print statements
                    mode.run()
                
                agent_instance.process_query.assert_called()
                state_instance.update_state.assert_called()

class TestInteractiveMode:
    """Tests for the InteractiveMode class."""
    
    def test_initialization(self, mock_game_sdk, mock_openrouter):
        """Test mode initialization."""
        mode = InteractiveMode()
        assert mode is not None
        assert hasattr(mode, "state_manager")
        assert hasattr(mode, "agent")
    
    def test_run(self, mock_game_sdk, mock_openrouter, sample_state):
        """Test running interactive mode."""
        with patch("src.modes.interactive.TravelManagerAgent") as mock_agent:
            agent_instance = MagicMock()
            agent_instance.get_next_step.return_value = {
                "recommendation": "Test recommendation",
                "workers": [{"worker_name": "TRAVEL_CONSULTANT", "actions": [{"name": "gather_preferences"}]}]
            }
            mock_agent.return_value = agent_instance
            
            with patch("src.modes.interactive.StateManager") as mock_state:
                state_instance = MagicMock()
                state_instance.get_state.return_value = sample_state
                mock_state.return_value = state_instance
                
                with patch("builtins.input") as mock_input:
                    # Mock user inputs for the interactive session
                    mock_input.side_effect = ["y", "1", "1", "q"]
                    
                    mode = InteractiveMode()
                    with patch("builtins.print"):  # Suppress print statements
                        mode.run()
                    
                    agent_instance.get_next_step.assert_called()
                    state_instance.update_state.assert_called()

class TestBlockchainModes:
    """Tests for the blockchain-enabled modes."""
    
    def test_blockchain_auto_mode(self, mock_game_sdk, mock_cdp_sdk, mock_openrouter, blockchain_state):
        """Test running blockchain auto mode."""
        with patch("src.modes.blockchain_auto.TravelManagerAgent") as mock_agent:
            agent_instance = MagicMock()
            mock_agent.return_value = agent_instance
            
            with patch("src.modes.blockchain_auto.StateManager") as mock_state:
                state_instance = MagicMock()
                state_instance.get_state.return_value = blockchain_state
                mock_state.return_value = state_instance
                
                with patch("src.modes.blockchain_auto.CDPClient") as mock_cdp:
                    cdp_instance = MagicMock()
                    mock_cdp.return_value = cdp_instance
                    
                    mode = BlockchainAutoMode()
                    with patch("builtins.print"):  # Suppress print statements
                        mode.run()
                    
                    agent_instance.process_query.assert_called()
                    state_instance.update_state.assert_called()
                    cdp_instance.connect_to_network.assert_called()
    
    def test_blockchain_chat_mode(self, mock_game_sdk, mock_cdp_sdk, mock_openrouter, blockchain_state):
        """Test running blockchain chat mode."""
        with patch("src.modes.blockchain_chat.TravelManagerAgent") as mock_agent:
            agent_instance = MagicMock()
            agent_instance.get_next_step.return_value = {
                "recommendation": "Test recommendation",
                "workers": [{"worker_name": "TRAVEL_CONSULTANT", "actions": [{"name": "gather_preferences"}]}]
            }
            mock_agent.return_value = agent_instance
            
            with patch("src.modes.blockchain_chat.StateManager") as mock_state:
                state_instance = MagicMock()
                state_instance.get_state.return_value = blockchain_state
                mock_state.return_value = state_instance
                
                with patch("src.modes.blockchain_chat.CDPClient") as mock_cdp:
                    cdp_instance = MagicMock()
                    mock_cdp.return_value = cdp_instance
                    
                    with patch("builtins.input") as mock_input:
                        # Mock user inputs for the interactive session
                        mock_input.side_effect = ["3", "100", "USDC", "hotel", "y", "q"]
                        
                        mode = BlockchainChatMode()
                        with patch("builtins.print"):  # Suppress print statements
                            mode.run()
                        
                        agent_instance.get_next_step.assert_called()
                        state_instance.update_state.assert_called()
                        cdp_instance.connect_to_network.assert_called()
