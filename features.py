from web3 import Web3
from datetime import datetime

# Connect to local blockchain (Ganache)
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

def get_all_txs(address, start_block=0, end_block=None):
    """Get all transactions involving the address."""
    if end_block is None:
        end_block = w3.eth.block_number
    sent = []
    received = []
    created_contracts = 0

    for block_num in range(start_block, end_block + 1):
        block = w3.eth.get_block(block_num, full_transactions=True)
        for tx in block.transactions:
            tx_from = tx['from'].lower()
            tx_to = tx['to'].lower() if tx['to'] else None
            if tx_from == address.lower():
                sent.append(tx)
                if tx_to is None:
                    created_contracts += 1
            elif tx_to == address.lower():
                received.append(tx)

    return sent, received, created_contracts

def compute_time_features(sent, received):
    """Compute average minutes between sent/received and overall time diff."""
    def avg_min_between(txs):
        if len(txs) < 2:
            return 0
        timestamps = [w3.eth.get_block(tx.blockNumber).timestamp for tx in txs]
        timestamps.sort()
        diffs = [(timestamps[i+1] - timestamps[i])/60 for i in range(len(timestamps)-1)]
        return sum(diffs)/len(diffs)

    all_times = [w3.eth.get_block(tx.blockNumber).timestamp for tx in sent+received]
    all_times.sort()
    time_diff_mins = (all_times[-1] - all_times[0])/60 if all_times else 0

    return {
        "Avg min between sent tnx": avg_min_between(sent),
        "Avg min between received tnx": avg_min_between(received),
        "Time Diff between first and last (Mins)": time_diff_mins
    }

def compute_tx_counts(sent, received, created_contracts):
    """Compute counts of transactions and unique addresses."""
    unique_sent_to = len(set(tx['to'] for tx in sent if tx['to']))
    unique_received_from = len(set(tx['from'] for tx in received))

    return {
        "Sent tnx": len(sent),
        "Received Tnx": len(received),
        "Number of Created Contracts": created_contracts,
        "Unique Received From Addresses": unique_received_from,
        "Unique Sent To Addresses": unique_sent_to
    }

def compute_value_features(address, sent, received):
    """Compute min, max, and avg of ETH sent and received."""
    def calc_stats(txs, key):
        if not txs:
            return 0, 0, 0
        values = [w3.from_wei(tx[key], 'ether') for tx in txs]
        return min(values), max(values), sum(values)/len(values)

    min_rec, max_rec, avg_rec = calc_stats(received, 'value')
    min_sent, max_sent, avg_sent = calc_stats(sent, 'value')

    sent_to_contract = [w3.from_wei(tx['value'], 'ether') for tx in sent if tx['to'] is None]
    min_contract = min(sent_to_contract) if sent_to_contract else 0
    max_contract = max(sent_to_contract) if sent_to_contract else 0
    avg_contract = sum(sent_to_contract)/len(sent_to_contract) if sent_to_contract else 0

    total_sent = sum([w3.from_wei(tx['value'], 'ether') for tx in sent])
    total_received = sum([w3.from_wei(tx['value'], 'ether') for tx in received])
    total_balance = w3.from_wei(w3.eth.get_balance(address), 'ether')


    return {
        "min value received": min_rec,
        "max value received ": max_rec,
        "avg val received": avg_rec,
        "min val sent": min_sent,
        "max val sent": max_sent,
        "avg val sent": avg_sent,
        "min value sent to contract": min_contract,
        "max val sent to contract": max_contract,
        "avg value sent to contract": avg_contract,
        "total transactions (including tnx to create contract": len(sent)+len(received),
        "total Ether sent": total_sent,
        "total ether received": total_received,
        "total ether sent contracts": sum(sent_to_contract),
        "total ether balance": total_balance
    }

def extract_features(address, start_block=0, end_block=None):
    sent, received, created_contracts = get_all_txs(address, start_block, end_block)
    features = {}
    features.update(compute_time_features(sent, received))
    features.update(compute_tx_counts(sent, received, created_contracts))
    features.update(compute_value_features(address, sent, received))
    return features

print(extract_features("0x826ACF55EBd27E9Df4020123C783f91f0585e1F9"))