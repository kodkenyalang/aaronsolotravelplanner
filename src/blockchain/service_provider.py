"""Registry of service providers supported by the travel payment processor."""

from typing import Dict, List

# Service provider addresses for testing
TEST_SERVICE_PROVIDERS = {
    "FLIGHTS": "0x1234567890123456789012345678901234567890",
    "HOTELS": "0x2345678901234567890123456789012345678901",
    "EXPERIENCES": "0x3456789012345678901234567890123456789012"
}

class ServiceProviderRegistry:
    """Registry for service providers."""
    
    def __init__(self):
        """Initialize the service provider registry."""
        self.providers = TEST_SERVICE_PROVIDERS.copy()
    
    def get_provider_address(self, service_type: str) -> str:
        """Get the address for a service provider.
        
        Args:
            service_type: Type of service ("FLIGHTS", "HOTELS", "EXPERIENCES")
            
        Returns:
            Provider address
            
        Raises:
            ValueError: If the service type is not supported
        """
        service_type = service_type.upper()
        if service_type not in self.providers:
            raise ValueError(f"Service provider for {service_type} not found")
        
        return self.providers[service_type]
    
    def get_supported_services(self) -> List[str]:
        """Get a list of supported service types.
        
        Returns:
            List of service types
        """
        return list(self.providers.keys())
    
    def is_service_supported(self, service_type: str) -> bool:
        """Check if a service type is supported.
        
        Args:
            service_type: Service type
            
        Returns:
            True if the service type is supported, False otherwise
        """
        return service_type.upper() in self.providers
