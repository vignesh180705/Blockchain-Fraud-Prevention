import React, { useState } from "react";
import { ethers } from "ethers";

export default function SendEth() {
  const [receiver, setReceiver] = useState("");
  const [amount, setAmount] = useState("");
  const [status, setStatus] = useState("");

  async function sendEth() {
    try {
      if (!window.ethereum) return setStatus("Please install MetaMask!");

      const provider = new ethers.BrowserProvider(window.ethereum);
      await provider.send("eth_requestAccounts", []);
      const signer = await provider.getSigner();

      const tx = await signer.sendTransaction({
        to: receiver,
        value: ethers.parseEther(amount),
      });

      setStatus(`✅ Transaction sent! Hash: ${tx.hash}`);
    } catch (err) {
      setStatus(`❌ Error: ${err.message}`);
    }
  }

  return (
    <div className="eth-container">
      <h2>Send ETH</h2>
      <input
        type="text"
        placeholder="Receiver address"
        value={receiver}
        onChange={(e) => setReceiver(e.target.value)}
      />
      <input
        type="number"
        placeholder="Amount (ETH)"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
      />
      <button onClick={sendEth}>Send ETH</button>
      <p>{status}</p>
    </div>
  );
}
