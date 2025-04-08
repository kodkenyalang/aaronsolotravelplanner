"""
CDP Wallet Provider Integration
"""
import os
import json
import logging
from coinbase_agentkit import CdpWalletProvider, CdpWalletProviderConfig

# Get the module logger
logger = logging.getLogger(__name__)

# Configure a file to persist the agent's CDP API Wallet Data
WALLET_DATA_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "wallet_data.txt")

def initialize_wallet_provider():
    """
    Initialize the CDP Wallet Provider
    Returns the wallet provider instance and any wallet data
    """
    logger.info("Initializing CDP Wallet Provider")
    
    # Initialize CDP Wallet Provider
    wallet_data = None
    if os.path.exists(WALLET_DATA_FILE):
        logger.info(f"Loading wallet data from {WALLET_DATA_FILE}")
        with open(WALLET_DATA_FILE) as f:
            wallet_data = f.read()

    cdp_config = None
    if wallet_data is not None:
        cdp_config = CdpWalletProviderConfig(wallet_data=wallet_data)

    wallet_provider = CdpWalletProvider(cdp_config)
    
    # Make sure the directory exists before saving
    os.makedirs(os.path.dirname(WALLET_DATA_FILE), exist_ok=True)
    
    # Save the wallet data to persist it
    wallet_data_json = json.dumps(wallet_provider.export_wallet().to_dict())
    with open(WALLET_DATA_FILE, "w") as f:
        f.write(wallet_data_json)
        
    logger.info("CDP Wallet Provider initialized")
    
    return wallet_provider
