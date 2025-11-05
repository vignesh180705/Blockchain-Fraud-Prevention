from flask import Flask, request, jsonify
import joblib
import os
from dotenv import load_dotenv
from web3 import Web3
import json
import pandas as pd
from features import extract_features  # Your existing feature extractor
from decimal import Decimal
load_dotenv()

RPC_URL = os.getenv("REACT_APP_INFURA_PROJECT_URL")
PRIVATE_KEY = os.getenv("REACT_APP_PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("REACT_APP_ETH_CONTRACT_ADDRESS")

# Initialize Web3
w3 = Web3(Web3.HTTPProvider(RPC_URL))
account = w3.eth.account.from_key(PRIVATE_KEY)

# Load FraudRegistry ABI
with open("frontend/src/abi/ERC20.json") as f:
    abi = json.load(f)

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

# Load ML model
model = joblib.load("model/fraud_model.pkl")

app = Flask(__name__)

def convert_decimals(obj):
    if isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals(v) for v in obj]
    elif isinstance(obj, Decimal):
        return float(obj)
    else:
        return obj

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        sender = data.get("sender")
        receiver = data.get("receiver")
        amount = float(data.get("amount"))
        token = data.get("token")
        tokenAddress = data.get("tokenAddress")

        if not sender or not receiver or not amount:
            return jsonify({"error": "Missing fields"}), 400

        # ---- Extract blockchain-based features ----
        features = extract_features(w3, sender)
        features = convert_decimals(features)

        # ---- Model Prediction ----
        # Convert dict → feature vector
        X = [list(features.values())]
        prediction = model.predict(X)[0]

        label = "fraudulent" if prediction == 1 else "legit"

        return jsonify({
            "prediction": label,
            "sender": sender,
            "receiver": receiver,
            "amount": amount,
            "token": token,
            "features_used": list(features.keys())
        })

    except Exception as e:
        print("Prediction error:", e)
        return jsonify({"error": str(e)}), 500


# ===== Log Fraudulent Transaction =====
@app.route("/logFraud", methods=["POST"])
def log_fraud():
    try:
        data = request.get_json()
        sender = data["sender"]
        receiver = data["receiver"]
        amount = data["amount"]
        token = data["token"]

        nonce = w3.eth.get_transaction_count(account.address)
        tx = contract.functions.logFraud(
            sender, receiver, str(amount), token
        ).build_transaction({
            "from": account.address,
            "nonce": nonce,
            "gas": 300000,
            "gasPrice": w3.eth.gas_price
        })

        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

        return jsonify({
            "status": "logged",
            "tx_hash": tx_hash.hex()
        })

    except Exception as e:
        print("Log error:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)

if __name__ == "__main__":
    app.run(debug=True)
