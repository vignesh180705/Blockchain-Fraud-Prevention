// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract FraudRegistry {
    address public owner;

    struct TransactionRecord {
        address sender;
        address receiver;
        uint256 amount;
    }

    TransactionRecord[] private transactions;

    event FraudLogged(
        address indexed sender,
        address indexed receiver,
        uint256 amount,
        uint256 timestamp
    );

    event TransactionsCleared(address indexed by);
    event FundsWithdrawn(address indexed by, uint256 amount);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not contract owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function logFraudAttempt(
        address _sender,
        address _receiver,
        uint256 _amount
    ) external {
        require(_sender != address(0), "Invalid sender");
        require(_receiver != address(0), "Invalid receiver");
        require(_amount > 0, "Amount must be > 0");

        transactions.push(
            TransactionRecord({
                sender: _sender,
                receiver: _receiver,
                amount: _amount
            })
        );

        emit FraudLogged(_sender, _receiver, _amount, block.timestamp);
    }

    function getTransaction(uint256 _index)
        external
        view
        returns (address, address, uint256)
    {
        require(_index < transactions.length, "Invalid index");
        TransactionRecord memory txRecord = transactions[_index];
        return (txRecord.sender, txRecord.receiver, txRecord.amount);
    }

    function totalTransactions() external view returns (uint256) {
        return transactions.length;
    }

    function getContractBalance() external view returns (uint256) {
        return address(this).balance;
    }

    function clearTransactions() external onlyOwner {
        delete transactions;
        emit TransactionsCleared(msg.sender);
    }

    function withdraw() external onlyOwner {
        uint256 amount = address(this).balance;
        require(amount > 0, "No balance to withdraw");
        payable(owner).transfer(amount);
        emit FundsWithdrawn(msg.sender, amount);
    }

    receive() external payable {}
}
