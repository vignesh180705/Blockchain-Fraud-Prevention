import React, { useState } from "react";
import { ethers } from "ethers";
import erc20Abi from "../abi/ERC20.json";

export default function SendToken({ selectedToken, TOKENS }) {
  const [receiver, setReceiver] = useState("");
  const [amount, setAmount] = useState("");
  const [status, setStatus] = useState("");
  const [tokenAddress, setTokenAddress] = useState("");

  async function sendToken() {
    try {
      if (!window.ethereum) return setStatus("Please install MetaMask!");
        console.log("Selected Token in SendToken:", selectedToken);
      const provider = new ethers.BrowserProvider(window.ethereum);
      console.log("Provider:", provider);
      await provider.send("eth_requestAccounts", []);
      const signer = await provider.getSigner();
        console.log("Signer:", signer);
      // 🔹 Use predefined token address if not CUSTOM
      const addressToUse =
        selectedToken === "CUSTOM"
          ? tokenAddress
          : TOKENS[selectedToken]?.address;
      if (!ethers.isAddress(addressToUse)) {
        return setStatus("❌ Invalid token contract address");
      }
      console.log("Using token address:", addressToUse);
      const token = new ethers.Contract(addressToUse, erc20Abi, signer);
      const decimals = await token.decimals();
      const amountToSend = ethers.parseUnits(amount, decimals);

      const tx = await token.transfer(receiver, amountToSend);
      setStatus(`✅ Token sent! Tx Hash: ${tx.hash}`);
    } catch (err) {
        
      setStatus(`❌ Error a: ${err.message}`);
    }
  }

  return (
    <div className="eth-container">
      <h2>Send ERC20 Token</h2>

      {/* Only show contract address input for custom tokens */}
      {selectedToken === "CUSTOM" && (
        <input
          type="text"
          placeholder="Token Contract Address"
          value={tokenAddress}
          onChange={(e) => setTokenAddress(e.target.value)}
        />
      )}

      <input
        type="text"
        placeholder="Receiver address"
        value={receiver}
        onChange={(e) => setReceiver(e.target.value)}
      />

      <input
        type="number"
        placeholder="Amount (tokens)"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
      />

      <button onClick={sendToken}>Send Token</button>
      <p>{status}</p>
    </div>
  );
}
