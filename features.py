import os
import requests
from dotenv import load_dotenv
from statistics import mean

load_dotenv()

API_KEY = os.getenv("REACT_APP_ETHERSCAN_API_KEY")
ADDRESS = os.getenv("REACT_APP_ETHERSCAN_ACCOUNT_ADDRESS")
ETHERSCAN_API = "https://api.etherscan.io/v2/api"

def fetch_txs(address, action="txlist"):
    params = {
        "chainid": 11155111,
        "module": "account",
        "action": action,
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "asc",
        "apikey": API_KEY
    }
    resp = requests.get(ETHERSCAN_API, params=params, timeout=30)
    #print(resp.status_code,resp.text)
    data = resp.json()
    if data["status"] != "1":
        print(f"Warning: {data.get('message')}")
        return []
    return data["result"]


def value_stats(txns, value_field="value", decimals=18):
    if not txns:
        return 0, 0, 0
    vals = [int(tx[value_field]) / (10 ** decimals) for tx in txns]
    return min(vals), max(vals), mean(vals)

def avg_min_between_txns(txns):
    if len(txns) < 2:
        return 0
    timestamps = [int(tx["timeStamp"]) for tx in txns]
    timestamps.sort()
    diffs = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
    return mean(diffs) / 60

def extract_features(address):
    eth_txs = fetch_txs(address, action="txlist")
    erc20_txs = fetch_txs(address, action="tokentx")

    sent_txs = [tx for tx in eth_txs if tx["from"].lower() == address.lower()]
    received_txs = [tx for tx in eth_txs if tx["to"] and tx["to"].lower() == address.lower()]

    total_ether_sent = sum(int(tx["value"])/1e18 for tx in sent_txs)
    total_ether_received = sum(int(tx["value"])/1e18 for tx in received_txs)

    min_val_sent, max_val_sent, avg_val_sent = value_stats(sent_txs)
    min_val_rec, max_val_rec, avg_val_rec = value_stats(received_txs)
    avg_min_sent = avg_min_between_txns(sent_txs)
    avg_min_received = avg_min_between_txns(received_txs)

    all_txs = sent_txs + received_txs
    if all_txs:
        timestamps = [int(tx["timeStamp"]) for tx in all_txs]
        time_diff_mins = (max(timestamps) - min(timestamps)) / 60
    else:
        time_diff_mins = 0

    uniq_sent_to = len(set(tx["to"].lower() for tx in sent_txs if tx["to"]))
    uniq_received_from = len(set(tx["from"].lower() for tx in received_txs))

    contracts_created = sum(1 for tx in sent_txs if not tx["to"])

    sent_erc20 = [tx for tx in erc20_txs if tx["from"].lower() == address.lower()]
    rec_erc20 = [tx for tx in erc20_txs if tx["to"].lower() == address.lower()]

    min_val_sent_erc, max_val_sent_erc, avg_val_sent_erc = value_stats(sent_erc20)
    min_val_rec_erc, max_val_rec_erc, avg_val_rec_erc = value_stats(rec_erc20)

    uniq_sent_token_name = len(set(tx["tokenName"] for tx in sent_erc20))
    uniq_rec_token_name = len(set(tx["tokenName"] for tx in rec_erc20))

    most_sent_token_type = max(set(tx["tokenName"] for tx in sent_erc20),
                               key=lambda t: sum(1 for tx in sent_erc20 if tx["tokenName"] == t),
                               default="None")
    most_rec_token_type = max(set(tx["tokenName"] for tx in rec_erc20),
                              key=lambda t: sum(1 for tx in rec_erc20 if tx["tokenName"] == t),
                              default="None")

    params = {
        "chainid": 11155111,
        "module": "account",
        "action": "balance",
        "address": address,
        "tag": "latest",
        "apikey": API_KEY
    }
    resp = requests.get(ETHERSCAN_API, params=params, timeout=30)
    total_ether_balance = int(resp.json().get("result", 0)) / 1e18

    features = {
        'Avg min between sent tnx': avg_min_sent,
        'Avg min between received tnx': avg_min_received,
        'Time Diff between first and last (Mins)': time_diff_mins,
        'Sent tnx': len(sent_txs),
        'Received Tnx': len(received_txs),
        'Number of Created Contracts': contracts_created,
        'Unique Received From Addresses': uniq_received_from,
        'Unique Sent To Addresses': uniq_sent_to,
        'min value received': min_val_rec,
        'max value received ': max_val_rec,
        'avg val received': avg_val_rec,
        'min val sent': min_val_sent,
        'max val sent': max_val_sent,
        'avg val sent': avg_val_sent,
        'min value sent to contract': 0,  
        'max val sent to contract': 0,
        'avg value sent to contract': 0,
        'total ether sent contracts': 0,
        'total transactions (including tnx to create contract': len(all_txs),
        'total Ether sent': total_ether_sent,
        'total ether received': total_ether_received,
        'total ether balance': total_ether_balance,

        'Total ERC20 tnxs': len(sent_erc20) + len(rec_erc20),
        'ERC20 total Ether received': sum(int(tx["value"])/1e18 for tx in rec_erc20),
        'ERC20 total ether sent': sum(int(tx["value"])/1e18 for tx in sent_erc20),
        'ERC20 total Ether sent contract': 0, 
        'ERC20 uniq sent addr': len(set(tx["to"].lower() for tx in sent_erc20)),
        'ERC20 uniq rec addr': len(set(tx["from"].lower() for tx in rec_erc20)),
        'ERC20 uniq sent addr.1': 0, 
        'ERC20 uniq rec contract addr': 0, 
        'ERC20 min val rec': min_val_rec_erc,
        'ERC20 max val rec': max_val_rec_erc,
        'ERC20 avg val rec': avg_val_rec_erc,
        'ERC20 min val sent': min_val_sent_erc,
        'ERC20 max val sent': max_val_sent_erc,
        'ERC20 avg val sent': avg_val_sent_erc,
        'ERC20 uniq sent token name': uniq_sent_token_name,
        'ERC20 uniq rec token name': uniq_rec_token_name,
        'ERC20 most sent token type': most_sent_token_type,
        'ERC20_most_rec_token_type': most_rec_token_type
    }

    return features

if __name__ == "__main__":
    feats = extract_features(ADDRESS)
    #for k, v in feats.items():
    #    print(f"{k}: {v}")
