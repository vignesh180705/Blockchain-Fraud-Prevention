# blockchain_client.py
import requests

payload = {
  "sender": "0xSenderAddress",
  "receiver": "0xReceiverAddress",
  "amount": 100,
  "features": [/* your features */]
}
r = requests.post("http://127.0.0.1:5000/predict", json=payload)
print(r.json())
