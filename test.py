from web3 import Web3
from features import get_erc20_features
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))
address = "0x376a8fefd5d04DCf1f7744CFaA8982B69F2Dd12e"
erc20_features = get_erc20_features(w3, address)
print(erc20_features)