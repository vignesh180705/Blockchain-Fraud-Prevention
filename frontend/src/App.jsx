import React, { useEffect, useState } from "react";
import { ethers } from "ethers";
import ERC20_ABI from "./abi/ERC20.json";
import SendEth from "./components/SendEth";
import SendToken from "./components/SendToken";
import "./index.css";

export const NETWORK_ID = 11155111; // Sepolia

const TOKENS = {
  MYTOKEN: {
    name: "MyToken",
    symbol: "MTK",
    address: process.env.REACT_APP_ERC_CONTRACT_ADDRESS,
  },
  LINK: {
    name: "Chainlink Token",
    symbol: "LINK",
    address: "0x779877A7B0D9E8603169DdbD7836e478b4624789",
  },
  WETH: {
    name: "Wrapped Ether",
    symbol: "WETH",
    address: "0xdd13E55209Fd76AfE204dBda4007C227904f0a81",
  },
};

function App() {
    const [tab, setTab] = useState("eth");
    const [selectedToken, setSelectedToken] = useState("MYTOKEN");
    const [account, setAccount] = useState(null);
    const [ethBalance, setEthBalance] = useState("0");
    const [tokenBalance, setTokenBalance] = useState("0");
    const [customTokenAddress, setCustomTokenAddress] = useState("");
    const [customTokenInfo, setCustomTokenInfo] = useState(null);

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

            // 🔹 Fetch ETH balance
            const balanceWei = await provider.getBalance(account);
            setEthBalance(ethers.formatEther(balanceWei));

            // 🔹 Get token address from selection
            const currentToken = TOKENS[selectedToken];
            const tokenAddress = selectedToken === "CUSTOM" ? customTokenAddress : currentToken.address;

            // 🔹 Check if token contract is valid
            if (tokenAddress && ethers.isAddress(tokenAddress)) {
            const code = await provider.getCode(tokenAddress);
            if (code !== "0x") {
                const token = new ethers.Contract(tokenAddress, ERC20_ABI, provider);
                const decimals = await token.decimals();
                const tokenBalRaw = await token.balanceOf(account);
                const formattedToken = ethers.formatUnits(tokenBalRaw, decimals);
                setTokenBalance(formattedToken.toString());
            } else {
                console.warn(`No contract found at ${tokenAddress}`);
                setTokenBalance("0");
            }
            } else {
            setTokenBalance("0");
            }

        } catch (error) {
            console.error("Error fetching balances:", error);
        }
        }

    async function fetchCustomTokenInfo(address) {
        try {
            if (!ethers.isAddress(address)) {
            alert("Invalid token address");
            return;
            }

            const provider = new ethers.BrowserProvider(window.ethereum);
            const code = await provider.getCode(address);
            if (code === "0x") {
            alert("No contract found at this address");
            return;
            }

            const token = new ethers.Contract(address, ERC20_ABI, provider);
            const [name, symbol, decimals, balanceRaw] = await Promise.all([
            token.name(),
            token.symbol(),
            token.decimals(),
            token.balanceOf(account)
            ]);

            const balance = ethers.formatUnits(balanceRaw, decimals);

            setCustomTokenInfo({ name, symbol, decimals, balance });
            setTokenBalance(balance.toString());
        } catch (err) {
            console.error("❌ Error fetching token info:", err);
            alert("Failed to fetch token details. Check console for details.");
        }
    }

    // Fetch balances when account changes
    useEffect(() => {
    if (account) fetchBalances();
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [account, selectedToken]);

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
            <p>
                <strong>
                    {selectedToken === "CUSTOM"
                    ? customTokenInfo?.symbol || "Custom"
                    : TOKENS[selectedToken].symbol} Balance:
                </strong>{" "}
                {tokenBalance}
            </p>
        </div>
        ) : (
        <button className="connect" onClick={connectWallet}>Connect Wallet</button>
        )}
    <div className="token-selector">
        <label htmlFor="token">Select Token: </label>
        <select
            id="token"
            value={selectedToken}
            onChange={(e) => setSelectedToken(e.target.value)}
        >
            <option value="CUSTOM">Custom Token</option>
            {Object.keys(TOKENS).map((key) => (
            <option key={key} value={key}>
                {TOKENS[key].name} ({TOKENS[key].symbol})
            </option>
            ))}
        </select>
    </div>
    {selectedToken === "CUSTOM" && (
        <div className="custom-token">
            <h3>🔍 Check Any ERC-20 Token</h3>
            <input
            type="text"
            placeholder="Paste token contract address"
            value={customTokenAddress}
            onChange={(e) => setCustomTokenAddress(e.target.value)}
            />
            <button onClick={() => fetchCustomTokenInfo(customTokenAddress)}>
            Fetch Token Info
            </button>

            {customTokenInfo && (
            <div className="token-info">
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

        {tab === "eth" ? (
        <SendEth account={account} />
        ) : (
        <SendToken selectedToken={selectedToken} TOKENS={TOKENS} account={account} />
        )}
    </div>
    );
}

export default App;
