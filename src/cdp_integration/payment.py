"""CDP payment processing module."""

from typing import Dict, Any, Optional

from src.cdp_integration.client import CDPClient
from src.blockchain.contract_client import ContractClient
from src.blockchain.token_registry import TokenRegistry
from src.blockchain.service_provider import ServiceProviderRegistry

class PaymentProcessor:
    """Payment processor for travel services."""
    
    def __init__(self, cdp_client: CDPClient = None):
        """Initialize the payment processor.
        
        Args:
            cdp_client: CDP client instance
        """
        self.cdp_client = cdp_client or CDPClient()
        self.contract_client = ContractClient()
        self.token_registry = TokenRegistry()
        self.service_registry = ServiceProviderRegistry()
    
    def process_payment(self, amount: float, currency: str, service_type: str) -> str:
        """Process a payment for a travel service.
        
        Args:
            amount: Amount to pay
            currency: Currency symbol (e.g., "USDC")
            service_type: Type of service ("flight", "hotel", "experience")
            
        Returns:
            Transaction hash
        """
        # Convert service type to provider key
        provider_key = self._map_service_type_to_provider(service_type)
        
        # Get the service provider address
        provider_address = self.service_registry.get_provider_address(provider_key)
        
        # Get the token address
        token_address = self.token_registry.get_token_address(currency)
        
        # Convert amount to wei (assuming 18 decimals for all tokens)
        amount_wei = int(amount * (10 ** 18))
        
        # Process the payment using the smart contract
        tx_hash = self.contract_client.process_payment(
            token_address, amount_wei, service_type, provider_address
        )
        
        return tx_hash
    
    def swap_tokens(self, from_token: str, to_token: str, amount: str) -> Dict[str, Any]:
        """Swap tokens using CDP.
        
        Args:
            from_token: Source token symbol
            to_token: Destination token symbol
            amount: Amount to swap
            
        Returns:
            Swap result details
        """
        return self.cdp_client.swap_tokens(from_token, to_token, amount)
    
    def get_loyalty_points(self) -> int:
        """Get the user's loyalty points balance.
        
        Returns:
            Loyalty points balance
        """
        user_address = self.contract_client.account.address
        return self.contract_client.get_loyalty_points(user_address)
    
    def redeem_loyalty_points(self, amount: int, token: str) -> str:
        """Redeem loyalty points for tokens.
        
        Args:
            amount: Amount of points to redeem
            token: Token symbol to receive
            
        Returns:
            Transaction hash
        """
        token_address = self.token_registry.get_token_address(token)
        return self.contract_client.redeem_loyalty_points(amount, token_address)
    
    def get_transaction_history(self) -> Dict[str, Any]:
        """Get the user's transaction history.
        
        Returns:
            Dictionary containing transaction history
        """
        user_address = self.contract_client.account.address
        payment_ids = self.contract_client.get_user_payments(user_address)
        
        payments = []
        for payment_id in payment_ids:
            details = self.contract_client.get_payment_details(payment_id)
            payments.append({
                "payment_id": payment_id,
                "token": details["token"],
                "amount": details["amount"],
                "service_type": details["service_type"],
                "timestamp": details["timestamp"],
                "refunded": details["refunded"]
            })
        
        return {"payments": payments}
    
    def _map_service_type_to_provider(self, service_type: str) -> str:
        """Map a service type to a provider key.
        
        Args:
            service_type: Type of service ("flight", "hotel", "experience")
            
        Returns:
            Provider key for the service registry
        """
        mapping = {
            "flight": "FLIGHTS",
            "hotel": "HOTELS",
            "experience": "EXPERIENCES"
        }
        
        return mapping.get(service_type.lower(), "HOTELS")  # Default to HOTELS if not found
