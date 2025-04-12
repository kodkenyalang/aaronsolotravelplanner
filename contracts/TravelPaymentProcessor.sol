// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/**
 * @title TravelPaymentProcessor
 * @dev Handles payments for travel services on the Base blockchain
 */
contract TravelPaymentProcessor is Ownable, ReentrancyGuard {
    // Supported payment tokens
    mapping(address => bool) public supportedTokens;
    
    // Service providers
    mapping(address => bool) public serviceProviders;
    
    // Payment records
    struct Payment {
        address user;
        address token;
        uint256 amount;
        string serviceType; // "flight", "hotel", "experience"
        uint256 timestamp;
        bool refunded;
    }
    
    // Mapping of payment IDs to payment details
    mapping(bytes32 => Payment) public payments;
    
    // User transaction history
    mapping(address => bytes32[]) public userPayments;
    
    // Loyalty points
    mapping(address => uint256) public loyaltyPoints;
    
    // Events
    event PaymentProcessed(bytes32 paymentId, address user, address token, uint256 amount, string serviceType);
    event PaymentRefunded(bytes32 paymentId, address user, address token, uint256 amount);
    event TokenAdded(address token);
    event TokenRemoved(address token);
    event ServiceProviderAdded(address provider);
    event ServiceProviderRemoved(address provider);
    event LoyaltyPointsEarned(address user, uint256 points);
    event LoyaltyPointsRedeemed(address user, uint256 points, uint256 amount);
    
    constructor() {
        // Initialize with owner as the first service provider
        serviceProviders[msg.sender] = true;
    }
    
    /**
     * @dev Add a supported payment token
     * @param _token The address of the ERC20 token
     */
    function addSupportedToken(address _token) external onlyOwner {
        require(_token != address(0), "Invalid token address");
        supportedTokens[_token] = true;
        emit TokenAdded(_token);
    }
    
    /**
     * @dev Remove a supported payment token
     * @param _token The address of the ERC20 token
     */
    function removeSupportedToken(address _token) external onlyOwner {
        require(supportedTokens[_token], "Token not supported");
        supportedTokens[_token] = false;
        emit TokenRemoved(_token);
    }
    
    /**
     * @dev Add a service provider
     * @param _provider The address of the service provider
     */
    function addServiceProvider(address _provider) external onlyOwner {
        require(_provider != address(0), "Invalid provider address");
        serviceProviders[_provider] = true;
        emit ServiceProviderAdded(_provider);
    }
    
    /**
     * @dev Remove a service provider
     * @param _provider The address of the service provider
     */
    function removeServiceProvider(address _provider) external onlyOwner {
        require(serviceProviders[_provider], "Not a service provider");
        serviceProviders[_provider] = false;
        emit ServiceProviderRemoved(_provider);
    }
    
    /**
     * @dev Process a payment for a travel service
     * @param _token The address of the payment token
     * @param _amount The payment amount
     * @param _serviceType The type of service being paid for
     * @param _recipient The service provider receiving the payment
     * @return The payment ID
     */
    function processPayment(
        address _token,
        uint256 _amount,
        string calldata _serviceType,
        address _recipient
    ) external nonReentrant returns (bytes32) {
        require(supportedTokens[_token], "Token not supported");
        require(serviceProviders[_recipient], "Invalid service provider");
        require(_amount > 0, "Amount must be greater than 0");
        
        // Transfer tokens from user to contract
        IERC20 token = IERC20(_token);
        require(token.transferFrom(msg.sender, address(this), _amount), "Transfer failed");
        
        // Transfer tokens to service provider
        require(token.transfer(_recipient, _amount), "Transfer to provider failed");
        
        // Generate payment ID
        bytes32 paymentId = keccak256(abi.encodePacked(
            msg.sender,
            _token,
            _amount,
            _serviceType,
            block.timestamp
        ));
        
        // Store payment details
        payments[paymentId] = Payment({
            user: msg.sender,
            token: _token,
            amount: _amount,
            serviceType: _serviceType,
            timestamp: block.timestamp,
            refunded: false
        });
        
        // Add to user's payment history
        userPayments[msg.sender].push(paymentId);
        
        // Award loyalty points (1 point per token unit)
        uint256 points = _amount / (10 ** 18);
        if (points > 0) {
            loyaltyPoints[msg.sender] += points;
            emit LoyaltyPointsEarned(msg.sender, points);
        }
        
        emit PaymentProcessed(paymentId, msg.sender, _token, _amount, _serviceType);
        return paymentId;
    }
    
    /**
     * @dev Refund a payment
     * @param _paymentId The ID of the payment to refund
     */
    function refundPayment(bytes32 _paymentId) external nonReentrant {
        Payment storage payment = payments[_paymentId];
        
        require(payment.user != address(0), "Payment does not exist");
        require(serviceProviders[msg.sender], "Only service providers can refund");
        require(!payment.refunded, "Payment already refunded");
        
        // Mark as refunded
        payment.refunded = true;
        
        // Transfer tokens back to user
        IERC20 token = IERC20(payment.token);
        require(token.transferFrom(msg.sender, payment.user, payment.amount), "Refund transfer failed");
        
        emit PaymentRefunded(_paymentId, payment.user, payment.token, payment.amount);
    }
    
    /**
     * @dev Get all payments for a user
     * @param _user The user address
     * @return Array of payment IDs
     */
    function getUserPayments(address _user) external view returns (bytes32[] memory) {
        return userPayments[_user];
    }
    
    /**
     * @dev Get payment details
     * @param _paymentId The payment ID
     * @return Payment details
     */
    function getPaymentDetails(bytes32 _paymentId) external view returns (
        address user,
        address token,
        uint256 amount,
        string memory serviceType,
        uint256 timestamp,
        bool refunded
    ) {
        Payment memory payment = payments[_paymentId];
        return (
            payment.user,
            payment.token,
            payment.amount,
            payment.serviceType,
            payment.timestamp,
            payment.refunded
        );
    }
    
    /**
     * @dev Redeem loyalty points for tokens
     * @param _amount The amount of points to redeem
     * @param _token The address of the token to receive
     */
    function redeemLoyaltyPoints(uint256 _amount, address _token) external nonReentrant {
        require(supportedTokens[_token], "Token not supported");
        require(loyaltyPoints[msg.sender] >= _amount, "Insufficient loyalty points");
        
        // Convert points to tokens (1 point = 0.01 tokens)
        uint256 tokenAmount = (_amount * (10 ** 18)) / 100;
        
        // Deduct points
        loyaltyPoints[msg.sender] -= _amount;
        
        // Transfer tokens to user
        IERC20 token = IERC20(_token);
        require(token.transfer(msg.sender, tokenAmount), "Redemption transfer failed");
        
        emit LoyaltyPointsRedeemed(msg.sender, _amount, tokenAmount);
    }
}
