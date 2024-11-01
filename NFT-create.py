#edited by Faliana_Lionel
import json
from typing import Dict, Any
from base64 import b64decode

from algosdk import account, mnemonic
from algosdk import transaction
from algosdk.v2client import algod



#WARNINGS: the accounts we use here are just created for testing. You can use them that way, but do not use them as your own wallet.

# ACCOUNT_RECOVER_MNEMONIC

account_1_mnemonic = "tone bronze curtain busy immune wild game trust vast tank sphere tourist long stem tissue culture angry cabin prison mean artefact bind magic abandon jeans"
account_1_private_key = mnemonic.to_private_key(account_1_mnemonic)
account_1_address = account.address_from_private_key(account_1_private_key)

print(f"Account 1 Base64 encoded private key: {account_1_private_key}")
print(f"Account 1 Address: {account_1_address}")

account_2_mnemonic = "open grit raw crush elevator royal tone rabbit thought hour soda deposit hungry inject someone sauce fresh trust grunt unveil essay clinic erode about urge"
account_2_private_key = mnemonic.to_private_key(account_2_mnemonic)
account_2_address = account.address_from_private_key(account_2_private_key)

print(f"Account 2 Base64 encoded private key: {account_2_private_key}")
print(f"Account 2 Address: {account_2_address}")


user_input = input("Account 1 and Account 2 have been funded, press enter to continue")

# connecting to the Algorand Testnet.
algod_address = "https://testnet-api.algonode.cloud"
algod_token = ""

algod_client = algod.AlgodClient(algod_token, algod_address)

# grab suggested params from algod using client includes things like suggested fee and first/last valid rounds
suggested_params = algod_client.suggested_params()


# Asset Creation transaction
unsigned_txn = transaction.AssetConfigTxn(
    sender=account_1_address,
    sp=suggested_params,
    total=1,
    default_frozen=False,
    unit_name="MAFI",
    asset_name="MAFI2023",
    manager=account_1_address,
    reserve=account_1_address,  
    freeze=account_1_address, 
    clawback=account_1_address,
    url="https://path/to/my/asset/details",
    decimals=0,
)


# sign the transaction with private key of creator
signed_txn = unsigned_txn.sign(account_1_private_key)



# submit the transaction to the network and get back a transaction id
try:
    txid = algod_client.send_transaction(signed_txn)
    print("Signed transaction with txID: {}".format(txid))
    # Wait for the transaction to be confirmed
    confirmed_txn = transaction.wait_for_confirmation(algod_client, txid, 4)
    asset_id = confirmed_txn["asset-index"]
    confirmed_round = confirmed_txn["confirmed-round"]

    print("TXID: ", txid)
    print("Asset ID: {}".format(asset_id))
    print("Result confirmed in round: {}".format(confirmed_round))
    print("Transaction information: {}".format(json.dumps(confirmed_txn, indent=4)))
except Exception as err:
    print(err)


# Retrieve the asset info of the newly created asset
asset_info = algod_client.asset_info(asset_id)
asset_params: Dict[str, Any] = asset_info["params"]
print(f"Asset Name: {asset_params['name']}")
print(f"Asset params: {list(asset_params.keys())}")


# OPT-IN_TO_ASSET from the acount 2
user_input = input("Now Opt-in to the newly created asset and press enter. ")
# Create opt-in transaction
# asset transfer from me to me for asset id we want to opt-in to with amt==0
suggested_params = algod_client.suggested_params()
optin_txn = transaction.AssetOptInTxn(
    sender=account_2_address, sp=suggested_params, index=asset_id
)
signed_optin_txn = optin_txn.sign(account_2_private_key)
txid = algod_client.send_transaction(signed_optin_txn)
print(f"Sent opt in transaction with txid: {txid}")

# Wait for the transaction to be confirmed
results = transaction.wait_for_confirmation(algod_client, txid, 4)
print(f"Result confirmed in round: {results['confirmed-round']}")


# Create transfer transaction
suggested_params = algod_client.suggested_params()
xfer_txn = transaction.AssetTransferTxn(
    sender=account_1_address,  
    sp=suggested_params,
    receiver=account_2_address,
    amt=1,
    index=asset_id,
)
signed_xfer_txn = xfer_txn.sign(account_1_private_key)
txid = algod_client.send_transaction(signed_xfer_txn)
print(f"Sent transfer transaction with txid: {txid}")

results = transaction.wait_for_confirmation(algod_client, txid, 4)
print(f"Result confirmed in round: {results['confirmed-round']}")

