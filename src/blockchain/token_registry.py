"""Registry of tokens supported by the travel payment processor."""

from typing import Dict, List

# Token addresses on Base Sepolia testnet
BASE_SEPOLIA_TOKENS = {
    "USDC": "0xf56dc6695CF1f5c4912e8AB1e59C7855CE906599",
    "USDT": "0x162B9566Ad6248B8836Cf5673129e7E66ae89F1C",
    "DAI": "0x5e6F1119354d85e95b81B2270260A6C1A7c2916E",
    "ETH": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",  # Special address for native ETH
    "ULT": "0x..."  # To be filled with deployed UnoLoyaltyToken address
}

# Token addresses on Base mainnet
BASE_MAINNET_TOKENS = {
    "USDC": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    "USDT": "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb",
    "DAI": "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb",
    "ETH": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",  # Special address for native ETH
    "ULT": "0x..."  # To be filled with deployed UnoLoyaltyToken address
}

class TokenRegistry:
    """Registry for supported ERC20 tokens."""
    
    def __init__(self, network: str = "base-sepolia"):
        """Initialize the token registry.
        
        Args:
            network: Blockchain network to use ('base-sepolia' or 'base-mainnet')
        """
        self.network = network
        self.tokens = BASE_SEPOLIA_TOKENS if network == "base-sepolia" else BASE_MAINNET_TOKENS
    
    def get_token_address(self, symbol: str) -> str:
        """Get the address for a token symbol.
        
        Args:
            symbol: Token symbol (e.g., "USDC")
            
        Returns:
            Token address
            
        Raises:
            ValueError: If the token is not supported
        """
        symbol = symbol.upper()
        if symbol not in self.tokens:
            raise ValueError(f"Token {symbol} is not supported on {self.network}")
        
        return self.tokens[symbol]
    
    def get_supported_tokens(self) -> List[str]:
        """Get a list of supported token symbols.
        
        Returns:
            List of token symbols
        """
        return list(self.tokens.keys())
    
    def is_token_supported(self, symbol: str) -> bool:
        """Check if a token is supported.
        
        Args:
            symbol: Token symbol
            
        Returns:
            True if the token is supported, False otherwise
        """
        return symbol.upper() in self.tokens
