from web3 import Web3
import os
from dotenv import load_dotenv
import json
load_dotenv()
# Connect to Ethereum node (Infura, Alchemy, etc.)
INFURA_API_KEY = os.getenv("REACT_APP_INFURA_PROJECT_URL")
w3 = Web3(Web3.HTTPProvider(INFURA_API_KEY))

contract_address = os.getenv("REACT_APP_ETH_CONTRACT_ADDRESS")
abi = []
with open("frontend/src/abi/FraudLog.json") as f:
    abi = json.load(f)

contract = w3.eth.contract(address=contract_address, abi=abi)

# Fetch all FraudLogged events
events = contract.events.FraudLogged.create_filter(from_block=0).get_all_entries()
c=1
for event in events:
    print("Log: ", c)
    print("Sender:", event.args.sender)
    print("Receiver:", event.args.receiver)
    print("Amount:", event.args.amount)
    print("Timestamp:", event.args.timestamp)
    c+=1