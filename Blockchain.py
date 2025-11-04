# blockchain_client.py
import requests
from dotenv import load_dotenv
load_dotenv()
import os
from web3 import Web3
RPC_URL = os.getenv("RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
from features import extract_features
w3 = Web3(Web3.HTTPProvider(RPC_URL))
import decimal

fraud_features = {'Avg min between sent tnx': 1641.74, 'Avg min between received tnx': 2103.12, 'Time Diff between first and last (Mins)': 327679.35, 'Sent tnx': 10, 'Received Tnx': 148, 'Number of Created Contracts': 0, 'Unique Received From Addresses': 137, 'Unique Sent To Addresses': 4, 'min value received': 0.001, 'max value received ': 14.341, 'avg val received': 1.429861, 'min val sent': 0.022257, 'max val sent': 70.0, 'avg val sent': 21.161505, 'min value sent to contract': 0.0, 'max val sent to contract': 0.0, 'avg value sent to contract': 0.0, 'total transactions (including tnx to create contract': 158, 'total Ether sent': 211.6150523, 'total ether received': 211.6193783, 'total ether sent contracts': 0.0, 'total ether balance': 0.004326, 'Total ERC20 tnxs': 5.0, 'ERC20 total Ether received': 2095.638173, 'ERC20 total ether sent': 0.0, 'ERC20 total Ether sent contract': 0.0, 'ERC20 uniq sent addr': 0.0, 'ERC20 uniq rec addr': 4.0, 'ERC20 uniq sent addr.1': 0.0, 'ERC20 uniq rec contract addr': 5.0, 'ERC20 min val rec': 0.0, 'ERC20 max val rec': 2082.268173, 'ERC20 avg val rec': 419.127635, 'ERC20 min val sent': 0.0, 'ERC20 max val sent': 0.0, 'ERC20 avg val sent': 0.0, 'ERC20 uniq sent token name': 0.0, 'ERC20 uniq rec token name': 5.0, 'ERC20 most sent token type': ' ', 'ERC20_most_rec_token_type': 'Genaro X'}


def convert_decimals(obj):
    if isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals(v) for v in obj]
    elif isinstance(obj, (decimal.Decimal,)):
        return float(obj)
    else:
        return obj

account = w3.eth.account.from_key(PRIVATE_KEY)
features = extract_features(w3, account.address)
payload = {
  "sender": account.address,
  "receiver": "0x4CD7047fA3DEB1fA584B9d72FAD321EEd6ebA54e",
  "amount": 300,
  "currency": "USDX",
  "is_token": True,
  "features": convert_decimals(features)
}
r = requests.post("http://127.0.0.1:5000/predict", json=payload)
print(r.json())