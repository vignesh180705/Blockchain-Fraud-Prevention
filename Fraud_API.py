from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import os
from dotenv import load_dotenv
from web3 import Web3
import json
import pandas as pd
from features import extract_features  
from decimal import Decimal
import numpy as np
load_dotenv()

RPC_URL = os.getenv("REACT_APP_INFURA_PROJECT_URL")
PRIVATE_KEY = os.getenv("REACT_APP_RELAYER_KEY")
CONTRACT_ADDRESS = os.getenv("REACT_APP_ETH_CONTRACT_ADDRESS")
ETHERSCAN_ADDRESS = os.getenv("REACT_APP_ETHERSCAN_ACCOUNT_ADDRESS")

w3 = Web3(Web3.HTTPProvider(RPC_URL))
balance = w3.eth.get_balance(Web3.to_checksum_address(ETHERSCAN_ADDRESS))
#print(balance)          
print('Balance:',balance / 1e18)
account = w3.eth.account.from_key(PRIVATE_KEY)
feature_names = ['Avg min between sent tnx', 'Avg min between received tnx',
       'Time Diff between first and last (Mins)', 'Sent tnx', 'Received Tnx',
       'Number of Created Contracts', 'Unique Received From Addresses',
       'Unique Sent To Addresses', 'min value received', 'max value received ',
       'avg val received', 'min val sent', 'max val sent', 'avg val sent',
       'min value sent to contract', 'max val sent to contract',
       'avg value sent to contract',
       'total transactions (including tnx to create contract',
       'total Ether sent', 'total ether received',
       'total ether sent contracts', 'total ether balance', 'Total ERC20 tnxs',
       'ERC20 total Ether received', 'ERC20 total ether sent',
       'ERC20 total Ether sent contract', 'ERC20 uniq sent addr',
       'ERC20 uniq rec addr', 'ERC20 uniq sent addr.1',
       'ERC20 uniq rec contract addr', 'ERC20 min val rec',
       'ERC20 max val rec', 'ERC20 avg val rec', 'ERC20 min val sent',
       'ERC20 max val sent', 'ERC20 avg val sent',
       'ERC20 uniq sent token name', 'ERC20 uniq rec token name',
       'ERC20 most sent token type', 'ERC20_most_rec_token_type']

with open("frontend/src/abi/FraudLog.json") as f:
    abi = json.load(f)

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

model = joblib.load("model/fraud_model.pkl")

app = Flask(__name__)
CORS(app)
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
        amount = float(data.get("amount", 0))
        token = data.get("token")  
        tokenAddress = data.get("tokenAddress") 

        if not sender or not receiver or not amount:
            return jsonify({"error": "Missing fields"}), 400

        features = extract_features(sender)  
        if not isinstance(features, dict):
            features = {k: 0 for k in feature_names}

        features = convert_decimals(features)

        if token and tokenAddress:
            erc20_features = {k: v for k, v in features.items() if "ERC20" in k}
            eth_features = {k: v for k, v in features.items() if "ERC20" not in k}
        else:
            erc20_features = {k: 0 for k in feature_names if "ERC20" in k}
            eth_features = {k: v for k, v in features.items() if "ERC20" not in k}

        # convert all NumPy floats in features to native Python floats
        features = {k: float(v) if isinstance(v, (np.float32, np.float64)) else v for k,v in features.items()}
        erc20_features = {k: float(v) if isinstance(v, (np.float32, np.float64)) else v for k,v in erc20_features.items()}
        eth_features = {k: float(v) if isinstance(v, (np.float32, np.float64)) else v for k,v in eth_features.items()}

        # Prediction
        X = pd.DataFrame([features])
        prob = float(model.predict_proba(X)[:, 1][0])  # convert to native float
        fraud_threshold = 0.9
        label = "fraudulent" if prob > fraud_threshold else "legit"

        print('Features:', features)
        print('Fraud Probability:', prob)

        return jsonify({
            "prediction_probability": prob,
            "prediction": label,
            "sender": sender,
            "receiver": receiver,
            "amount": amount,
            "token": token,
            "features_used": list(features.keys()),
            "eth_features": eth_features,
            "erc20_features": erc20_features
        })

    except Exception as e:
        print("Prediction error:", e)
        return jsonify({"error": str(e)}), 500


@app.route("/logFraud", methods=["POST"])
def log_fraud():
    try:
        data = request.get_json()
        sender = data["sender"]
        receiver = data["receiver"]
        amount = data["amount"]
        #token = data["token"]

        nonce = w3.eth.get_transaction_count(account.address)
        sender_cs = Web3.to_checksum_address(sender)
        receiver_cs = Web3.to_checksum_address(receiver)
        tx = contract.functions.logFraudAttempt(
            sender_cs, receiver_cs, int(amount)#, token
        ).build_transaction({
            "from": account.address,
            "nonce": nonce,
            "gas": 300000,
            "gasPrice": w3.eth.gas_price
        })

        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print("Logged fraud tx hash:", tx_hash.hex())
        return jsonify({
            "status": "logged",
            "tx_hash": tx_hash.hex()
        })

    except Exception as e:
        print("Log error:", e)
        return jsonify({"error": str(e)}), 500

'''@app.route("/get_features", methods=["POST"])
def get_features():
    try:
        data = request.get_json()
        address = data.get("address")
        if not address:
            return jsonify({"error": "Missing address"}), 400
        features = extract_features(address)
        features = convert_decimals(features)

        return jsonify(features)

    except Exception as e:
        print("Feature extraction error:", e)
        return jsonify({"error": str(e)}), 500'''

if __name__ == "__main__":
    app.run(debug=True)
