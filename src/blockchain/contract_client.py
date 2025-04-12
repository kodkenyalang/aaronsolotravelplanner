"""Client for interacting with the Travel Manager smart contracts."""

import json
import os
from typing import Dict, List, Optional, Any

from web3 import Web3
from web3.contract import Contract

class ContractClient:
    """Client for interacting with the deployed smart contracts."""
    
    def __init__(self):
        """Initialize the contract client."""
        # Load configuration
        self.provider_url = os.getenv("WEB3_PROVIDER_URL", "https://sepolia.base.org")
        self.private_key = os.getenv("PRIVATE_KEY", "")
        self.payment_processor_address = os.getenv("PAYMENT_PROCESSOR_ADDRESS", "")
        self.loyalty_token_address = os.getenv("LOYALTY_TOKEN_ADDRESS", "")
        
        # Connect to the provider
        self.web3 = Web3(Web3.HTTPProvider(self.provider_url))
        
        # Check connection
        if not self.web3.is_connected():
            raise ConnectionError(f"Failed to connect to provider at {self.provider_url}")
        
        # Load contract ABIs
        self.payment_processor_abi = self._load_contract_abi("TravelPaymentProcessor.json")
        self.loyalty_token_abi = self._load_contract_abi("TravelLoyaltyToken.json")
        
        # Initialize contract instances
        self.payment_processor = self.web3.eth.contract(
            address=self.web3.to_checksum_address(self.payment_processor_address),
            abi=self.payment_processor_abi
        )
        
        self.loyalty_token = self.web3.eth.contract(
            address=self.web3.to_checksum_address(self.loyalty_token_address),
            abi=self.loyalty_token_abi
        )
        
        # Setup account
        self.account = self.web3.eth.account.from_key(self.private_key)
    
    def _load_contract_abi(self, filename: str) -> List[Dict[str, Any]]:
        """Load a contract ABI from a JSON file.
        
        Args:
            filename: Name of the JSON file containing the ABI
            
        Returns:
            List representing the contract ABI
        """
        contract_dir = os.path.join(os.path.dirname(__file__), "contracts", "artifacts")
        file_path = os.path.join(contract_dir, filename)
        
        try:
            with open(file_path, "r") as file:
                contract_json = json.load(file)
                return contract_json["abi"]
        except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
            raise RuntimeError(f"Failed to load contract ABI from {filename}: {str(e)}")
    
    def process_payment(
        self, token_address: str, amount: int, service_type: str, recipient: str
    ) -> str:
        """Process a payment through the TravelPaymentProcessor contract.
        
        Args:
            token_address: Address of the ERC20 token to use for payment
            amount: Amount to pay (in wei)
            service_type: Type of service being paid for ("flight", "hotel", "experience")
            recipient: Address of the service provider receiving the payment
            
        Returns:
            Transaction hash
        """
        # Get the ERC20 token contract
        token_contract = self.web3.eth.contract(
            address=self.web3.to_checksum_address(token_address),
            abi=self._get_erc20_abi()
        )
        
        # Approve the payment processor to spend tokens
        approve_tx = token_contract.functions.approve(
            self.payment_processor_address, amount
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.web3.eth.get_transaction_count(self.account.address),
            "gasPrice": self.web3.eth.gas_price
        })
        
        # Sign and send the approval transaction
        signed_approve_tx = self.web3.eth.account.sign_transaction(approve_tx, self.private_key)
        approve_tx_hash = self.web3.eth.send_raw_transaction(signed_approve_tx.rawTransaction)
        self.web3.eth.wait_for_transaction_receipt(approve_tx_hash)
        
        # Now process the payment
        payment_tx = self.payment_processor.functions.processPayment(
            token_address, amount, service_type, recipient
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.web3.eth.get_transaction_count(self.account.address),
            "gasPrice": self.web3.eth.gas_price
        })
        
        # Sign and send the payment transaction
        signed_payment_tx = self.web3.eth.account.sign_transaction(payment_tx, self.private_key)
        payment_tx_hash = self.web3.eth.send_raw_transaction(signed_payment_tx.rawTransaction)
        
        # Return the transaction hash
        return self.web3.to_hex(payment_tx_hash)
    
    def get_user_payments(self, user_address: str) -> List[str]:
        """Get all payment IDs for a user.
        
        Args:
            user_address: Address of the user
            
        Returns:
            List of payment IDs
        """
        payment_ids = self.payment_processor.functions.getUserPayments(
            self.web3.to_checksum_address(user_address)
        ).call()
        
        return payment_ids
    
    def get_payment_details(self, payment_id: str) -> Dict[str, Any]:
        """Get details for a specific payment.
        
        Args:
            payment_id: ID of the payment
            
        Returns:
            Dictionary containing payment details
        """
        result = self.payment_processor.functions.getPaymentDetails(payment_id).call()
        
        return {
            "user": result[0],
            "token": result[1],
            "amount": result[2],
            "service_type": result[3],
            "timestamp": result[4],
            "refunded": result[5]
        }
    
    def get_loyalty_points(self, user_address: str) -> int:
        """Get the loyalty points balance for a user.
        
        Args:
            user_address: Address of the user
            
        Returns:
            Loyalty points balance
        """
        points = self.payment_processor.functions.loyaltyPoints(
            self.web3.to_checksum_address(user_address)
        ).call()
        
        return points
    
    def redeem_loyalty_points(self, amount: int, token_address: str) -> str:
        """Redeem loyalty points for tokens.
        
        Args:
            amount: Amount of points to redeem
            token_address: Address of the token to receive
            
        Returns:
            Transaction hash
        """
        redeem_tx = self.payment_processor.functions.redeemLoyaltyPoints(
            amount, self.web3.to_checksum_address(token_address)
        ).build_transaction({
            "from": self.account.address,
            "nonce": self.web3.eth.get_transaction_count(self.account.address),
            "gasPrice": self.web3.eth.gas_price
        })
        
        # Sign and send the redemption transaction
        signed_redeem_tx = self.web3.eth.account.sign_transaction(redeem_tx, self.private_key)
        redeem_tx_hash = self.web3.eth.send_raw_transaction(signed_redeem_tx.rawTransaction)
        
        # Return the transaction hash
        return self.web3.to_hex(redeem_tx_hash)
    
    def get_loyalty_token_balance(self, user_address: str) -> int:
        """Get the loyalty token balance for a user.
        
        Args:
            user_address: Address of the user
            
        Returns:
            Token balance
        """
        balance = self.loyalty_token.functions.balanceOf(
            self.web3.to_checksum_address(user_address)
        ).call()
        
        return balance
    
    def _get_erc20_abi(self) -> List[Dict[str, Any]]:
        """Get a basic ERC20 ABI for token interactions.
        
        Returns:
            ERC20 ABI
        """
        return [
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": False,
                "inputs": [
                    {"name": "_spender", "type": "address"},
                    {"name": "_value", "type": "uint256"}
                ],
                "name": "approve",
                "outputs": [{"name": "", "type": "bool"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "totalSupply",
                "outputs": [{"name": "", "type": "uint256"}],
                "type": "function"
            },
            {
                "constant": False,
                "inputs": [
                    {"name": "_to", "type": "address"},
                    {"name": "_value", "type": "uint256"}
                ],
                "name": "transfer",
                "outputs": [{"name": "", "type": "bool"}],
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [
                    {"name": "_owner", "type": "address"},
                    {"name": "_spender", "type": "address"}
                ],
                "name": "allowance",
                "outputs": [{"name": "", "type": "uint256"}],
                "type": "function"
            }
        ]
