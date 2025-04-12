### UnoTravel - Blockchain Travel Planning Platform
Project Overview

UnoTravel is a comprehensive travel planning platform that combines intelligent agent-based trip planning with blockchain payment capabilities. Built on the GAME Framework, UnoTravel offers seamless coordination of flights, accommodations, and experiences while supporting cryptocurrency payments through Coinbase Developer Platform integration.

### Key Features

Intelligent Trip Planning: Coordinate all aspects of travel using specialized worker agents
Blockchain Payments: Pay for travel services using cryptocurrency
Loyalty Program: Earn ULT (UnoTravel Loyalty Tokens) for discounts and rewards
Multi-Mode Operation: Choose from automatic, interactive, and blockchain-enabled modes

### Directory Structure

/
├── README.md                  # Project documentation
├── LICENSE                    # Project license (UnoTravel copyright)
├── main.py                    # Main application entry point
├── hardhat.config.js          # Hardhat configuration for smart contracts
├── requirements.txt           # Python dependencies
│
├── contracts/                 # Smart contracts
│   ├── UnoTravelPaymentProcessor.sol  # Payment processing contract
│   └── UnoLoyaltyToken.sol            # Loyalty token contract
│
├── scripts/                   # Deployment scripts
│   └── deploy.js              # Script to deploy contracts
│
├── src/                       # Source code
│   ├── __init__.py            # Package initialization
│   │
│   ├── blockchain/            # Blockchain integration
│   │   ├── __init__.py
│   │   ├── contract_client.py # Smart contract client
│   │   └── token_registry.py  # Token registry
│   │
│   ├── cdp_integration/       # Coinbase Developer Platform integration
│   │   ├── __init__.py
│   │   ├── agent.py           # CDP agent interface
│   │   ├── client.py          # CDP client
│   │   ├── payment.py         # Payment processing
│   │   └── wallet.py          # Wallet management
│   │
│   ├── game_agents/           # Agent definitions
│   │   ├── __init__.py
│   │   ├── agent.py           # Main Travel Manager agent
│   │   └── workers.py         # Worker agent definitions
│   │
│   ├── modes/                 # Application modes
│   │   ├── __init__.py
│   │   ├── automatic.py       # Automatic planning mode
│   │   ├── interactive.py     # Interactive planning mode
│   │   ├── blockchain_payments.py     # Blockchain payments mode
│   │   └── blockchain_chat.py         # Interactive blockchain mode
│   │
│   └── utils/                 # Utilities
│       ├── __init__.py
│       ├── logging.py         # Logging configuration
│       └── state.py           # State management
│
└── tests/                     # Test suite
    ├── __init__.py
    ├── test_blockchain.py     # Blockchain integration tests
    ├── test_cdp.py            # CDP integration tests
    └── test_agents.py         # Agent tests

### Installation

Clone the repository:

git clone https://github.com/your-organization/UnoTravel.git
cd UnoTravel

Install dependencies:

pip install -r requirements.txt
npm install

Set up environment variables:

cp .env.example .env
# Edit .env with your API keys and configuration

### Deploy smart contracts:

npx hardhat run scripts/deploy.js --network sepolia

### Run the application:

python main.py

### Usage

UnoTravel supports four primary modes of operation:

Automatic Mode: The system autonomously plans trips based on preferences.

python main.py --mode automatic

Interactive Mode: Engage in a conversation-driven planning process.

python main.py --mode interactive

Blockchain Auto Mode: Autonomous planning with blockchain payments.

python main.py --mode blockchain-auto

Blockchain Chat Mode: Interactive planning with blockchain payments.

python main.py --mode blockchain-chat

### Blockchain Features

UnoTravel leverages blockchain technology for:

Secure Payments: Process travel payments using popular cryptocurrencies
Loyalty Program: Earn and redeem ULT tokens for discounts
Transaction Verification: Immutable record of all travel bookings
Smart Contract Automation: Automatic refunds and loyalty point distribution



License

This project is licensed under the terms of the UnoTravel License - see the LICENSE file for details.

Contact

For questions or support, please contact:

Email: aaron.ong@zoho.com
