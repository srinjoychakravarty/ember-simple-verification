import pytest
from web3 import EthereumTesterProvider, Web3
import contract_abi, contract_bytecode
import binascii

@pytest.fixture
def tester_provider():
    return EthereumTesterProvider()

@pytest.fixture
def eth_tester(tester_provider):
    return tester_provider.ethereum_tester

@pytest.fixture
def w3(tester_provider):
    return Web3(tester_provider)

@pytest.fixture
def foo_contract(eth_tester, w3):
    deploy_address = eth_tester.get_accounts()[0]
    # contract_address = "0xd33814b0aA4bC9c9d560a01F9780c82beE76Ffa7"
    string_bytecode = contract_bytecode.bytecode
    heya = binascii.hexlify(string_bytecode.encode('utf8'))
    FooContract = w3.eth.contract(abi = contract_abi.abi, bytecode = heya)                # Creates contract class
    # FooContract = w3.eth.contract(abi = contract_abi.abi, address = contract_address)
    tx_hash = FooContract.constructor().transact({'from': deploy_address, 'gas': 3000000000})                                      # Issues a transaction to deploy the contract
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash, 180)                                                 # Wait for the transaction to be mined
    return FooContract(tx_receipt.contractAddress)                                                              # Innstantiate and return an instance of the contract

def test_initial_greeting(foo_contract):
    hw = foo_contract.caller.getAdminCount()
    print(hw)
    # assert hw == 4

# def test_can_update_greeting(w3, foo_contract):
#     tx_hash = foo_contract.functions.setBar("testing contracts is easy").transact({'from': w3.eth.accounts[1]}) # Send transaction that updates the greeting
#     w3.eth.waitForTransactionReceipt(tx_hash, 180)
#     hw = foo_contract.caller.bar()                                                                              # Verify that the contract is now using the updated greeting
#     assert hw == "testing contracts is easy"

# def test_updating_greeting_emits_event(w3, foo_contract):
#     # send transaction that updates the greeting
#     tx_hash = foo_contract.functions.setBar(
#         "testing contracts is easy",
#     ).transact({
#         'from': w3.eth.accounts[1],
#     })
#     receipt = w3.eth.waitForTransactionReceipt(tx_hash, 180)

#     # get all of the `barred` logs for the contract
#     logs = foo_contract.events.barred.getLogs()
#     assert len(logs) == 1

#     # verify that the log's data matches the expected value
#     event = logs[0]
#     assert event.blockHash == receipt.blockHash
#     assert event.args._bar == "testing contracts is easy"
