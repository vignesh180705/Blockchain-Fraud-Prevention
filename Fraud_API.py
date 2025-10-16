from flask import Flask, request, jsonify
import joblib
import os
from dotenv import load_dotenv
from web3 import Web3
import json

load_dotenv()
RPC_URL = os.getenv("RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)

# Load contract ABI (save ABI in fraud_registry_abi.json)
with open("ABI.json") as f:
    abi = json.load(f)

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

# Load ML model
model = joblib.load("model/fraud_model.pkl")

# Initialize Flask
app = Flask(__name__)

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    sender = data["sender"]
    receiver = data["receiver"]
    amount = data["amount"]
    features = data["features"]

    # Predict fraud
    is_fraud = int(model.predict([features])[0])

    tx_hash = None
    if is_fraud == 1:
        tx = contract.functions.logTransaction(
            sender,
            receiver,
            int(amount),
            True
        ).build_transaction({
            'from': account.address,
            'gas': 3000000,
            'nonce': w3.eth.get_transaction_count(account.address)
        })
        signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction).hex()

    return jsonify({"is_fraud": bool(is_fraud), "tx_hash": tx_hash})

if __name__ == "__main__":
    app.run(debug=True)
