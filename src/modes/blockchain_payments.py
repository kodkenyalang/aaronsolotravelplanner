"""Blockchain payments mode for UnoTravel."""

import time
from typing import Dict, Any, Optional, List
import json
from decimal import Decimal

from src.game_agents.agent import UnoTravelAgent
from src.utils.state import StateManager
from src.cdp_integration.client import CDPClient
from src.cdp_integration.wallet import WalletManager
from src.cdp_integration.payment import PaymentProcessor
from src.blockchain.contract_client import ContractClient
from src.blockchain.token_registry import TokenRegistry

class BlockchainPaymentsMode:
    """Mode for processing payments with blockchain integration."""
    
    def __init__(self):
        """Initialize the blockchain payments mode."""
        self.agent = UnoTravelAgent()
        self.state_manager = StateManager()
        self.cdp_client = CDPClient()
        self.wallet_manager = WalletManager(self.cdp_client)
        self.payment_processor = PaymentProcessor(self.cdp_client)
        
        # Initialize blockchain components
        self.contract_client = ContractClient()
        self.token_registry = TokenRegistry()
        
        print("UnoTravel Blockchain Payments Mode Initialized")
        
    def run(self):
        """Run the blockchain payments mode."""
        print("Welcome to UnoTravel - Blockchain Payments")
        print("------------------------------------------")
        
        # Load user profile
        user_id = self._get_or_create_user()
        user_profile = self.cdp_client.get_user_profile(user_id)
        
        # Main interaction loop
        while True:
            print("\nWhat would you like to do?")
            print("1. View available payment tokens")
            print("2. Make a payment for travel services")
            print("3. View payment history")
            print("4. View loyalty points")
            print("5. Redeem loyalty points")
            print("6. View wallet balances")
            print("7. Exit")
            
            choice = input("Enter your choice (1-7): ")
            
            if choice == "1":
                self._view_payment_tokens()
            elif choice == "2":
                self._make_payment(user_id)
            elif choice == "3":
                self._view_payment_history()
            elif choice == "4":
                self._view_loyalty_points()
            elif choice == "5":
                self._redeem_loyalty_points()
            elif choice == "6":
                self._view_wallet_balances()
            elif choice == "7":
                print("Thank you for using UnoTravel Blockchain Payments!")
                break
            else:
                print("Invalid choice. Please try again.")
    
    def _get_or_create_user(self) -> str:
        """Get or create a user ID.
        
        Returns:
            User ID
        """
        # Check for existing user ID in state
        user_id = self.state_manager.get("user_id")
        
        if not user_id:
            print("Let's create a new UnoTravel profile...")
            name = input("Enter your name: ")
            email = input("Enter your email: ")
            
            # Create user in CDP
            user_id = self.cdp_client.create_user({
                "name": name,
                "email": email,
                "wallet_address": self.contract_client.address
            })
            
            # Save user ID to state
            self.state_manager.set("user_id", user_id)
            
            print(f"Welcome to UnoTravel, {name}!")
        else:
            user_profile = self.cdp_client.get_user_profile(user_id)
            print(f"Welcome back, {user_profile['name']}!")
        
        return user_id
    
    def _view_payment_tokens(self):
        """View available payment tokens."""
        print("\nAvailable Payment Tokens:")
        print("-------------------------")
        
        tokens = self.token_registry.get_supported_tokens()
        
        for i, token in enumerate(tokens, 1):
            token_info = self.contract_client.get_token_info(token["address"])
            
            # Check if token is supported by the contract
            is_supported = self.contract_client.is_supported_token(token["address"])
            status = "✓ Supported" if is_supported else "✗ Not supported"
            
            print(f"{i}. {token_info['name']} ({token_info['symbol']})")
            print(f"   Address: {token['address']}")
            print(f"   Status: {status}")
            print(f"   Decimals: {token_info['decimals']}")
            print()
    
    def _make_payment(self, user_id: str):
        """Make a payment for travel services.
        
        Args:
            user_id: User ID
        """
        print("\nMake a Payment for UnoTravel Services")
        print("------------------------------------")
        
        # Get available tokens
        tokens = self.token_registry.get_supported_tokens()
        
        # Display token options
        print("Available payment tokens:")
        for i, token in enumerate(tokens, 1):
            token_info = self.contract_client.get_token_info(token["address"])
            balance = self.contract_client.get_token_balance(token["address"])
            print(f"{i}. {token_info['symbol']} - Balance: {balance}")
        
        # Get token selection
        token_index = int(input("\nSelect token to pay with (number): ")) - 1
        if token_index < 0 or token_index >= len(tokens):
            print("Invalid token selection.")
            return
        
        selected_token = tokens[token_index]
        token_info = self.contract_client.get_token_info(selected_token["address"])
        
        # Get service type
        print("\nService types:")
        print("1. Flight")
        print("2. Hotel")
        print("3. Experience")
        
        service_type_index = int(input("Select service type (number): "))
        if service_type_index == 1:
            service_type = "flight"
        elif service_type_index == 2:
            service_type = "hotel"
        elif service_type_index == 3:
            service_type = "experience"
        else:
            print("Invalid service type.")
            return
        
        # Get amount
        amount_str = input(f"\nEnter amount to pay in {token_info['symbol']}: ")
        try:
            amount = Decimal(amount_str)
        except:
            print("Invalid amount.")
            return
        
        # Get recipient
        recipient = input("\nEnter recipient address (leave empty for default UnoTravel provider): ")
        if not recipient:
            # Use default service provider for UnoTravel
            if service_type == "flight":
                recipient = "0x1234567890123456789012345678901234567890"  # Example flight provider
            elif service_type == "hotel":
                recipient = "0x2345678901234567890123456789012345678901"  # Example hotel provider
            else:
                recipient = "0x3456789012345678901234567890123456789012"  # Example experience provider
        
        # Confirm payment
        print("\nPayment Details:")
        print(f"Token: {token_info['symbol']} ({selected_token['address']})")
        print(f"Amount: {amount}")
        print(f"Service Type: {service_type}")
        print(f"Recipient: {recipient}")
        
        confirm = input("\nConfirm payment? (y/n): ")
        if confirm.lower() != "y":
            print("Payment cancelled.")
            return
        
        # Process payment
        try:
            payment_result = self.contract_client.process_payment(
                selected_token["address"],
                amount,
                service_type,
                recipient
            )
            
            # Record payment in CDP
            self.payment_processor.record_payment(
                user_id,
                {
                    "payment_id": payment_result["payment_id"],
                    "token": token_info["symbol"],
                    "amount": str(amount),
                    "service_type": service_type,
                    "recipient": recipient,
                    "transaction_hash": payment_result["receipt"]["transactionHash"].hex()
                }
            )
            
            print("\nPayment successful!")
            print(f"Payment ID: {payment_result['payment_id']}")
            print(f"Transaction Hash: {payment_result['receipt']['transactionHash'].hex()}")
            
        except Exception as e:
            print(f"\nPayment failed: {str(e)}")
    
    def _view_payment_history(self):
        """View payment history."""
        print("\nPayment History")
        print("--------------")
        
        payments = self.contract_client.get_user_payments()
        
        if not payments:
            print("No payments found.")
            return
        
        for i, payment in enumerate(payments, 1):
            print(f"{i}. Payment ID: {payment['payment_id']}")
            print(f"   Amount: {payment['amount']} {payment['token_symbol']}")
            print(f"   Service Type: {payment['service_type']}")
            print(f"   Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(payment['timestamp']))}")
            print(f"   Status: {'Refunded' if payment['refunded'] else 'Completed'}")
            print()
    
    def _view_loyalty_points(self):
        """View loyalty points."""
        print("\nUnoTravel Loyalty Points")
        print("----------------------")
        
        points = self.contract_client.get_loyalty_points()
        ult_balance = self.contract_client.get_token_balance(self.contract_client.loyalty_token_address)
        
        print(f"Current Points: {points}")
        print(f"ULT Token Balance: {ult_balance}")
        
        # Get points conversion rate
        points_per_token = 100  # Example: 100 points = 1 ULT token
        
        print(f"\nConversion Rate: {points_per_token} points = 1 ULT token")
        print(f"Redeemable Points: {points}")
        print(f"Equivalent ULT Tokens: {points / points_per_token}")
    
    def _redeem_loyalty_points(self):
        """Redeem loyalty points for tokens."""
        print("\nRedeem Loyalty Points")
        print("-------------------")
        
        points = self.contract_client.get_loyalty_points()
        
        if points == 0:
            print("You don't have any loyalty points to redeem.")
            return
        
        # Get points to redeem
        points_to_redeem_str = input(f"You have {points} points. How many points would you like to redeem? ")
        try:
            points_to_redeem = int(points_to_redeem_str)
            if points_to_redeem <= 0 or points_to_redeem > points:
                print("Invalid points amount.")
                return
        except:
            print("Invalid points amount.")
            return
        
        # Get available tokens
        tokens = self.token_registry.get_supported_tokens()
        
        # Display token options
        print("\nAvailable tokens to receive:")
        for i, token in enumerate(tokens, 1):
            token_info = self.contract_client.get_token_info(token["address"])
            print(f"{i}. {token_info['symbol']}")
        
        # Default to ULT token
        print(f"{len(tokens) + 1}. ULT (UnoTravel Loyalty Token)")
        
        # Get token selection
        token_index = int(input("\nSelect token to receive (number): ")) - 1
        if token_index < 0 or token_index > len(tokens):
            print("Invalid token selection.")
            return
        
        if token_index == len(tokens):
            # ULT token
            selected_token_address = self.contract_client.loyalty_token_address
        else:
            selected_token_address = tokens[token_index]["address"]
        
        token_info = self.contract_client.get_token_info(selected_token_address)
        
        # Confirm redemption
        print("\nRedemption Details:")
        print(f"Points to Redeem: {points_to_redeem}")
        print(f"Token to Receive: {token_info['symbol']}")
        
        confirm = input("\nConfirm redemption? (y/n): ")
        if confirm.lower() != "y":
            print("Redemption cancelled.")
            return
        
        # Process redemption
        try:
            redemption_result = self.contract_client.redeem_loyalty_points(
                points_to_redeem,
                selected_token_address
            )
            
            print("\nRedemption successful!")
            print(f"Transaction Hash: {redemption_result['transactionHash'].hex()}")
            
        except Exception as e:
            print(f"\nRedemption failed: {str(e)}")
    
    def _view_wallet_balances(self):
        """View wallet balances."""
        print("\nWallet Balances")
        print("--------------")
        
        print(f"Wallet Address: {self.contract_client.address}")
        
        # Get ETH balance
        eth_balance = self.contract_client.get_eth_balance()
        print(f"ETH: {eth_balance}")
        
        # Get ULT balance
        ult_balance = self.contract_client.get_token_balance(self.contract_client.loyalty_token_address)
        print(f"ULT: {ult_balance}")
        
        # Get other token balances
        tokens = self.token_registry.get_supported_tokens()
        
        for token in tokens:
            balance = self.contract_client.get_token_balance(token["address"])
            token_info = self.contract_client.get_token_info(token["address"])
            print(f"{token_info['symbol']}: {balance}")
