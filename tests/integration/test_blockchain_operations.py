"""Integration tests for blockchain components."""

import pytest
from unittest.mock import MagicMock, patch

from src.cdp_integration.payment import PaymentProcessor
from src.blockchain.contract_client import ContractClient
from src.blockchain.token_registry import TokenRegistry
from src.utils.state import StateManager
from src.modes.blockchain_payments import BlockchainPaymentsMode

class TestBlockchainIntegration:
    """Tests for blockchain integration."""
    
    @patch("src.cdp_integration.client.CDPClient")
    @patch("src.blockchain.contract_client.ContractClient")
    def test_payment_processing_flow(self, mock_contract_client, mock_cdp_client):
        """Test the complete payment processing flow."""
        # Setup mocks
        cdp_instance = MagicMock()
        mock_cdp_client.return_value = cdp_instance
        
        contract_instance = MagicMock()
        mock_contract_client.return_value = contract_instance
        contract_instance.process_payment.return_value = "0xabcdef1234567890"
        contract_instance.account = MagicMock(address="0x1234")
        
        # Create payment processor
        payment_processor = PaymentProcessor(cdp_instance)
        payment_processor.contract_client = contract_instance
        
        # Create token registry with mock
        token_registry = TokenRegistry()
        with patch.object(token_registry, "get_token_address") as mock_get_address:
            mock_get_address.return_value = "0x5678"
            payment_processor.token_registry = token_registry
            
            # Create service registry with mock
            with patch.object(payment_processor.service_registry, "get_provider_address") as mock_get_provider:
                mock_get_provider.return_value = "0x9876"
                
                # Process a payment
                result = payment_processor.process_payment(100.0, "USDC", "hotel")
                
                # Verify the result
                assert result == "0xabcdef1234567890"
                mock_get_address.assert_called_once_with("USDC")
                mock_get_provider.assert_called_once()
                contract_instance.process_payment.assert_called_once()
    
    @patch("builtins.input")
    @patch("builtins.print")
    @patch("src.game_agents.agent.TravelManagerAgent")
    @patch("src.cdp_integration.client.CDPClient")
    @patch("src.blockchain.contract_client.ContractClient")
    def test_blockchain_payments_mode(
        self, mock_contract_client, mock_cdp_client, mock_agent, mock_print, mock_input
    ):
        """Test the blockchain payments mode."""
        # Setup mocks
        cdp_instance = MagicMock()
        mock_cdp_client.return_value = cdp_instance
        
        contract_instance = MagicMock()
        mock_contract_client.return_value = contract_instance
        contract_instance.account = MagicMock(address="0x1234")
        
        agent_instance = MagicMock()
        mock_agent.return_value = agent_instance
        agent_instance.process_query.return_value = {
            "response": "I found some great options for your trip!",
            "selected_destination": "Tokyo"
        }
        
        # Mock wallet balance
        cdp_instance.get_wallet_balance.return_value = {
            "ETH": "0.1",
            "USDC": "100",
            "USDT": "50",
            "DAI": "75"
        }
        
        # Mock inputs for menu navigation - check balance, plan trip, exit
        mock_input.side_effect = ["2", "1", "Tokyo", "8"]
        
        # Create and run blockchain payments mode
        with patch.object(BlockchainPaymentsMode, "_check_wallet_balance"):
            mode = BlockchainPaymentsMode()
            mode.run()
        
        # Verify key operations
        cdp_instance.connect_to_network.assert_called_once_with("base-sepolia")
        agent_instance.process_query.assert_called_once()
        mock_print.assert_called()
        
        # Verify state was updated
        state = mode.state_manager.get_state()
        assert state["blockchain_enabled"] is True
        assert state["interaction_mode"] == "blockchain_payments"
        assert state["selected_destination"] == "Tokyo"
