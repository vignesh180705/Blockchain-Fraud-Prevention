# features.py
from web3 import Web3
import time
from collections import defaultdict

def get_eth_features(w3: Web3, account_address: str):
    """
    Extract ETH transaction features for a given account.
    """
    txns_sent = []
    txns_received = []
    contracts_created = 0
    unique_sent_to = set()
    unique_received_from = set()
    total_ether_sent = 0
    total_ether_received = 0

    latest_block = w3.eth.block_number
    for block_num in range(0, latest_block + 1):
        block = w3.eth.get_block(block_num, full_transactions=True)
        for tx in block.transactions:
            if tx['from'].lower() == account_address.lower():
                txns_sent.append(tx)
                unique_sent_to.add(tx['to'])
                total_ether_sent += w3.from_wei(tx['value'], 'ether')
                if tx['to'] is None:
                    contracts_created += 1
            if tx['to'] and tx['to'].lower() == account_address.lower():
                txns_received.append(tx)
                unique_received_from.add(tx['from'])
                total_ether_received += w3.from_wei(tx['value'], 'ether')

    # Time-based calculations
    def avg_min_between_txns(txns):
        if len(txns) < 2:
            return 0
        timestamps = [w3.eth.get_block(tx.blockNumber)['timestamp'] for tx in txns]
        timestamps.sort()
        diffs = [timestamps[i+1]-timestamps[i] for i in range(len(timestamps)-1)]
        avg_diff_sec = sum(diffs)/len(diffs)
        return avg_diff_sec / 60  # convert to minutes

    avg_min_sent = avg_min_between_txns(txns_sent)
    avg_min_received = avg_min_between_txns(txns_received)

    first_ts = min([w3.eth.get_block(tx.blockNumber)['timestamp'] for tx in txns_sent + txns_received], default=0)
    last_ts = max([w3.eth.get_block(tx.blockNumber)['timestamp'] for tx in txns_sent + txns_received], default=0)
    time_diff_mins = (last_ts - first_ts) / 60 if last_ts > first_ts else 0

    # Values
    def tx_values(txns):
        if not txns:
            return 0,0,0
        values = [w3.from_wei(tx['value'], 'ether') for tx in txns]
        return min(values), max(values), sum(values)/len(values)

    min_received, max_received, avg_received = tx_values(txns_received)
    min_sent, max_sent, avg_sent = tx_values(txns_sent)
    sent_to_contract = [w3.from_wei(tx['value'], 'ether') for tx in txns_sent if tx['to'] is None]
    min_contract = min(sent_to_contract) if sent_to_contract else 0
    max_contract = max(sent_to_contract) if sent_to_contract else 0
    avg_contract = sum(sent_to_contract)/len(sent_to_contract) if sent_to_contract else 0
    balance = w3.from_wei(w3.eth.get_balance(account_address), 'ether')

    features = {
        'Avg min between sent tnx': avg_min_sent,
        'Avg min between received tnx': avg_min_received,
        'Time Diff between first and last (Mins)': time_diff_mins,
        'Sent tnx': len(txns_sent),
        'Received Tnx': len(txns_received),
        'Number of Created Contracts': contracts_created,
        'Unique Received From Addresses': len(unique_received_from),
        'Unique Sent To Addresses': len(unique_sent_to),
        'min value received': min_received,
        'max value received ': max_received,
        'avg val received': avg_received,
        'min val sent': min_sent,
        'max val sent': max_sent,
        'avg val sent': avg_sent,
        'min value sent to contract': min_contract,
        'max val sent to contract': max_contract,
        'avg value sent to contract': avg_contract,
        'total ether sent contracts': sum(sent_to_contract),
        'total transactions (including tnx to create contract': len(txns_sent + txns_received),
        'total Ether sent': total_ether_sent,
        'total ether received': total_ether_received,
        'total ether balance': balance
    }
    return features





def extract_features(w3: Web3, account_address: str):
    """
    Extract both ETH and ERC20 features for an account.
    erc20_contracts: list of dicts [{'address':..., 'abi':...}]
    """
    features = get_eth_features(w3, account_address)
    features.update({'Total ERC20 tnxs': 0.0, 'ERC20 total Ether received': 0.0, 'ERC20 total ether sent': 0.0, 'ERC20 total Ether sent contract': 0.0, 'ERC20 uniq sent addr': 0.0, 'ERC20 uniq rec addr': 0.0, 'ERC20 uniq sent addr.1': 0.0, 'ERC20 uniq rec contract addr': 0.0, 'ERC20 min val rec': 0.0, 'ERC20 max val rec': 0.0, 'ERC20 avg val rec': 0.0, 'ERC20 min val sent': 0.0, 'ERC20 max val sent': 0.0, 'ERC20 avg val sent': 0.0, 'ERC20 uniq sent token name': 0.0, 'ERC20 uniq rec token name': 0.0, 'ERC20 most sent token type': '0', 'ERC20_most_rec_token_type': '0'})
    return features


print(extract_features(Web3(Web3.HTTPProvider("http://127.0.0.1:7545")),"0x93d75E1991b0cea056c2f6633E9E3F4e45295844"))