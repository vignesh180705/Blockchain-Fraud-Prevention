// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";

contract FraudRegistry is Ownable {
    struct FraudRecord {
        address sender;
        address receiver;
        uint256 amount;
        uint256 timestamp;
    }

    FraudRecord[] private records;

    event FraudLogged(
        address indexed sender,
        address indexed receiver,
        uint256 amount,
        uint256 timestamp
    );

    constructor() Ownable() {}

    function logFraudAttempt(
        address _sender,
        address _receiver,
        uint256 _amount
    ) external onlyOwner {
        require(_sender != address(0) && _receiver != address(0), "Invalid address");
        require(_amount > 0, "Invalid amount");

        records.push(FraudRecord(_sender, _receiver, _amount, block.timestamp));
        emit FraudLogged(_sender, _receiver, _amount, block.timestamp);
    }

    function getRecord(uint256 index)
        external
        view
        returns (address, address, uint256, uint256)
    {
        require(index < records.length, "Invalid index");
        FraudRecord memory r = records[index];
        return (r.sender, r.receiver, r.amount, r.timestamp);
    }

    function totalRecords() external view returns (uint256) {
        return records.length;
    }

    function clearRecords() external onlyOwner {
        delete records;
    }
}
