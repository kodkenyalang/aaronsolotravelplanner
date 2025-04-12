"""Travel Manager CDP main entry point."""

import os
import argparse
from dotenv import load_dotenv

from src.modes.automatic import AutomaticMode
from src.modes.interactive import InteractiveMode
from src.modes.blockchain_auto import BlockchainAutoMode
from src.modes.blockchain_chat import BlockchainChatMode
from src.modes.blockchain_payments import BlockchainPaymentsMode

def main():
    """Main entry point for the travel manager."""
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Travel Manager CDP")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["auto", "interactive", "blockchain-auto", "blockchain-chat", "blockchain-payments"],
        default="interactive",
        help="Mode to run the travel manager in"
    )
    args = parser.parse_args()
    
    # Create and run the appropriate mode
    if args.mode == "auto":
        mode = AutomaticMode()
    elif args.mode == "interactive":
        mode = InteractiveMode()
    elif args.mode == "blockchain-auto":
        mode = BlockchainAutoMode()
    elif args.mode == "blockchain-chat":
        mode = BlockchainChatMode()
    elif args.mode == "blockchain-payments":
        mode = BlockchainPaymentsMode()
    else:
        mode = InteractiveMode()
    
    # Run the selected mode
    mode.run()

if __name__ == "__main__":
    main()
