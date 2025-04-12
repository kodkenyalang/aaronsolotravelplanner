const { ethers } = require("hardhat");

async function main() {
  console.log("Deploying Travel Manager contracts to Base blockchain...");

  // Get the contract factories
  const TravelPaymentProcessor = await ethers.getContractFactory("TravelPaymentProcessor");
  const TravelLoyaltyToken = await ethers.getContractFactory("TravelLoyaltyToken");

  // Deploy the loyalty token
  const travelLoyaltyToken = await TravelLoyaltyToken.deploy();
  await travelLoyaltyToken.deployed();
  console.log(`TravelLoyaltyToken deployed to: ${travelLoyaltyToken.address}`);

  // Deploy the payment processor
  const travelPaymentProcessor = await TravelPaymentProcessor.deploy();
  await travelPaymentProcessor.deployed();
  console.log(`TravelPaymentProcessor deployed to: ${travelPaymentProcessor.address}`);

  // Setup the contracts
  console.log("Setting up contracts...");

  // Add the payment processor as a minter for the loyalty token
  const addMinterTx = await travelLoyaltyToken.addMinter(travelPaymentProcessor.address);
  await addMinterTx.wait();
  console.log("Added payment processor as loyalty token minter");

  // Add common tokens to supported tokens (using base testnet addresses)
  // Note: Replace with actual token addresses for Base
  const USDC_ADDRESS = "0xf56dc6695CF1f5c4912e8AB1e59C7855CE906599"; // Example USDC on Base testnet
  const USDT_ADDRESS = "0x162B9566Ad6248B8836Cf5673129e7E66ae89F1C"; // Example USDT on Base testnet
  const DAI_ADDRESS = "0x5e6F1119354d85e95b81B2270260A6C1A7c2916E";  // Example DAI on Base testnet
  
  const addUSDCTx = await travelPaymentProcessor.addSupportedToken(USDC_ADDRESS);
  await addUSDCTx.wait();
  
  const addUSDTTx = await travelPaymentProcessor.addSupportedToken(USDT_ADDRESS);
  await addUSDTTx.wait();
  
  const addDAITx = await travelPaymentProcessor.addSupportedToken(DAI_ADDRESS);
  await addDAITx.wait();
  
  console.log("Added supported tokens to payment processor");

  // Add travel loyalty token to supported tokens
  const addTLTTx = await travelPaymentProcessor.addSupportedToken(travelLoyaltyToken.address);
  await addTLTTx.wait();
  console.log("Added loyalty token to supported tokens");

  console.log("Deployment and setup complete!");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
