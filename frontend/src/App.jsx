import React, { useEffect, useState } from "react";
import { ethers } from "ethers";
import ERC20_ABI from "./abi/ERC20.json";
import SendEth from "./components/SendEth";
import SendToken from "./components/SendToken";
import "./index.css";

export const NETWORK_ID = 11155111; // Sepolia

function App() {
  const [tab, setTab] = useState("eth");
  const [account, setAccount] = useState(null);
  const [ethBalance, setEthBalance] = useState("0");
  const [tokenBalance, setTokenBalance] = useState("0");

  const TOKEN_ADDRESS = process.env.REACT_APP_ERC_CONTRACT_ADDRESS;

  async function connectWallet() {
    try {
      if (!window.ethereum) {
        alert("Please install MetaMask.");
        return;
      }
      const provider = new ethers.BrowserProvider(window.ethereum);
      const accounts = await provider.send("eth_requestAccounts", []);
      setAccount(accounts[0]);
      const network = await provider.getNetwork();
    console.log("Current network:", network.chainId);

    // 🔹 Force switch to Sepolia if needed
    if (network.chainId !== 11155111n) {
    try {
        await window.ethereum.request({
        method: "wallet_switchEthereumChain",
        params: [{ chainId: "0xaa36a7" }], // Sepolia in hex
        });
        console.log("Switched to Sepolia");
    } catch (switchError) {
        // 🔹 If Sepolia isn't added, add it
        if (switchError.code === 4902) {
        await window.ethereum.request({
            method: "wallet_addEthereumChain",
            params: [
            {
                chainId: "0xaa36a7",
                chainName: "Sepolia Test Network",
                nativeCurrency: { name: "SepoliaETH", symbol: "SEP", decimals: 18 },
                rpcUrls: ["https://rpc.sepolia.org"],
                blockExplorerUrls: ["https://sepolia.etherscan.io"],
            },
            ],
        });
        } else {
        console.error("Failed to switch:", switchError);
        alert("Please manually switch MetaMask to Sepolia network.");
        }
    }
    }
    } catch (error) {
      console.error("Wallet connection failed:", error);
    }
  }

  async function fetchBalances() {
    if (!account || !window.ethereum) return;

    try {
      const provider = new ethers.BrowserProvider(window.ethereum);
      const balanceWei = await provider.getBalance(account);
      setEthBalance(ethers.formatEther(balanceWei));
                console.log(TOKEN_ADDRESS);
                console.log(ERC20_ABI);
        const network = await provider.getNetwork();
        console.log("🔹 Provider connected", provider);
        console.log("🔹 Connected network:", network);
        const code = await provider.getCode(TOKEN_ADDRESS);
console.log("🔹 Contract code at address:", code);
      if (TOKEN_ADDRESS) {
        console.log('aaaaaaaaa');
        const token = new ethers.Contract(TOKEN_ADDRESS, ERC20_ABI, provider);
        const decimals = await token.decimals();
        const tokenBalRaw = await token.balanceOf(account);
        const formattedToken = ethers.formatUnits(tokenBalRaw, decimals);
        setTokenBalance(formattedToken.toString());
      }
    } catch (error) {
      console.error("Error fetching balances:", error);
    }
  }

  // Fetch balances when account changes
  useEffect(() => {
    if (account) fetchBalances();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [account]);

  // Detect account/network change
  useEffect(() => {
    if (window.ethereum) {
      window.ethereum.on("accountsChanged", (accounts) => {
        setAccount(accounts[0] || null);
      });
      window.ethereum.on("chainChanged", () => window.location.reload());
    }
  }, []);

  return (
    <div className="App">
      <h1>Blockchain Transaction Dashboard</h1>

      {account ? (
        <div className="wallet-info">
          <p><strong>Wallet:</strong> {account.slice(0, 6)}...{account.slice(-4)}</p>
          <p><strong>ETH Balance:</strong> {ethBalance} ETH</p>
          <p><strong>Token Balance:</strong> {tokenBalance}</p>
        </div>
      ) : (
        <button className="connect" onClick={connectWallet}>Connect Wallet</button>
      )}

      <div className="tabs">
        <button onClick={() => setTab("eth")} className={tab === "eth" ? "active" : ""}>Send ETH</button>
        <button onClick={() => setTab("token")} className={tab === "token" ? "active" : ""}>Send Token</button>
      </div>

      {tab === "eth" ? <SendEth /> : <SendToken />}
    </div>
  );
}

export default App;
