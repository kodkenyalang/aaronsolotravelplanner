# UnoTravel


> An AI-powered travel management system with blockchain payment capabilities.

## Overview

UnoTravel is an innovative travel management system that combines AI-powered travel planning with blockchain payment capabilities. It leverages the GAME Framework for orchestrating travel planning tasks and the Coinbase Developer Platform (CDP) AgentKit for blockchain payment processing.

The system demonstrates how to integrate modern AI-driven task planning with decentralized payment systems, providing a comprehensive travel planning experience with cryptocurrency payment options.

## Features

- 🧠 **AI-Powered Planning**: Utilizes DeepSeek V3 through OpenRouter for intelligent travel planning
- 🔗 **Blockchain Payments**: Processes cryptocurrency payments via Coinbase Developer Platform
- 👥 **Specialised Workers**: Dedicated workers for flights, hotels, experiences, and payments
- 🔄 **Multiple Operation Modes**:
  - **Automatic**: AI makes all travel decisions autonomously
  - **Interactive**: User guides the AI travel decisions
  - **Blockchain Auto**: AI makes travel & blockchain decisions autonomously
  - **Blockchain Chat**: User guides both travel & blockchain decisions
- 💼 **State Management**: Maintains state across both travel planning and blockchain operations

## System Architecture

```
aaronsolotravelplanner/
├── src/
│   ├── game_agents/       # GAME framework agents & workers
│   ├── cdp_integration/   # Coinbase Developer Platform integration
│   ├── utils/             # Utility functions & state management
│   └── modes/             # Different operational modes
```

The system is designed with a modular architecture:

1. **GAME Framework Integration**: Uses GAME SDK to orchestrate travel planning through specialized workers
2. **CDP AgentKit Integration**: Connects to blockchain networks to process crypto payments
3. **OpenRouter Integration**: Leverages DeepSeek V3 for advanced natural language understanding
4. **Mode-based Execution**: Supports different operational modes for flexibility

## Installation

1. Clone the repository:
   ```bash
   git clone kodkenyalang/aaronsolotravelplanner/final.git
   cd travel-manager-cdp
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your API keys:
   ```
   GAME_API_KEY=your_game_api_key_here
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   CDP_API_KEY=your_cdp_api_key_here
   ```

## Usage

Run the application:
```bash
python main.py
```

Follow the prompts to select an operating mode:
1. **Automatic Mode**: AI makes all travel decisions
2. **Interactive Mode**: You guide the AI travel decisions
3. **Blockchain Auto Mode**: AI makes travel & blockchain decisions
4. **Blockchain Chat Mode**: You guide travel & blockchain decisions

### Example Interaction (Interactive Mode)

```
🔄 Select Operating Mode:
1. Automatic Mode - AI makes all travel decisions
2. Interactive Mode - You guide the AI travel decisions
3. Blockchain Auto Mode - AI makes travel & blockchain decisions
4. Blockchain Chat Mode - You guide travel & blockchain decisions

Enter choice (1-4): 2

👤 Running in INTERACTIVE MODE - You'll guide the AI decisions

📊 Initial State:
{
    "customer_satisfaction": 0,
    "budget_remaining": 1000,
    "trip_completeness": 0,
    "interaction_mode": "interactive",
    "blockchain_enabled": false,
    "wallet_balance": 0,
    "wallet_tokens": {
        "ETH": "0",
        "USDC": "0",
        "USDT": "0",
        "DAI": "0"
    }
}

📊 Current Status:
Budget: $1000
Satisfaction: 0
Trip Completeness: 0%

🤔 AI Recommendation:
Based on the current state, the AI would recommend the next steps...

⚠️ Confirm action: Would you like to see what the AI recommends? (y/n): y

💡 AI Recommends: Based on the current state of planning, you should:
- Gather customer preferences first
- Research potential destinations

🧰 Available Workers:
1. TRAVEL_CONSULTANT - Collects and analyzes customer travel preferences and requirements.
   Actions:
   1. gather_preferences - Gather travel preferences from the customer

[...]
```

### Example Interaction (Blockchain Chat Mode)

```
🔄 Select Operating Mode:
1. Automatic Mode - AI makes all travel decisions
2. Interactive Mode - You guide the AI travel decisions
3. Blockchain Auto Mode - AI makes travel & blockchain decisions
4. Blockchain Chat Mode - You guide travel & blockchain decisions

Enter choice (1-4): 4

👤🔗 Running in BLOCKCHAIN CHAT MODE - You'll guide AI decisions with blockchain options

🔗 Initializing blockchain connection through CDP AgentKit...
Fetching network information...
Connected to network: base-sepolia
Wallet address: 0x1234...abcd

📊 Initial State:
{
    "customer_satisfaction": 0,
    "budget_remaining": 1000,
    "trip_completeness": 0,
    "interaction_mode": "blockchain_chat",
    "blockchain_enabled": true,
    "wallet_balance": 100,
    "wallet_tokens": {
        "ETH": "0.1",
        "USDC": "100",
        "USDT": "100",
        "DAI": "100"
    }
}

[...]

💰 Blockchain Payment Options:
1. Check wallet balance
2. Request funds from faucet
3. Process payment for travel service
4. Swap tokens (e.g., ETH to USDC)
5. Transfer tokens to another address
6. Get token price
7. Explore DeFi options

Select blockchain action (1-7): 3

Enter payment amount: 100
Enter currency (e.g., ETH, USDC): USDC
Enter service type (flight, hotel, experience): hotel

⚠️ Confirm action: Process payment of 100 USDC for hotel (y/n): y
Processing payment...
Transaction hash: 0x5678...efgh
Payment completed successfully!
```

## API Reference

### GAME Framework

The application uses the GAME SDK to orchestrate travel planning:

- **Agent**: Central Travel Manager that coordinates tasks
- **Workers**: Specialized workers for different travel tasks
- **Functions**: Task implementations for travel operations

### Coinbase Developer Platform

The CDP integration enables blockchain operations:

- **Wallet Management**: Create and manage blockchain wallets
- **Token Operations**: Check balances, swap tokens, transfer tokens
- **Payment Processing**: Process crypto payments for travel services

### OpenRouter

DeepSeek V3 through OpenRouter powers the intelligent capabilities:

- **Natural Language Understanding**: Process user travel preferences
- **Decision Making**: Select optimal travel options
- **Task Planning**: Orchestrate complex travel arrangements

## DeepSeek V3 Integration

This project leverages DeepSeek V3 through the OpenRouter API for all AI interactions:

- **High-quality Language Understanding**: Better comprehension of travel preferences and requirements
- **Improved Decision-Making**: More sophisticated travel planning recommendations
- **Natural Interactions**: Enhanced conversational capabilities for better user experience
- **Blockchain Comprehension**: Advanced understanding of blockchain concepts for payment processing

The integration with DeepSeek V3 allows the system to provide more nuanced travel recommendations and better understand complex user requests, significantly improving the quality of the travel planning experience.


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [GAME Framework](https://github.com/game-by-virtuals/game-python) for agent orchestration
- [Coinbase Developer Platform](https://www.coinbase.com/cloud/products/developer-platform) for blockchain integration
- [OpenRouter](https://openrouter.ai/) for providing access to DeepSeek V3 and other models
- [DeepSeek](https://deepseek.com) for their advanced language model technology
