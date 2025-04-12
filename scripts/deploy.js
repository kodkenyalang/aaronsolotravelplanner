const { ethers } = require("hardhat");

async function main() {
  console.log("Deploying UnoTravel contracts to Base blockchain...");

  // Get the contract factories
  const UnoTravelPaymentProcessor = await ethers.getContractFactory("UnoTravelPaymentProcessor");
  const UnoLoyaltyToken = await ethers.getContractFactory("UnoLoyaltyToken");

  // Deploy the loyalty token
  const unoLoyaltyToken = await UnoLoyaltyToken.deploy();
  await unoLoyaltyToken.deployed();
  console.log(`UnoLoyaltyToken deployed to: ${unoLoyaltyToken.address}`);

  // Deploy the payment processor
  const unoTravelPaymentProcessor = await UnoTravelPaymentProcessor.deploy();
  await unoTravelPaymentProcessor.deployed();
  console.log(`UnoTravelPaymentProcessor deployed to: ${unoTravelPaymentProcessor.address}`);

  // Setup the contracts
  console.log("Setting up contracts...");

  // Add the payment processor as a minter for the loyalty token
  const addMinterTx = await unoLoyaltyToken.addMinter(unoTravelPaymentProcessor.address);
  await addMinterTx.wait();
  console.log("Added payment processor as loyalty token minter");

  // Add common tokens to supported tokens (using base testnet addresses)
  // Note: Replace with actual token addresses for Base
  const USDC_ADDRESS = "0xf56dc6695CF1f5c4912e8AB1e59C7855CE906599"; // Example USDC on Base testnet
  const USDT_ADDRESS = "0x162B9566Ad6248B8836Cf5673129e7E66ae89F1C"; // Example USDT on Base testnet
  const DAI_ADDRESS = "0x5e6F1119354d85e95b81B2270260A6C1A7c2916E";  // Example DAI on Base testnet
  
  const addUSDCTx = await unoTravelPaymentProcessor.addSupportedToken(USDC_ADDRESS);
  await addUSDCTx.wait();
  
  const addUSDTTx = await unoTravelPaymentProcessor.addSupportedToken(USDT_ADDRESS);
  await addUSDTTx.wait();
  
  const addDAITx = await unoTravelPaymentProcessor.addSupportedToken(DAI_ADDRESS);
  await addDAITx.wait();
  
  console.log("Added supported tokens to payment processor");

  // Add UnoTravel loyalty token to supported tokens
  const addULTTx = await unoTravelPaymentProcessor.addSupportedToken(unoLoyaltyToken.address);
  await addULTTx.wait();
  console.log("Added loyalty token to supported tokens");

  console.log("Deployment and setup complete!");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
