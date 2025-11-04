import React, { useState } from "react";
import { ethers } from "ethers";
import erc20Abi from "../abi/ERC20.json";

export default function SendToken() {
  const [receiver, setReceiver] = useState("");
  const [amount, setAmount] = useState("");
  const [status, setStatus] = useState("");
  const [tokenAddress, setTokenAddress] = useState("");

  async function sendToken() {
    try {
      if (!window.ethereum) return setStatus("Please install MetaMask!");

      const provider = new ethers.BrowserProvider(window.ethereum);
      await provider.send("eth_requestAccounts", []);
      const signer = await provider.getSigner();

      const token = new ethers.Contract(tokenAddress, erc20Abi, signer);
      const decimals = await token.decimals();
      const amountToSend = ethers.parseUnits(amount, decimals);

      const tx = await token.transfer(receiver, amountToSend);
      setStatus(`✅ Token sent! Tx Hash: ${tx.hash}`);
    } catch (err) {
      setStatus(`❌ Error: ${err.message}`);
    }
  }

  return (
    <div className="eth-container">
      <h2>Send ERC20 Token</h2>
      <input
        type="text"
        placeholder="Token Contract Address"
        value={tokenAddress}
        onChange={(e) => setTokenAddress(e.target.value)}
      />
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
