from web3 import Web3
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

RPC_URL = os.getenv("RPC_URL", "http://127.0.0.1:7545")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

# Connect to blockchain (Ganache or given RPC)
w3 = Web3(Web3.HTTPProvider(RPC_URL))
print("Connected:", w3.is_connected())

# Load contract ABI
with open("ABI.json") as f:
    abi = json.load(f)

# Load deployed contract
contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

# Fetch all FraudLogged events
fraud_filter = contract.events.FraudLogged.create_filter(from_block=0)
events = fraud_filter.get_all_entries()

print("\n=== Transaction Logs ===")
if len(events) == 0:
    print("No FraudLogged events found.")
else:
    for e in events:
        args = e["args"]
        print(f"Sender:    {args['sender']}")
        print(f"Receiver:  {args['receiver']}")
        print(f"Amount:    {args['amount']}")
        print(f"Timestamp: {args['timestamp']}")
        print("-" * 40)
