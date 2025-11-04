// scripts/deploy.js
const hre = require("hardhat");

async function main() {
  // Deploy ERC20 token
  const ERC20Token = await hre.ethers.getContractFactory("ERC20");
  const token = await ERC20Token.deploy(1000000);
  await token.waitForDeployment();
  console.log(`ERC20 Token deployed to: ${await token.getAddress()}`);

  // Deploy FraudRegistry contract
  const FraudRegistry = await hre.ethers.getContractFactory("FraudRegistry");
  const fraudRegistry = await FraudRegistry.deploy();
  await fraudRegistry.waitForDeployment();
  console.log(`FraudRegistry deployed to: ${await fraudRegistry.getAddress()}`);

  // Optional: link ERC20 with FraudRegistry
  console.log("\nDeployment complete!");
  console.log({
    ERC20_Token_Address: await token.getAddress(),
    Fraud_Registry_Address: await fraudRegistry.getAddress()
  });
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("Deployment failed:", error);
    process.exit(1);
  });
