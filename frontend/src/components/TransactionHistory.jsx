import React, { useEffect, useState } from "react";
import { ethers } from "ethers";

const API_KEY = process.env.REACT_APP_ETHERSCAN_API_KEY;
const getTransactions = async (address) => {
    const response = await fetch(
        `https://api.etherscan.io/v2/api?chainid=11155111&module=account&action=txlist&address=${address}&startblock=0&endblock=99999999&page=1&offset=20&sort=desc&apikey=${API_KEY}`
    );
    const data = await response.json();
    return data.result; // array of transactions
};

export default function TransactionHistory({ account }) {
    const [txs, setTxs] = useState([]);

    useEffect(() => {
        if (!account) return;
        getTransactions(account).then(setTxs);
    }, [account]);

    return (
        <div>
            <h2>Transaction History</h2>
            <table>
                <thead>
                    <tr>
                        <th>Hash</th>
                        <th>From</th>
                        <th>To</th>
                        <th>Value (ETH)</th>
                    </tr>
                </thead>
                <tbody>
                    {txs.map((tx) => (
                        <tr key={tx.hash}>
                            <td>
                              <a
                                href={`https://sepolia.etherscan.io/tx/${tx.hash}`}
                                target="_blank"
                                rel="noopener noreferrer"
                              >
                                {tx.hash.slice(0, 10)}...
                              </a>
                            </td>
                            <td>{tx.from}</td>
                            <td>{tx.to}</td>
                            <td>{ethers.formatEther(tx.value)}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
