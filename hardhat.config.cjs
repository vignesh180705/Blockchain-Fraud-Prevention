require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();



module.exports = {
  solidity: "0.8.28",
  networks: {
    sepolia: {
      url: process.env.INFURE_PROJECT_URL,   // from Infura
      accounts: [`0x${process.env.METAMASK_PRIVATE_KEY}`],
    },
  },
};