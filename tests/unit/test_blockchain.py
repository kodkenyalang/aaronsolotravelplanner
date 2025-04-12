"""Unit tests for the blockchain module."""

import pytest
from unittest.mock import MagicMock, patch

from src.blockchain.contract_client import ContractClient
from src.blockchain.token_registry import TokenRegistry
from src.blockchain.service_provider import ServiceProviderRegistry

class TestContractClient:
    """Tests for the ContractClient class."""
    
    @patch("src.blockchain.contract_client.Web3")
    @patch("src.blockchain.contract_client.os")
    def test_initialization(self, mock_os, mock_web3):
        """Test client initialization with mocked Web3."""
        # Setup mocks
        mock_web3_instance = MagicMock()
        mock_web3.return_value = mock_web3_instance
        mock_web3_instance.is_connected.return_value = True
        mock_web3_instance.eth.contract.return_value = MagicMock()
        mock_web3_instance.eth.account.from_key.return_value = MagicMock()
        
        # Setup environment variables
        mock_os.getenv.side_effect = lambda key, default=None: {
            "WEB3_PROVIDER_URL": "https://sepolia.base.org",
            "PRIVATE_KEY": "0x1234567890abcdef",
            "PAYMENT_PROCESSOR_ADDRESS": "0x1234567890123456789012345678901234567890",
            "LOYALTY_TOKEN_ADDRESS": "0x1234567890123456789012345678901234567890"
        }.get(key, default)
        
        # Mock loading ABI
        with patch.object(ContractClient, "_load_contract_abi") as mock_load_abi:
            mock_load_abi.return_value = []
            
            # Initialize client
            client = ContractClient()
            
            # Verify initialization
            assert client is not None
            assert client.web3 is not None
            mock_web3_instance.is_connected.assert_called_once()
            mock_web3_instance.eth.contract.assert_called()
    
    @patch("src.blockchain.contract_client.Web3")
    @patch("src.blockchain.contract_client.os")
    def test_process_payment(self, mock_os, mock_web3):
        """Test processing a payment through the contract."""
        # Setup mocks
        mock_web3_instance = MagicMock()
        mock_web3.return_value = mock_web3_instance
        mock_web3_instance.is_connected.return_value = True
        
        # Setup mock contract and functions
        mock_contract = MagicMock()
        mock_web3_instance.eth.contract.return_value = mock_contract
        
        # Setup mock ERC20 contract
        mock_erc20 = MagicMock()
        mock_web3_instance.eth.contract.side_effect = [mock_contract, mock_contract, mock_erc20]
        
        # Setup function calls
        mock_approve_func = MagicMock()
        mock_erc20.functions.approve.return_value = mock_approve_func
        mock_approve_func.build_transaction.return_value = {"test": "tx"}
        
        mock_process_func = MagicMock()
        mock_contract.functions.processPayment.return_value = mock_process_func
        mock_process_func.build_transaction.return_value = {"test": "tx"}
        
        # Setup transaction signing and sending
        mock_web3_instance.eth.account.sign_transaction.return_value = MagicMock(
            rawTransaction=b"raw_tx"
        )
        mock_web3_instance.eth.send_raw_transaction.return_value = b"tx_hash"
        mock_web3_instance.to_hex.return_value = "0xabcdef"
        
        # Setup environment variables
        mock_os.getenv.side_effect = lambda key, default=None: {
            "WEB3_PROVIDER_URL": "https://sepolia.base.org",
            "PRIVATE_KEY": "0x1234567890abcdef",
            "PAYMENT_PROCESSOR_ADDRESS": "0x1234567890123456789012345678901234567890",
            "LOYALTY_TOKEN_ADDRESS": "0x1234567890123456789012345678901234567890"
        }.get(key, default)
        
        # Mock loading ABI
        with patch.object(ContractClient, "_load_contract_abi") as mock_load_abi:
            mock_load_abi.return_value = []
            
            # Initialize client with mock account
            client = ContractClient()
            client.account = MagicMock(address="0x1234")
            
            # Process payment
            token_address = "0x5678"
            amount = 100
            service_type = "hotel"
            recipient = "0x9876"
            
            result = client.process_payment(token_address, amount, service_type, recipient)
            
            # Verify result
            assert result == "0xabcdef"
            mock_erc20.functions.approve.assert_called_once()
            mock_contract.functions.processPayment.assert_called_once_with(
                token_address, amount, service_type, recipient
            )
            mock_web3_instance.eth.send_raw_transaction.assert_called()

class TestTokenRegistry:
    """Tests for the TokenRegistry class."""
    
    def test_initialization(self):
        """Test registry initialization."""
        # Initialize with default network
        registry = TokenRegistry()
        assert registry.network == "base-sepolia"
        assert registry.tokens is not None
        
        # Initialize with specific network
        registry = TokenRegistry(network="base-mainnet")
        assert registry.network == "base-mainnet"
    
    def test_get_token_address(self):
        """Test getting token address."""
        registry = TokenRegistry()
        
        # Test valid token
        address = registry.get_token_address("USDC")
        assert address is not None
        assert isinstance(address, str)
        
        # Test case insensitivity
        address_lower = registry.get_token_address("usdc")
        assert address_lower == address
        
        # Test invalid token
        with pytest.raises(ValueError):
            registry.get_token_address("INVALID_TOKEN")
    
    def test_get_supported_tokens(self):
        """Test getting list of supported tokens."""
        registry = TokenRegistry()
        tokens = registry.get_supported_tokens()
        
        assert tokens is not None
        assert isinstance(tokens, list)
        assert len(tokens) > 0
        assert "USDC" in tokens
        assert "ETH" in tokens
    
    def test_is_token_supported(self):
        """Test checking if a token is supported."""
        registry = TokenRegistry()
        
        assert registry.is_token_supported("USDC") is True
        assert registry.is_token_supported("usdc") is True
        assert registry.is_token_supported("INVALID_TOKEN") is False

class TestServiceProviderRegistry:
    """Tests for the ServiceProviderRegistry class."""
    
    def test_initialization(self):
        """Test registry initialization."""
        registry = ServiceProviderRegistry()
        assert registry.providers is not None
        assert isinstance(registry.providers, dict)
    
    def test_get_provider_address(self):
        """Test getting provider address."""
        registry = ServiceProviderRegistry()
        
        # Test valid service type
        address = registry.get_provider_address("FLIGHTS")
        assert address is not None
        assert isinstance(address, str)
        
        # Test case insensitivity
        address_lower = registry.get_provider_address("flights")
        assert address_lower == address
        
        # Test invalid service type
        with pytest.raises(ValueError):
            registry.get_provider_address("INVALID_SERVICE")
    
    def test_get_supported_services(self):
        """Test getting list of supported services."""
        registry = ServiceProviderRegistry()
        services = registry.get_supported_services()
        
        assert services is not None
        assert isinstance(services, list)
        assert len(services) > 0
        assert "FLIGHTS" in services
        assert "HOTELS" in services
    
    def test_is_service_supported(self):
        """Test checking if a service is supported."""
        registry = ServiceProviderRegistry()
        
        assert registry.is_service_supported("FLIGHTS") is True
        assert registry.is_service_supported("flights") is True
        assert registry.is_service_supported("INVALID_SERVICE") is False
