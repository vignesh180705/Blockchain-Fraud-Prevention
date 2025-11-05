import requests
from dotenv import load_dotenv
import os
from web3 import Web3
from features import extract_features
import decimal

load_dotenv()

RPC_URL = os.getenv("RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# Example ERC20 token address (use your deployed one)
TOKEN_CONTRACT = "0xYourERC20TokenAddressHere"

def convert_decimals(obj):
    if isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals(v) for v in obj]
    elif isinstance(obj, decimal.Decimal):
        return float(obj)
    else:
        return obj

account = w3.eth.account.from_key(PRIVATE_KEY)

# Extract blockchain features dynamically
features = extract_features(w3, account.address)
features = convert_decimals(features)

payload = {
    "sender": account.address,
    "receiver": "0x4CD7047fA3DEB1fA584B9d72FAD321EEd6ebA54e",  # example receiver
    "amount": 10,
    "is_token": True,  # set False for ETH
    "token_address": TOKEN_CONTRACT,
    "features": features
}

r = requests.post("http://127.0.0.1:5000/predict", json=payload)
print(r.status_code, r.json())
