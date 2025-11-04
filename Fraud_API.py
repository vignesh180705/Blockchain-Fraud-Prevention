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

with open("ABI.json") as f:
    abi = json.load(f)

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

model = joblib.load("model/fraud_model.pkl")

app = Flask(__name__)

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    features = pd.DataFrame([data["features"]])
    sender = data["sender"]
    receiver = data["receiver"]
    amount = float(data["amount"])
    currency = data.get("currency", "ETH")  # default ETH
    is_token = data.get("is_token", False)
    features = pd.DataFrame([data["features"]])
    best_threshold = 0.3089379
    fraud_prob = float(model.predict_proba(features)[:, 1][0])
    is_fraud = int(fraud_prob >= best_threshold)
    tx_hash = None
    nonce = w3.eth.get_transaction_count(account.address)
    if is_fraud:
        print("Fraud detected! Blocking transaction.")
        # Log only fraudulent attempt on blockchain
        tx = contract.functions.logFraudAttempt(
            sender,
            receiver,
            int(amount),
            currency,
            is_token
        ).build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gas': 200000,
            'gasPrice': w3.to_wei('20', 'gwei')
        })
        signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    else:
        print("Legitimate transaction, proceeding with transfer...")
        tx = {
            'from': data["sender"],
            'to': data["receiver"],
            'value': w3.to_wei(int(data["amount"]), 'wei'),
            'gas': 21000,
            'gasPrice': w3.to_wei('20', 'gwei'),
            'nonce': nonce
        }
        signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print("Transaction hash:", tx_hash.hex())
    status = "rejected" if is_fraud else "accepted"
    return jsonify({
        "status": status,
        "fraud_prob": fraud_prob,
        "tx_hash": tx_hash.hex()
    }), (400 if is_fraud else 200)


if __name__ == "__main__":
    app.run(debug=True)
