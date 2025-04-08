"""Integration tests for blockchain operations."""

import pytest
from unittest.mock import MagicMock, patch

from src.cdp_integration.client import CDPClient
from src.cdp_integration.wallet import WalletManager
from src.cdp_integration.payment import PaymentProcessor
from src.utils.state import StateManager

class TestBlockchainOperationsFlow:
    """Tests for the blockchain operations workflow."""
    
    def test_full_blockchain_payment_flow(self, mock_cdp_sdk, blockchain_state):
        """Test a complete blockchain payment flow."""
        # Setup components
        cdp_client = CDPClient()
        wallet_manager = WalletManager(cdp_client)
        payment_processor = PaymentProcessor(cdp_client)
        state_manager = StateManager(initial_state=blockchain_state)
        
        # Mock responses for operations
        mock_cdp_sdk.get_wallet_balance.return_value = {
            "ETH": "0.1",
            "USDC": "100",
            "USDT": "100",
            "DAI": "100"
        }
        
        mock_cdp_sdk.get_token_price.return_value = {
            "token": "USDC",
            "price_usd": "1.00"
        }
        
        mock_cdp_sdk.process_payment.return_value = "0x1234567890abcdef"
        
        # Step 1: Connect to network
        cdp_client.connect_to_network("base-sepolia")
        
        # Step 2: Check wallet balance
        balance = wallet_manager.get_wallet_balance()
        state_manager.update_state({
            "wallet_tokens": balance
        })
        
        # Check that the balance is correctly updated
        assert state_manager.get_state()["wallet_tokens"]["USDC"] == "100"
        
        # Step 3: Get token price
        token_price = cdp_client.get_token_price("USDC")
        assert token_price["price_usd"] == "1.00"
        
        # Step 4: Process hotel payment
        tx_hash = payment_processor.process_payment(100, "USDC", "hotel")
        
        # Update state with payment info
        hotel_payment = {
            "amount": 100,
            "currency": "USDC",
            "service_type": "hotel",
            "transaction_hash": tx_hash
        }
        
        state_manager.update_state({
            "payments": [hotel_payment],
            "wallet_tokens": {
                "ETH": "0.1",
                "USDC": "0",  # After spending 100 USDC
                "USDT": "100",
                "DAI": "100"
            }
        })
        
        # Verify final state after payment
        final_state = state_manager.get_state()
        assert len(final_state["payments"]) == 1
        assert final_state["payments"][0]["transaction_hash"] == "0x1234567890abcdef"
        assert final_state["wallet_tokens"]["USDC"] == "0"  # Spent all USDC
        
        # Step 5: Test token swap (ETH to USDC)
        mock_cdp_sdk.swap_tokens.return_value = {
            "txHash": "0x9876543210",
            "fromToken": "ETH",
            "toToken": "USDC",
            "fromAmount": "0.05",
            "toAmount": "90"
        }
        
        swap_result = payment_processor.swap_tokens("ETH", "USDC", "0.05")
        
        # Update state with new balances after swap
        state_manager.update_state({
            "wallet_tokens": {
                "ETH": "0.05",  # 0.1 - 0.05
                "USDC": "90",   # 0 + 90
                "USDT": "100",
                "DAI": "100"
            }
        })
        
        # Verify state after swap
        final_state = state_manager.get_state()
        assert final_state["wallet_tokens"]["ETH"] == "0.05"
        assert final_state["wallet_tokens"]["USDC"] == "90"
