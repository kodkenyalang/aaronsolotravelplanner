# UnoTravel


One-stop travel platform with AI planning and blockchain payments

## Overview

UnoTravel is a revolutionary travel platform that combines AI-powered travel planning with blockchain payment capabilities on the Base network. It provides a seamless travel experience from planning to payment in one unified interface.

The platform leverages cutting-edge AI agents through the GAME Framework to orchestrate complex travel planning tasks while integrating with Base blockchain for secure, transparent payments using cryptocurrency.

## Features

### AI-Powered Travel Planning
- Personalized travel recommendations based on preferences
- Intelligent flight and hotel suggestions
- Curated experience recommendations
- Dynamic itinerary building

### Blockchain Payments
- Secure payments using cryptocurrency on Base blockchain
- Support for multiple tokens (USDC, USDT, DAI, ETH)
- On-chain transaction history
- Loyalty rewards system with UnoTravel Loyalty Tokens (ULT)

### Multiple Operational Modes
- **Automatic Mode**: AI agent manages the entire travel planning process
- **Interactive Mode**: Guide the AI through your preferences with interactive prompts
- **Blockchain Auto Mode**: Automatic planning with blockchain payments
- **Blockchain Chat Mode**: Interactive planning with blockchain payments
- **Blockchain Payments Mode**: Dedicated interface for managing travel purchases

## Architecture

UnoTravel is built on a modular architecture:

1. **GAME Agents**: Orchestrates specialized workers for different travel tasks
2. **Base Blockchain Integration**: Handles payments and loyalty on Base network
3. **Smart Contracts**: 
   - UnoTravelPaymentProcessor: Manages payment processing
   - UnoLoyaltyToken: ERC20 token for loyalty rewards
4. **CDP Integration**: Connects with Coinbase Developer Platform
5. **State Management**: Tracks trip details and user preferences

## Getting Started

### Prerequisites
- Python 3.9+
- Node.js and npm (for smart contract deployment)
- Base blockchain wallet

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/unotravel.git
cd unotravel

# Install Python dependencies
pip install -r requirements.txt

# Install smart contract dependencies
npm install
