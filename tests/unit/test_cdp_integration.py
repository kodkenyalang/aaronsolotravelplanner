"""Unit tests for the CDP integration module."""

import pytest
from unittest.mock import MagicMock, patch

from src.cdp_integration.client import CDPClient
from src.cdp_integration.wallet import WalletManager
from src.cdp_integration.payment import PaymentProcessor

class TestCDPClient:
    """Tests for the CDPClient class."""
    
    def test_initialization(self, mock_env):
        """Test client initialization."""
        with patch("src.cdp_integration.client.CDPClient._init_client") as mock_init:
            client = CDPClient()
            assert client is not None
            mock_init.assert_called_once()
    
    def test_connect_to_network(self, mock_cdp_sdk):
        """Test connecting to blockchain network."""
        client = CDPClient()
        result = client.connect_to_network("base-sepolia")
        assert result is not None
        mock_cdp_sdk.connect.assert_called_once_with("base-sepolia")

class TestWalletManager:
    """Tests for the WalletManager class."""
    
    def test_get_wallet_balance(self, mock_cdp_sdk):
        """Test getting wallet balance."""
        wallet_manager = WalletManager(mock_cdp_sdk)
        balance = wallet_manager.get_wallet_balance()
        assert balance is not None
        assert isinstance(balance, dict)
        assert "ETH" in balance
        mock_cdp_sdk.get_wallet_balance.assert_called_once()
    
    def test_request_funds_from_faucet(self, mock_cdp_sdk):
        """Test requesting funds from faucet."""
        mock_cdp_sdk.request_from_faucet.return_value = {
            "txHash": "0xabcdef",
            "token": "ETH",
            "amount": "0.1"
        }
        wallet_manager = WalletManager(mock_cdp_sdk)
        result = wallet_manager.request_funds_from_faucet("ETH")
        assert result is not None
        assert "txHash" in result
        mock_cdp_sdk.request_from_faucet.assert_called_once_with("ETH")

class TestPaymentProcessor:
    """Tests for the PaymentProcessor class."""
    
    def test_process_payment(self, mock_cdp_sdk):
        """Test processing payment."""
        payment_processor = PaymentProcessor(mock_cdp_sdk)
        tx_hash = payment_processor.process_payment(100, "USDC", "hotel")
        assert tx_hash is not None
        assert isinstance(tx_hash, str)
        mock_cdp_sdk.process_payment.assert_called_once()
    
    def test_swap_tokens(self, mock_cdp_sdk):
        """Test swapping tokens."""
        mock_cdp_sdk.swap_tokens.return_value = {
            "txHash": "0x9876543210",
            "fromToken": "ETH",
            "toToken": "USDC",
            "fromAmount": "0.1",
            "toAmount": "180"
        }
        payment_processor = PaymentProcessor(mock_cdp_sdk)
        result = payment_processor.swap_tokens("ETH", "USDC", "0.1")
        assert result is not None
        assert "txHash" in result
        mock_cdp_sdk.swap_tokens.assert_called_once_with("ETH", "USDC", "0.1")
