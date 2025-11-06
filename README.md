# Ethereum & ERC-20 Fraud Detection Dashboard

## About
This project detects and prevents fraudulent transactions on the **Ethereum blockchain**, analyzing both **ETH** and **ERC-20 token** activity.  
It integrates:
- **MetaMask** — for wallet connection and signing transactions  
- **Infura** — as the blockchain RPC provider  
- **Etherscan APIs** — for transaction data  
- **Flask (Python)** — for backend ML fraud detection  
- **React.js (JavaScript)** — for the user interface  

By combining on-chain wallet behavior and machine learning predictions, this system aims to provide **real-time fraud prevention** for both ETH and token-based transactions.

---

## Features
- **Connect Wallet** via MetaMask  
- **Send ETH or ERC-20 Tokens** securely  
- **Machine Learning Fraud Detection** using Flask API  
- **Wallet Analytics Dashboard** (transaction stats, unique addresses, averages)  
- **Transaction History Viewer** with Etherscan links  
- **ERC-20 Token Integration** (custom or predefined tokens)

---

## 🧩 Tech Stack

### **Frontend**
- React.js  
- Ethers.js  
- Custom CSS  

### **Backend**
- Python (Flask)  
- Scikit-learn / XGBoost / Pandas / NumPy  

### **Blockchain**
- Ethereum (Sepolia Testnet)  
- Infura (RPC endpoint)  
- Etherscan API  
