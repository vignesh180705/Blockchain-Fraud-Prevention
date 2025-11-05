import React, { useState } from "react";
import { ethers } from "ethers";

export default function SendEth({ account }) {
  const [receiver, setReceiver] = useState("");
  const [amount, setAmount] = useState("");
  const [status, setStatus] = useState("");

  async function sendEth() {
    try {
      if (!window.ethereum) return alert("Please install MetaMask.");
      const provider = new ethers.BrowserProvider(window.ethereum);
      const signer = await provider.getSigner();

      // Step 1: Prepare fraud check data
      const payload = {
        sender: account,
        receiver,
        amount: amount,
        features: {}, // optional or from backend
      };

      // Step 2: Call Flask ML API
      const response = await fetch("http://127.0.0.1:5000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const result = await response.json();

      if (result.status === "rejected") {
        setStatus(`🚫 Fraudulent Transaction Detected!`);
        return;
      }

      // Step 3: Proceed with ETH transaction if legit
      const tx = await signer.sendTransaction({
        to: receiver,
        value: ethers.parseEther(amount),
      });

      setStatus(`✅ Transaction sent! Hash: ${tx.hash}`);
    } catch (err) {
      console.error(err);
      setStatus(`❌ Error: ${err.message}`);
    }
  }

  return (
    <div className="eth-container">
      <h2>Send ETH</h2>
      <input
        type="text"
        placeholder="Receiver Address"
        value={receiver}
        onChange={(e) => setReceiver(e.target.value)}
      />
      <input
        type="number"
        placeholder="Amount (ETH)"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
      />
      <button onClick={sendEth}>Send</button>
      <p>{status}</p>
    </div>
  );
}
