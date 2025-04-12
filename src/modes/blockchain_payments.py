"""Blockchain payments mode for travel manager."""

import time
from typing import Dict, Any

from src.game_agents.agent import TravelManagerAgent
from src.utils.state import StateManager
from src.cdp_integration.client import CDPClient
from src.cdp_integration.wallet import WalletManager
from src.cdp_integration.payment import PaymentProcessor
from src.blockchain.contract_client import ContractClient
from src.blockchain.token_registry import TokenRegistry

class BlockchainPaymentsMode:
    """Mode for managing travel with blockchain payments."""
    
    def __init__(self):
        """Initialize the blockchain payments mode."""
        self.state_manager = StateManager()
        self.agent = TravelManagerAgent()
        self.cdp_client = CDPClient()
        self.wallet_manager = WalletManager(self.cdp_client)
        self.payment_processor = PaymentProcessor(self.cdp_client)
        self.contract_client = ContractClient()
        self.token_registry = TokenRegistry()
        
        # Connect to the blockchain
        self.cdp_client.connect_to_network("base-sepolia")
        
        # Update state with blockchain settings
        self.state_manager.update_state({
            "blockchain_enabled": True,
            "interaction_mode": "blockchain_payments"
        })
    
    def run(self):
        """Run the blockchain payments mode."""
        print("\n===== Travel Manager with Blockchain Payments =====\n")
        print("This mode allows you to manage your travel plans with blockchain payments.")
        print("You can use your crypto tokens to pay for travel services.\n")
        
        # Check wallet balance
        self._check_wallet_balance()
        
        while True:
            print("\nWhat would you like to do?")
            print("1. Plan a trip")
            print("2. View wallet balance")
            print("3. Make a payment")
            print("4. View transaction history")
            print("5. View loyalty points")
            print("6. Redeem loyalty points")
            print("7. Swap tokens")
            print("8. Exit")
            
            choice = input("\nEnter your choice (1-8): ")
            
            if choice == "1":
                self._plan_trip()
            elif choice == "2":
                self._check_wallet_balance()
            elif choice == "3":
                self._make_payment()
            elif choice == "4":
                self._view_transaction_history()
            elif choice == "5":
                self._view_loyalty_points()
            elif choice == "6":
                self._redeem_loyalty_points()
            elif choice == "7":
                self._swap_tokens()
            elif choice == "8":
                print("\nThank you for using Travel Manager with Blockchain Payments!")
                break
            else:
                print("\nInvalid choice. Please try again.")
    
    def _check_wallet_balance(self):
        """Check and display the wallet balance."""
        print("\nChecking wallet balance...")
        try:
            balance = self.wallet_manager.get_wallet_balance()
            self.state_manager.update_state({"wallet_tokens": balance})
            
            print("\nWallet Balance:")
            for token, amount in balance.items():
                print(f"  {token}: {amount}")
        except Exception as e:
            print(f"\nError checking wallet balance: {str(e)}")
    
    def _plan_trip(self):
        """Plan a trip using the travel agent."""
        print("\nLet's plan your trip!")
        destination = input("Where would you like to go? ")
        
        # Process the query through the agent
        print("\nProcessing your request...")
        result = self.agent.process_query(f"I want to go to {destination}")
        
        print("\nTravel Agent Response:")
        print(result["response"])
        
        # Update the state with the planning info
        if "selected_destination" in result:
            self.state_manager.update_state(result)
    
    def _make_payment(self):
        """Make a payment for a travel service."""
        print("\nMake a Payment")
        
        # Get payment details
        service_type = input("What are you paying for? (flight/hotel/experience): ")
        amount = float(input("Amount to pay: "))
        
        # Show available tokens
        tokens = self.token_registry.get_supported_tokens()
        print("\nAvailable tokens:")
        for i, token in enumerate(tokens):
            print(f"  {i+1}. {token}")
        
        token_index = int(input("\nSelect token (number): ")) - 1
        token = tokens[token_index]
        
        # Confirm the payment
        print(f"\nYou are about to pay {amount} {token} for {service_type}.")
        confirm = input("Confirm payment? (y/n): ")
        
        if confirm.lower() != "y":
            print("Payment cancelled.")
            return
        
        try:
            # Process the payment
            print("\nProcessing payment...")
            tx_hash = self.payment_processor.process_payment(amount, token, service_type)
            
            print(f"\nPayment successful!")
            print(f"Transaction hash: {tx_hash}")
            
            # Update wallet balance
            self._check_wallet_balance()
            
            # Update state
            state = self.state_manager.get_state()
            if "payments" not in state:
                state["payments"] = []
            
            state["payments"].append({
                "service_type": service_type,
                "amount": amount,
                "currency": token,
                "tx_hash": tx_hash,
                "timestamp": int(time.time())
            })
            
            self.state_manager.update_state(state)
        except Exception as e:
            print(f"\nError processing payment: {str(e)}")
    
    def _view_transaction_history(self):
        """View transaction history."""
        print("\nTransaction History")
        
        try:
            history = self.payment_processor.get_transaction_history()
            
            if not history["payments"]:
                print("No transactions found.")
                return
            
            for i, payment in enumerate(history["payments"]):
                amount = payment["amount"] / (10 ** 18)  # Convert from wei
                print(f"\nTransaction {i+1}:")
                print(f"  Service: {payment['service_type']}")
                print(f"  Amount: {amount}")
                print(f"  Token: {payment['token']}")
                print(f"  Timestamp: {time.ctime(payment['timestamp'])}")
                print(f"  Refunded: {'Yes' if payment['refunded'] else 'No'}")
                print(f"  Payment ID: {payment['payment_id']}")
        except Exception as e:
            print(f"\nError retrieving transaction history: {str(e)}")
    
    def _view_loyalty_points(self):
        """View loyalty points balance."""
        print("\nLoyalty Points")
        
        try:
            points = self.payment_processor.get_loyalty_points()
            print(f"You have {points} loyalty points.")
            
            # Also show loyalty token balance if available
            try:
                token_balance = self.contract_client.get_loyalty_token_balance(
                    self.contract_client.account.address
                )
                token_balance_eth = token_balance / (10 ** 18)  # Convert from wei
                print(f"You have {token_balance_eth} TLT (Travel Loyalty Tokens).")
            except Exception:
                pass  # Ignore errors with loyalty token
        except Exception as e:
            print(f"\nError retrieving loyalty points: {str(e)}")
    
    def _redeem_loyalty_points(self):
        """Redeem loyalty points for tokens."""
        print("\nRedeem Loyalty Points")
        
        try:
            # Show current points
            points = self.payment_processor.get_loyalty_points()
            print(f"You have {points} loyalty points.")
            
            if points == 0:
                print("You don't have any loyalty points to redeem.")
                return
            
            # Get redemption details
            points_to_redeem = int(input("How many points do you want to redeem? "))
            
            if points_to_redeem > points:
                print("You don't have enough points.")
                return
            
            # Show available tokens
            tokens = self.token_registry.get_supported_tokens()
            print("\nAvailable tokens:")
            for i, token in enumerate(tokens):
                print(f"  {i+1}. {token}")
            
            token_index = int(input("\nSelect token to receive (number): ")) - 1
            token = tokens[token_index]
            
            # Confirm redemption
            estimated_value = (points_to_redeem / 100)  # 1 point = 0.01 tokens
            print(f"\nYou will receive approximately {estimated_value} {token}.")
            confirm = input("Confirm redemption? (y/n): ")
            
            if confirm.lower() != "y":
                print("Redemption cancelled.")
                return
            
            # Process the redemption
            print("\nProcessing redemption...")
            tx_hash = self.payment_processor.redeem_loyalty_points(points_to_redeem, token)
            
            print(f"\nRedemption successful!")
            print(f"Transaction hash: {tx_hash}")
            
            # Update wallet balance
            self._check_wallet_balance()
        except Exception as e:
            print(f"\nError redeeming loyalty points: {str(e)}")
    
    def _swap_tokens(self):
        """Swap one token for another."""
        print("\nSwap Tokens")
        
        # Show available tokens
        tokens = self.token_registry.get_supported_tokens()
        print("\nAvailable tokens:")
        for i, token in enumerate(tokens):
            print(f"  {i+1}. {token}")
        
        from_index = int(input("\nFrom token (number): ")) - 1
        from_token = tokens[from_index]
        
        to_index = int(input("To token (number): ")) - 1
        to_token = tokens[to_index]
        
        amount = input(f"Amount of {from_token} to swap: ")
        
        # Confirm the swap
        print(f"\nYou are about to swap {amount} {from_token} for {to_token}.")
        confirm = input("Confirm swap? (y/n): ")
        
        if confirm.lower() != "y":
            print("Swap cancelled.")
            return
        
        try:
            # Process the swap
            print("\nProcessing swap...")
            result = self.payment_processor.swap_tokens(from_token, to_token, amount)
            
            print(f"\nSwap successful!")
            print(f"You swapped {result['fromAmount']} {result['fromToken']} for {result['toAmount']} {result['toToken']}")
            print(f"Transaction hash: {result['txHash']}")
            
            # Update wallet balance
            self._check_wallet_balance()
        except Exception as e:
            print(f"\nError processing swap: {str(e)}")
