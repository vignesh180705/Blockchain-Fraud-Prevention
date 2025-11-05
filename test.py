from etherscan import Etherscan
import os

API_KEY = os.getenv("REACT_APP_ETHERSCAN_API_KEY")
ADDRESS = os.getenv("REACT_APP_ETHERSCAN_ACCOUNT_ADDRESS")

eth = Etherscan(API_KEY)  # handles V2 automatically
print(eth.get_eth_balance(ADDRESS))
'''balance = eth.get_eth_balance(ADDRESS, chainid=11155111)
txlist = eth.get_normal_txs_by_address(ADDRESS, startblock=0, endblock=99999999, sort="asc", chain_id=11155111)

print("Balance:", int(balance)/1e18)
print("Transactions:", len(txlist))'''
params = {
        "chainid": 11155111,
        "module": "account",
        "action": "txlist",
        "address": ADDRESS,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "asc",
        "apikey": API_KEY
    }