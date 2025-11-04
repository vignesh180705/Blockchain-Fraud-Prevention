from web3 import Web3
import time
from collections import defaultdict
import os
from dotenv import load_dotenv
import statistics
load_dotenv()
RPC_URL = os.getenv("RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

w3= Web3(Web3.HTTPProvider(RPC_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)
address = account.address

def get_erc20_features(w3, account_address):
    transfer_sig = w3.keccak(text="Transfer(address,address,uint256)").hex()
    latest_block = w3.eth.block_number
    logs = []
    for block_num in range(0, latest_block + 1):
        block = w3.eth.get_block(block_num, full_transactions=True)
        for tx in block.transactions:
            if tx['to'] is not None:
                try:
                    receipt = w3.eth.get_transaction_receipt(tx['hash'])
                    for log in receipt.logs:
                        if log.topics and log.topics[0].hex() == transfer_sig:
                            logs.append(log)
                except:
                    continue
    sent_txns = []
    rec_txns = []
    sent_token_names = []
    rec_token_names = []
    sent_to_contracts = []
    sent_to_addresses = set()
    rec_from_addresses = set()
    rec_from_contracts = set()

    for log in logs:
        token_contract = w3.eth.contract(address=log.address, abi=[
            {
                "constant": True,
                "inputs": [],
                "name": "name",
                "outputs": [{"name": "", "type": "string"}],
                "type": "function"
            }
        ])
        try:
            token_name = token_contract.functions.name().call()
        except:
            token_name = "Unknown"

        from_addr = '0x' + log.topics[1].hex()[-40:]
        to_addr = '0x' + log.topics[2].hex()[-40:]
        value = int(log.data, 16)
        value_eth = w3.from_wei(value, 'ether')

        # classify transactions
        if from_addr.lower() == account_address.lower():
            sent_txns.append((to_addr, value_eth, token_name))
            sent_token_names.append(token_name)
            if w3.eth.get_code(to_addr) != b'':
                sent_to_contracts.append((to_addr, value_eth))
            else:
                sent_to_addresses.add(to_addr)
        elif to_addr.lower() == account_address.lower():
            rec_txns.append((from_addr, value_eth, token_name))
            rec_token_names.append(token_name)
            if w3.eth.get_code(from_addr) != b'':
                rec_from_contracts.add(from_addr)
            else:
                rec_from_addresses.add(from_addr)

    # helper: get min, max, avg values
    def value_stats(txns):
        if not txns:
            return 0, 0, 0
        vals = [t[1] for t in txns]
        return min(vals), max(vals), sum(vals)/len(vals)

    # helper: get average minutes between txns

    min_val_rec, max_val_rec, avg_val_rec = value_stats(rec_txns)
    min_val_sent, max_val_sent, avg_val_sent = value_stats(sent_txns)

    # build feature dict (exactly 18)
    features = {
        'Total ERC20 tnxs': len(sent_txns) + len(rec_txns),
        'ERC20 total Ether received': sum([t[1] for t in rec_txns]),
        'ERC20 total ether sent': sum([t[1] for t in sent_txns]),
        'ERC20 total Ether sent contract': sum([t[1] for t in sent_to_contracts]),
        'ERC20 uniq sent addr': len(sent_to_addresses),
        'ERC20 uniq rec addr': len(rec_from_addresses),
        'ERC20 uniq sent addr.1': len(sent_to_contracts),
        'ERC20 uniq rec contract addr': len(rec_from_contracts),
        'ERC20 min val rec': min_val_rec,
        'ERC20 max val rec': max_val_rec,
        'ERC20 avg val rec': avg_val_rec,
        'ERC20 min val sent': min_val_sent,
        'ERC20 max val sent': max_val_sent,
        'ERC20 avg val sent': avg_val_sent,
        'ERC20 uniq sent token name': len(set(sent_token_names)),
        'ERC20 uniq rec token name': len(set(rec_token_names)),
        'ERC20 most sent token type': max(set(sent_token_names), key=sent_token_names.count, default='None'),
        'ERC20_most_rec_token_type': max(set(rec_token_names), key=rec_token_names.count, default='None')
    }

    return features

def get_eth_features(w3, account_address):
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

    def avg_min_between_txns(txns):
        if len(txns) < 2:
            return 0
        timestamps = [w3.eth.get_block(tx.blockNumber)['timestamp'] for tx in txns]
        timestamps.sort()
        diffs = [timestamps[i+1]-timestamps[i] for i in range(len(timestamps)-1)]
        avg_diff_sec = sum(diffs)/len(diffs)
        return avg_diff_sec / 60

    avg_min_sent = avg_min_between_txns(txns_sent)
    avg_min_received = avg_min_between_txns(txns_received)

    first_ts = min([w3.eth.get_block(tx.blockNumber)['timestamp'] for tx in txns_sent + txns_received], default=0)
    last_ts = max([w3.eth.get_block(tx.blockNumber)['timestamp'] for tx in txns_sent + txns_received], default=0)
    time_diff_mins = (last_ts - first_ts) / 60 if last_ts > first_ts else 0

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
    features = get_eth_features(w3, account_address)
    #features.update({'Total ERC20 tnxs': 0.0, 'ERC20 total Ether received': 0.0, 'ERC20 total ether sent': 0.0, 'ERC20 total Ether sent contract': 0.0, 'ERC20 uniq sent addr': 0.0, 'ERC20 uniq rec addr': 0.0, 'ERC20 uniq sent addr.1': 0.0, 'ERC20 uniq rec contract addr': 0.0, 'ERC20 min val rec': 0.0, 'ERC20 max val rec': 0.0, 'ERC20 avg val rec': 0.0, 'ERC20 min val sent': 0.0, 'ERC20 max val sent': 0.0, 'ERC20 avg val sent': 0.0, 'ERC20 uniq sent token name': 0.0, 'ERC20 uniq rec token name': 0.0, 'ERC20 most sent token type': '0', 'ERC20_most_rec_token_type': '0'})
    features.update(get_erc20_features(w3, account_address))
    return features


print(extract_features(Web3(Web3.HTTPProvider("http://127.0.0.1:7545")), address))