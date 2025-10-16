from flask import Flask, request, jsonify, make_response
import joblib
import os
from dotenv import load_dotenv
from web3 import Web3
import json
import pandas as pd
from features import extract_features
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
    features = pd.DataFrame([data["features"]])

    # Fraud detection
    best_threshold = 0.3089379
    fraud_prob = float(model.predict_proba(features)[:, 1][0])  # convert to Python float
    is_fraud = int(fraud_prob >= best_threshold)
    tx_hash = None
    tx = contract.functions.logTransaction(
        sender,
        receiver,
        int(amount),
        bool(is_fraud)
    ).build_transaction({
        'from': account.address,
        'nonce': w3.eth.get_transaction_count(account.address),
        'gas': 200000,
        'gasPrice': w3.to_wei('20', 'gwei')
    })

    # Sign & send
    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction).hex()
    print("Transaction mined:", tx_hash)
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    events = contract.events.TransactionLogged().process_receipt(tx_receipt)
    print(events)
    # Return response
    status = "rejected" if is_fraud else "accepted"
    return jsonify({
        "status": status,
        "fraud_prob": fraud_prob,
        "tx_hash": tx_hash
    }), (400 if is_fraud else 200)


if __name__ == "__main__":
    app.run(debug=True)
