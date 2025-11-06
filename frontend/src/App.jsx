import React, { useEffect, useState } from "react";
import { ethers } from "ethers";
import ERC20_ABI from "./abi/ERC20.json";
import SendEth from "./components/SendEth";
import SendToken from "./components/SendToken";
import TransactionHistory from "./components/TransactionHistory";
import "./index.css";

export const NETWORK_ID = 11155111; // Sepolia

const TOKENS = {
  MYTOKEN: { name: "MyToken", symbol: "MTK", address: process.env.REACT_APP_ERC_CONTRACT_ADDRESS },
  LINK: { name: "Chainlink Token", symbol: "LINK", address: "0x779877A7B0D9E8603169DdbD7836e478b4624789" },
  WETH: { name: "Wrapped Ether", symbol: "WETH", address: "0xdd13E55209Fd76AfE204dBda4007C227904f0a81" },
};

function App() {
  const [tab, setTab] = useState("eth");
  const [selectedToken, setSelectedToken] = useState("MYTOKEN");
  const [account, setAccount] = useState(null);
  const [ethBalance, setEthBalance] = useState("0");
  const [tokenBalance, setTokenBalance] = useState("0");
  const [customTokenAddress, setCustomTokenAddress] = useState("");
  const [customTokenInfo, setCustomTokenInfo] = useState(null);
  const [showDashboard, setShowDashboard] = useState(false);

  async function connectWallet() {
    if (!window.ethereum) return alert("Please install MetaMask.");
    try {
      const provider = new ethers.BrowserProvider(window.ethereum);
      const accounts = await provider.send("eth_requestAccounts", []);
      setAccount(accounts[0]);
    } catch (err) {
      console.error("Wallet connection failed:", err);
    }
  }

  const disconnectWallet = () => {
    setAccount(null);
    setEthBalance("0");
    setTokenBalance("0");
    setCustomTokenInfo(null);
    setCustomTokenAddress("");
    setShowDashboard(false);
  };

  async function fetchBalances() {
    if (!account || !window.ethereum) return;
    try {
      const provider = new ethers.BrowserProvider(window.ethereum);
      const balanceWei = await provider.getBalance(account);
      setEthBalance(ethers.formatEther(balanceWei));

      const currentToken = TOKENS[selectedToken];
      const tokenAddress = selectedToken === "CUSTOM" ? customTokenAddress : currentToken.address;

      if (tokenAddress && ethers.isAddress(tokenAddress)) {
        const code = await provider.getCode(tokenAddress);
        if (code !== "0x") {
          const token = new ethers.Contract(tokenAddress, ERC20_ABI, provider);
          const decimals = await token.decimals();
          const tokenBalRaw = await token.balanceOf(account);
          setTokenBalance(ethers.formatUnits(tokenBalRaw, decimals));
        } else setTokenBalance("0");
      } else setTokenBalance("0");
    } catch (err) {
      console.error("Error fetching balances:", err);
    }
  }

  async function fetchCustomTokenInfo(address) {
    if (!ethers.isAddress(address)) return alert("Invalid token address");
    try {
      const provider = new ethers.BrowserProvider(window.ethereum);
      const token = new ethers.Contract(address, ERC20_ABI, provider);
      const [name, symbol, decimals, balanceRaw] = await Promise.all([
        token.name(), token.symbol(), token.decimals(), token.balanceOf(account)
      ]);
      setCustomTokenInfo({ name, symbol, decimals, balance: ethers.formatUnits(balanceRaw, decimals) });
      setTokenBalance(ethers.formatUnits(balanceRaw, decimals));
    } catch (err) {
      console.error(err);
      alert("Failed to fetch token details.");
    }
  }

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { if (account) fetchBalances(); }, [account, selectedToken]);

  useEffect(() => {
    if (!window.ethereum) return;
    const handleAccounts = (accounts) => setAccount(accounts[0] || null);
    const handleChain = () => window.location.reload();
    window.ethereum.on("accountsChanged", handleAccounts);
    window.ethereum.on("chainChanged", handleChain);
    return () => {
      window.ethereum.removeListener("accountsChanged", handleAccounts);
      window.ethereum.removeListener("chainChanged", handleChain);
    };
  }, []);

  return (
    <div className="App">
      <h1>Blockchain Transaction Dashboard</h1>

      {account ? (
        <div className="wallet">
          <p><strong>Wallet:</strong> {account.slice(0, 6)}...{account.slice(-4)}</p>
          <p><strong>ETH Balance:</strong> {ethBalance} ETH</p>
          <p><strong>{selectedToken === "CUSTOM" ? customTokenInfo?.symbol || "Custom" : TOKENS[selectedToken].symbol} Balance:</strong> {tokenBalance}</p>
          <button onClick={disconnectWallet}>Disconnect</button>
        </div>
      ) : (
        <button className="connect" onClick={connectWallet}>Connect Wallet</button>
      )}

      <div className="token-selector">
        <label>Select Token: </label>
        <select value={selectedToken} onChange={(e) => setSelectedToken(e.target.value)}>
          <option value="CUSTOM">Custom Token</option>
          {Object.keys(TOKENS).map(key => (
            <option key={key} value={key}>{TOKENS[key].name} ({TOKENS[key].symbol})</option>
          ))}
        </select>
      </div>

      {selectedToken === "CUSTOM" && (
        <div className="custom-token">
          <input type="text" placeholder="Paste token contract address" value={customTokenAddress} onChange={(e) => setCustomTokenAddress(e.target.value)} />
          <button onClick={() => fetchCustomTokenInfo(customTokenAddress)}>Fetch Token Info</button>
          {customTokenInfo && (
            <div>
              <p><strong>Name:</strong> {customTokenInfo.name}</p>
              <p><strong>Symbol:</strong> {customTokenInfo.symbol}</p>
              <p><strong>Decimals:</strong> {customTokenInfo.decimals}</p>
              <p><strong>Balance:</strong> {customTokenInfo.balance}</p>
            </div>
          )}
        </div>
      )}

      <div className="tabs">
        <button onClick={() => setTab("eth")} className={tab === "eth" ? "active" : ""}>Send ETH</button>
        <button onClick={() => setTab("token")} className={tab === "token" ? "active" : ""}>Send Token</button>
      </div>
      {tab === "eth" ? <SendEth account={account} /> : <SendToken selectedToken={selectedToken} TOKENS={TOKENS} account={account} />}

      {account && (
        <button className="dashboard-toggle" onClick={() => setShowDashboard(!showDashboard)}>
          {showDashboard ? "Hide Wallet Dashboard" : "Show Wallet Dashboard"}
        </button>
      )}

      {showDashboard && (
        <div className="wallet-dashboard">
          <TransactionHistory account={account} />
        </div>
      )}
    </div>
  );
}

export default App;
