import React, { useState } from "react";
import { ethers } from "ethers";
import erc20Abi from "../abi/ERC20.json";

export default function SendToken({ selectedToken, TOKENS }) {
    const [receiver, setReceiver] = useState("");
    const [amount, setAmount] = useState("");
    const [status, setStatus] = useState("");
    const [tokenAddress, setTokenAddress] = useState("");
    const [success, setSuccess] = useState(false);

    async function sendToken() {
        try {
            if (!window.ethereum) return setStatus("Please install MetaMask!");

            setStatus("Checking transaction for fraud...");
            const provider = new ethers.BrowserProvider(window.ethereum);
            await provider.send("eth_requestAccounts", []);
            const signer = await provider.getSigner();
            const sender = await signer.getAddress();

            const addressToUse =
                selectedToken === "CUSTOM"
                    ? tokenAddress
                    : TOKENS[selectedToken]?.address;

            if (!ethers.isAddress(addressToUse)) {
                setStatus("Invalid token contract address");
                setSuccess(false);
                return;
            }

            const fraudCheck = await fetch("http://127.0.0.1:5000/predict", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    sender,
                    receiver,
                    amount,
                    token: selectedToken,
                    tokenAddress: addressToUse,
                }),
            });

            const result = await fraudCheck.json();
            console.log("ML result:", result);

            if (result.prediction === "fraudulent") {
                setStatus("Transaction flagged as fraudulent, hence blocked.");
                setSuccess(false);
                await fetch("http://127.0.0.1:5000/logFraud", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ sender, receiver, amount, token: selectedToken }),
                });
                return;
            }

            setStatus("Legitimate transaction. Sending token...");
            setSuccess(true);

            const token = new ethers.Contract(addressToUse, erc20Abi, signer);
            const decimals = await token.decimals();
            const amountToSend = ethers.parseUnits(amount, decimals);

            const tx = await token.transfer(receiver, amountToSend);
            setStatus(`Token sent! Tx Hash: ${tx.hash}`);
            setSuccess(true);

        } catch (err) {
            console.error("Error:", err);
            setStatus(`Error: ${err.message}`);
            setSuccess(false);
        }
    }

    return (
        <div className="eth-container">
            <h2>Send ERC20 Token</h2>

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
            {status && (
              <p style={{ backgroundColor: success ? "green" : "red", color: "white", padding: "8px" }}>
                {status}
              </p>
            )}
            <button onClick={sendToken}>Send Token</button>
        </div>
    );
}
