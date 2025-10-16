from web3 import Web3
import json
from dotenv import load_dotenv
import os
# Connect to Ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
print("Connected:", w3.is_connected())

load_dotenv()
RPC_URL = os.getenv("RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
# Load ABI (copy your Remix ABI here)
with open("ABI.json") as f:
    abi = json.load(f)

# Replace with your deployed contract address
contract_address = CONTRACT_ADDRESS
contract = w3.eth.contract(address=contract_address, abi=abi)

# Fetch all events
events = contract.events.TransactionLogged.create_filter(from_block=0).get_all_entries()

print("\n=== Transaction Logs ===")
for e in events:
    args = e['args']
    print(f"Sender: {args['sender']}")
    print(f"Receiver: {args['receiver']}")
    print(f"Amount: {args['amount']}")
    print(f"Is Fraudulent: {args['isFraudulent']}")
    print("-" * 40)
