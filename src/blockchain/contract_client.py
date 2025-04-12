"""Client for interacting with the UnoTravel smart contracts."""

import json
import os
from typing import Dict, List, Optional, Any
from decimal import Decimal

from web3 import Web3
from web3.contract import Contract
from web3.exceptions import ContractLogicError

class ContractClient:
    """Client for interacting with the deployed UnoTravel smart contracts."""
    
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
        self.payment_processor_abi = self._load_contract_abi("UnoTravelPaymentProcessor.json")
        self.loyalty_token_abi = self._load_contract_abi("UnoLoyaltyToken.json")
        self.erc20_abi = self._load_contract_abi("ERC20.json")
        
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
        self.address = self.account.address
        
        print(f"UnoTravel Blockchain Client initialized - connected to {self.provider_url}")
        print(f"Account: {self.address}")

    def _load_contract_abi(self, filename: str) -> List[Dict[str, Any]]:
        """Load a contract ABI from the artifacts directory.
        
        Args:
            filename: Name of the JSON file containing the ABI
            
        Returns:
            The contract ABI
        """
        try:
            # Try to load from artifacts directory
            artifacts_dir = os.path.join(os.path.dirname(__file__), "..", "..", "artifacts", "contracts")
            filepath = os.path.join(artifacts_dir, filename)
            
            if not os.path.exists(filepath):
                # Try alternate location
                artifacts_dir = os.path.join(os.path.dirname(__file__), "..", "..", "artifacts")
                filepath = os.path.join(artifacts_dir, filename)
                
            if not os.path.exists(filepath):
                # One more try with contract name
                contract_name = filename.split(".")[0]
                filepath = os.path.join(
                    artifacts_dir, 
                    f"{contract_name}.sol", 
                    f"{contract_name}.json"
                )
            
            with open(filepath, "r") as f:
                data = json.load(f)
                if "abi" in data:
                    return data["abi"]
                return data
        except Exception as e:
            print(f"Error loading ABI from {filename}: {e}")
            # Return a minimal ABI for ERC20 if loading fails
            if filename == "ERC20.json":
                return [
                    {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
                    {"constant": False, "inputs": [{"name": "_to", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "transfer", "outputs": [{"name": "success", "type": "bool"}], "type": "function"},
                    {"constant": False, "inputs": [{"name": "_spender", "type": "address"}, {"name": "_value", "type": "uint256"}], "name": "approve", "outputs": [{"name": "success", "type": "bool"}], "type": "function"},
                    {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"},
                    {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"},
                    {"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "type": "function"}
                ]
            return []

    def _get_erc20_contract(self, token_address: str) -> Contract:
        """Get an ERC20 token contract instance.
        
        Args:
            token_address: Address of the ERC20 token
            
        Returns:
            The ERC20 contract instance
        """
        return self.web3.eth.contract(
            address=self.web3.to_checksum_address(token_address),
            abi=self.erc20_abi
        )

    def _get_gas_price(self) -> int:
        """Get the current gas price with a buffer.
        
        Returns:
            Gas price in wei
        """
        gas_price = self.web3.eth.gas_price
        return int(gas_price * 1.1)  # 10% buffer

    def _build_and_send_tx(self, function_call, value: int = 0) -> Dict[str, Any]:
        """Build and send a transaction.
        
        Args:
            function_call: The contract function call
            value: The value in wei to send with the transaction
            
        Returns:
            Transaction receipt
        """
        # Get nonce
        nonce = self.web3.eth.get_transaction_count(self.account.address)
        
        # Build transaction
        tx = function_call.build_transaction({
            'from': self.account.address,
            'nonce': nonce,
            'gas': 2000000,  # Gas limit
            'gasPrice': self._get_gas_price(),
            'value': value
        })
        
        # Sign transaction
        signed_tx = self.web3.eth.account.sign_transaction(tx, private_key=self.private_key)
        
        # Send transaction
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        # Wait for transaction receipt
        print(f"Transaction sent: {tx_hash.hex()}")
        print("Waiting for transaction to be mined...")
        
        receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt['status'] == 1:
            print(f"Transaction successful: {receipt['transactionHash'].hex()}")
        else:
            print(f"Transaction failed: {receipt['transactionHash'].hex()}")
        
        return receipt

    def get_token_balance(self, token_address: str, address: Optional[str] = None) -> Decimal:
        """Get the balance of a token for an address.
        
        Args:
            token_address: Address of the ERC20 token
            address: Address to check balance for (defaults to client address)
            
        Returns:
            Token balance as a Decimal
        """
        if address is None:
            address = self.address
            
        address = self.web3.to_checksum_address(address)
        token_contract = self._get_erc20_contract(token_address)
        
        raw_balance = token_contract.functions.balanceOf(address).call()
        decimals = token_contract.functions.decimals().call()
        
        # Convert to human-readable format
        balance = Decimal(raw_balance) / Decimal(10 ** decimals)
        
        return balance

    def get_token_info(self, token_address: str) -> Dict[str, Any]:
        """Get information about a token.
        
        Args:
            token_address: Address of the ERC20 token
            
        Returns:
            Token information
        """
        token_contract = self._get_erc20_contract(token_address)
        
        try:
            symbol = token_contract.functions.symbol().call()
            name = token_contract.functions.name().call()
            decimals = token_contract.functions.decimals().call()
            
            return {
                "symbol": symbol,
                "name": name,
                "decimals": decimals,
                "address": token_address
            }
        except Exception as e:
            print(f"Error getting token info: {e}")
            return {
                "symbol": "UNKNOWN",
                "name": "Unknown Token",
                "decimals": 18,
                "address": token_address
            }

    def approve_token_spending(self, token_address: str, spender_address: str, amount: Decimal) -> Dict[str, Any]:
        """Approve a spender to spend tokens.
        
        Args:
            token_address: Address of the ERC20 token
            spender_address: Address of the spender
            amount: Amount to approve as a Decimal
            
        Returns:
            Transaction receipt
        """
        token_contract = self._get_erc20_contract(token_address)
        decimals = token_contract.functions.decimals().call()
        
        # Convert amount to token units
        amount_in_units = int(amount * Decimal(10 ** decimals))
        
        # Build approve function call
        approve_function = token_contract.functions.approve(
            self.web3.to_checksum_address(spender_address),
            amount_in_units
        )
        
        return self._build_and_send_tx(approve_function)

    def process_payment(self, token_address: str, amount: Decimal, service_type: str, recipient: str) -> Dict[str, Any]:
        """Process a payment for UnoTravel services.
        
        Args:
            token_address: Address of the ERC20 token to pay with
            amount: Amount to pay as a Decimal
            service_type: Type of service (flight, hotel, experience)
            recipient: Address of the service provider
            
        Returns:
            Transaction receipt and payment details
        """
        token_contract = self._get_erc20_contract(token_address)
        decimals = token_contract.functions.decimals().call()
        
        # Convert amount to token units
        amount_in_units = int(amount * Decimal(10 ** decimals))
        
        # First approve the payment processor to spend tokens
        self.approve_token_spending(
            token_address,
            self.payment_processor_address,
            amount
        )
        
        # Build process payment function call
        process_payment_function = self.payment_processor.functions.processPayment(
            self.web3.to_checksum_address(token_address),
            amount_in_units,
            service_type,
            self.web3.to_checksum_address(recipient)
        )
        
        # Send transaction
        receipt = self._build_and_send_tx(process_payment_function)
        
        # Extract payment ID from event logs
        payment_id = None
        for log in receipt['logs']:
            if log['address'].lower() == self.payment_processor_address.lower():
                try:
                    # Try to decode the log as a PaymentProcessed event
                    event = self.payment_processor.events.PaymentProcessed().process_log(log)
                    payment_id = event['args']['paymentId']
                    break
                except:
                    continue
        
        return {
            "receipt": receipt,
            "payment_id": payment_id,
            "token_address": token_address,
            "amount": amount,
            "service_type": service_type,
            "recipient": recipient
        }

    def get_user_payments(self, address: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all payments for a user.
        
        Args:
            address: Address to get payments for (defaults to client address)
            
        Returns:
            List of payment details
        """
        if address is None:
            address = self.address
            
        address = self.web3.to_checksum_address(address)
        
        # Get payment IDs
        payment_ids = self.payment_processor.functions.getUserPayments(address).call()
        
        payments = []
        for payment_id in payment_ids:
            payment_details = self.get_payment_details(payment_id)
            payments.append(payment_details)
        
        return payments

    def get_payment_details(self, payment_id: str) -> Dict[str, Any]:
        """Get details for a payment.
        
        Args:
            payment_id: Payment ID
            
        Returns:
            Payment details
        """
        (user, token, amount, service_type, timestamp, refunded) = (
            self.payment_processor.functions.getPaymentDetails(payment_id).call()
        )
        
        # Get token info
        token_info = self.get_token_info(token)
        
        # Convert amount to human-readable format
        amount_decimal = Decimal(amount) / Decimal(10 ** token_info['decimals'])
        
        return {
            "payment_id": payment_id,
            "user": user,
            "token": token,
            "token_symbol": token_info['symbol'],
            "amount": amount_decimal,
            "service_type": service_type,
            "timestamp": timestamp,
            "refunded": refunded
        }

    def get_loyalty_points(self, address: Optional[str] = None) -> int:
        """Get loyalty points for a user.
        
        Args:
            address: Address to get loyalty points for (defaults to client address)
            
        Returns:
            Loyalty points
        """
        if address is None:
            address = self.address
            
        address = self.web3.to_checksum_address(address)
        
        return self.payment_processor.functions.loyaltyPoints(address).call()

    def redeem_loyalty_points(self, points: int, token_address: str) -> Dict[str, Any]:
        """Redeem loyalty points for tokens.
        
        Args:
            points: Points to redeem
            token_address: Address of the token to receive
            
        Returns:
            Transaction receipt
        """
        redeem_function = self.payment_processor.functions.redeemLoyaltyPoints(
            points,
            self.web3.to_checksum_address(token_address)
        )
        
        return self._build_and_send_tx(redeem_function)

    def add_supported_token(self, token_address: str) -> Dict[str, Any]:
        """Add a supported payment token (admin only).
        
        Args:
            token_address: Address of the ERC20 token
            
        Returns:
            Transaction receipt
        """
        add_token_function = self.payment_processor.functions.addSupportedToken(
            self.web3.to_checksum_address(token_address)
        )
        
        return self._build_and_send_tx(add_token_function)

    def remove_supported_token(self, token_address: str) -> Dict[str, Any]:
        """Remove a supported payment token (admin only).
        
        Args:
            token_address: Address of the ERC20 token
            
        Returns:
            Transaction receipt
        """
        remove_token_function = self.payment_processor.functions.removeSupportedToken(
            self.web3.to_checksum_address(token_address)
        )
        
        return self._build_and_send_tx(remove_token_function)

    def add_service_provider(self, provider_address: str) -> Dict[str, Any]:
        """Add a service provider (admin only).
        
        Args:
            provider_address: Address of the service provider
            
        Returns:
            Transaction receipt
        """
        add_provider_function = self.payment_processor.functions.addServiceProvider(
            self.web3.to_checksum_address(provider_address)
        )
        
        return self._build_and_send_tx(add_provider_function)

    def remove_service_provider(self, provider_address: str) -> Dict[str, Any]:
        """Remove a service provider (admin only).
        
        Args:
            provider_address: Address of the service provider
            
        Returns:
            Transaction receipt
        """
        remove_provider_function = self.payment_processor.functions.removeServiceProvider(
            self.web3.to_checksum_address(provider_address)
        )
        
        return self._build_and_send_tx(remove_provider_function)

    def mint_loyalty_tokens(self, to_address: str, amount: Decimal) -> Dict[str, Any]:
        """Mint loyalty tokens (minter only).
        
        Args:
            to_address: Address to mint tokens to
            amount: Amount of tokens to mint
            
        Returns:
            Transaction receipt
        """
        # Convert amount to token units (ULT has 18 decimals)
        amount_in_units = int(amount * Decimal(10 ** 18))
        
        mint_function = self.loyalty_token.functions.mint(
            self.web3.to_checksum_address(to_address),
            amount_in_units
        )
        
        return self._build_and_send_tx(mint_function)

    def add_minter(self, minter_address: str) -> Dict[str, Any]:
        """Add a minter for loyalty tokens (admin only).
        
        Args:
            minter_address: Address of the minter
            
        Returns:
            Transaction receipt
        """
        add_minter_function = self.loyalty_token.functions.addMinter(
            self.web3.to_checksum_address(minter_address)
        )
        
        return self._build_and_send_tx(add_minter_function)

    def is_supported_token(self, token_address: str) -> bool:
        """Check if a token is supported for payments.
        
        Args:
            token_address: Address of the ERC20 token
            
        Returns:
            True if supported, False otherwise
        """
        return self.payment_processor.functions.supportedTokens(
            self.web3.to_checksum_address(token_address)
        ).call()

    def is_service_provider(self, provider_address: str) -> bool:
        """Check if an address is a service provider.
        
        Args:
            provider_address: Address to check
            
        Returns:
            True if a service provider, False otherwise
        """
        return self.payment_processor.functions.serviceProviders(
            self.web3.to_checksum_address(provider_address)
        ).call()

    def get_owner(self) -> str:
        """Get the owner of the payment processor contract.
        
        Returns:
            Owner address
        """
        return self.payment_processor.functions.owner().call()

    def refund_payment(self, payment_id: str) -> Dict[str, Any]:
        """Refund a payment (service provider only).
        
        Args:
            payment_id: Payment ID to refund
            
        Returns:
            Transaction receipt
        """
        refund_function = self.payment_processor.functions.refundPayment(payment_id)
        return self._build_and_send_tx(refund_function)

    def transfer_tokens(self, token_address: str, to_address: str, amount: Decimal) -> Dict[str, Any]:
        """Transfer tokens to another address.
        
        Args:
            token_address: Address of the ERC20 token
            to_address: Address to transfer to
            amount: Amount to transfer as a Decimal
            
        Returns:
            Transaction receipt
        """
        token_contract = self._get_erc20_contract(token_address)
        decimals = token_contract.functions.decimals().call()
        
        # Convert amount to token units
        amount_in_units = int(amount * Decimal(10 ** decimals))
        
        # Build transfer function call
        transfer_function = token_contract.functions.transfer(
            self.web3.to_checksum_address(to_address),
            amount_in_units
        )
        
        return self._build_and_send_tx(transfer_function)

    def get_eth_balance(self, address: Optional[str] = None) -> Decimal:
        """Get the ETH balance for an address.
        
        Args:
            address: Address to check balance for (defaults to client address)
            
        Returns:
            ETH balance as a Decimal
        """
        if address is None:
            address = self.address
            
        address = self.web3.to_checksum_address(address)
        
        raw_balance = self.web3.eth.get_balance(address)
        balance = Decimal(raw_balance) / Decimal(10 ** 18)  # ETH has 18 decimals
        
        return balance
