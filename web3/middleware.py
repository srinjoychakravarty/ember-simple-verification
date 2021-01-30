from colorama import Fore
from web3 import HTTPProvider, Web3
import binascii, contract_abi, emoji, hashlib, inquirer, json, pprint, subprocess, sys, threading, time, web3.exceptions

def get_chain_id(network):
    '''retrieves the right chain ethereum id'''
    help(get_chain_id)
    with open('network_ids.json') as json_file:
        chains = json.load(json_file)
        chain_item = next((item for item in chains if item["name"] == network), None)
        chain_id = int(chain_item.get('chainId'), 16)
        return chain_id

def setup():
    '''sets up connection to solidity smart contract'''
    help(setup)
    network = input("Enter blockchain network: \n") or "Rinkeby"
    print(network + "\n")
    chain_id = get_chain_id(network)
    contract_address = input("Enter smart contract address: \n") or "0xd33814b0aA4bC9c9d560a01F9780c82beE76Ffa7"
    print(contract_address + "\n")
    wallet_address = input("Enter your wallet address: \n") or "0xa6c56C26e5758CaC9D2fF67cc3687843F0AEE908"
    print(wallet_address + "\n")
    wallet_private_key = input("Enter your private key: \n") or "6045f8eaac72f51a9f435c4e142e857d73822c31f5041f7541fde0e285250a30"
    print(wallet_private_key + "\n")
    infura_key = input("Enter your infura api key: \n") or "6c7e9aed2af146138cc7ef1986d9b558"
    print(infura_key + "\n")
    websockets_rinkeby = "wss://rinkeby.infura.io/ws/v3/" + infura_key
    ws3 = Web3(Web3.WebsocketProvider(websockets_rinkeby, websocket_kwargs={'timeout': 60}))
    https_rinkeby = "https://rinkeby.infura.io/v3/" + infura_key
    w3 = Web3(HTTPProvider(https_rinkeby))
    contract = w3.eth.contract(address = contract_address, abi = contract_abi.abi)
    return (wallet_address, w3, ws3, contract, chain_id, wallet_private_key)

def list_functions(contract):
    '''lists all smart contract functions'''
    help(list_functions)
    return contract.all_functions()

def enumerate_functions(all_functions):
    '''enumerates all read functions on smart contract'''
    help(enumerate_functions)
    function_set = {str(function).replace('<Function ', '')[:-1] for function in all_functions}
    question = [inquirer.List('function', message = "Which function to call?", choices = function_set)]
    answer = inquirer.prompt(question)
    chosen_function = answer['function']
    return chosen_function

def print_gas_estimate(contract_base):
    '''calculates and returns gas estimate to execute given call'''
    help(print_gas_estimate)
    gas_estimate = contract_base + '''.estimateGas()'''
    gas_estimate_result = eval(gas_estimate)
    print(Fore.YELLOW + f"{emoji.emojize(':fuel_pump:')}  Gas Estimate: {gas_estimate_result}" + Fore.RESET)
    return gas_estimate_result

def sort_ether_addresses(admin_array):
    '''quick sorts input ethereum address array before relaying to network'''
    help(sort_ether_addresses)
    admin_array = admin_array[1:-1]
    admin_array = "".join(admin_array.split())
    strings = admin_array.split(",")
    new_strings = []
    for string in strings:
        new_string = string[1:-1]
        new_strings.append(new_string)
    new_strings.sort()
    return new_strings

def help(some_function):
    print(f"{emoji.emojize(':dragon:')}  Intrinsic Python3.9 Call to Memory Address: {some_function}\n{emoji.emojize(':file_cabinet:')}  Definition: {some_function.__doc__}")

def execute_function(chosen_function):
    '''calls getter functions or executes setter functions via ether transactions'''
    if (chosen_function[0:3] == "get"):
        print(Fore.BLUE + f"\n{emoji.emojize(':backhand_index_pointing_up:')}  Function Selected: {chosen_function}" + Fore.RESET)
        params = chosen_function[chosen_function.find('(')+1 : chosen_function.find(')')]
        if not params:
            contract_base = '''contract.functions.''' + chosen_function
            gas_estimate_result = print_gas_estimate(contract_base)
            getter =  contract_base + '''.call()'''
            result_from_getter = eval(getter)
            output = (f"{emoji.emojize(':loudspeaker:')}  {chosen_function} called successfully!\n{emoji.emojize(':game_die:')}  {chosen_function} Result: {str(result_from_getter)}")
            return output
        else:
            arguments = params.split(',')
            number_of_args = len(arguments)
            function_name = chosen_function[chosen_function.find('get') + 0 : chosen_function.find('(')]
            if ("getSignatureAddress" in function_name):          
                for x in range(1, number_of_args + 1):
                    if (x == 1):
                        msg_hash_bytes32 = input("\nEnter message hash: e.g. \"0x2d44736a74ee82cb16c42d5ef8a9d0da58e96f7d9a9fc017f2532598ece1e0b3\"\n")
                        print(Fore.BLUE + f"\n{emoji.emojize(':footprints:')} Message Hash Entered: {msg_hash_bytes32}" + Fore.RESET)
                    elif (x == 2):
                        sig_bytes = input("\nEnter digital signature: e.g. \"0xc7349eea5aa143f0bc043743f2ad0d1c37a2a47718bd649663ee8359e31c756047a60d6f623dc8d64ce78235ef0ce7ec1e0df7510a38b66527fb47f80c18aa371b\"\n")
                        print(Fore.BLUE + f"\n{emoji.emojize(':fountain_pen:')}  Digital Signature Entered: {sig_bytes}" + Fore.RESET)
                contract_base = '''contract.functions.''' + function_name + "(" + msg_hash_bytes32 + ", " + sig_bytes + ")"
                gas_estimate_result = print_gas_estimate(contract_base)
                getter = contract_base + '''.call()'''
                result_from_getter = eval(getter)
                output = (f"{emoji.emojize(':check_box_with_check:')}  {chosen_function} called successfully!\n{emoji.emojize(':game_die:')} Result: {str(result_from_getter)}")
                return output   
            if("getESVItem" in function_name):
                uuid_int = input("\nEnter UUID to set: e.g. 904\n")
                print(Fore.BLUE + f"\n{emoji.emojize(':input_numbers:')} UUID Entered: {uuid_int}" + Fore.RESET)
                contract_base = '''contract.functions.''' + function_name + "(" + uuid_int + ")"
                gas_estimate_result = print_gas_estimate(contract_base)
                getter = contract_base + '''.call()'''
                result_from_getter = eval(getter)
                output = (f"{emoji.emojize(':check_box_with_check:')}  {chosen_function} called successfully!\n{emoji.emojize(':game_die:')} Result: {str(result_from_getter)}")
                return output         
            if("getMultiESVItem" in function_name):
                while True:
                    try:
                        esv_array = input("\nEnter ESV Items with square brackets: [902, 903, 904...]\n")
                        print(Fore.BLUE + f"\n{emoji.emojize(':clipboard:')} ESV ItemArray Request: {esv_array}" + Fore.RESET)
                        contract_base = '''contract.functions.''' + function_name + "(" + esv_array + ")" 
                        gas_estimate_result = print_gas_estimate(contract_base)
                        getter = contract_base + '''.call()'''
                        result_from_getter = eval(getter)
                        output = (f"{emoji.emojize(':check_box_with_check:')}  {chosen_function} called successfully!\n{emoji.emojize(':game_die:')} Result: {str(result_from_getter)}")
                        return output
                        break
                    except Exception as error:
                        print(Fore.RED + f"\n{error}\n" + Fore.RESET)
                        choice = input("\nWould you like to try to get ESV Items again? (yes [y] | no [n]) \n") or "no"
                        print(Fore.BLUE + f"\nChoice: {choice}\n" + Fore.RESET)
                        if (choice == "no" or choice == "n"):
                            break
    elif (chosen_function[0:3] == "set"):
        with lock:
            attempts = 0
            while True:
                try:
                    remote_nonce = w3.eth.getTransactionCount(wallet_address)
                    is_local_nonce_available = "local_nonce" in locals()
                    if (is_local_nonce_available == False):
                        local_nonce = remote_nonce
                    nonce = max(local_nonce, remote_nonce)
                    is_local_gas_price_available = "gas_price" in locals()
                    if (is_local_gas_price_available == False):
                        gas_price = w3.toWei('40', 'gwei')
                    gas_limit = (10000000 - 1)
                    chosen_method = chosen_function.split('(')[0]
                    params = chosen_function[chosen_function.find('(')+1 : chosen_function.find(')')]
                    arguments = params.split(',')
                    number_of_args = len(arguments)
                    user_inputs = []
                    function_name = chosen_function[chosen_function.find('set') + 0 : chosen_function.find('(')]
                    if ("setMultiESVItemSignatureUpdate" in function_name):
                        print(Fore.BLUE + f"\n  Function Selected: {chosen_function}" + Fore.RESET)
                        
                        uuid_array = input("\nEnter uuid array: [902, 903, 904...]\n")
                        print(Fore.BLUE + f"\n{emoji.emojize(':clipboard:')} Input UUIDArray: {uuid_array}" + Fore.RESET)
                        
                        msghash_array = input("\nEnter message hash array: [\"0x2d44736a74ee82cb16c42d5ef8a9d0da58e96f7d9a9fc017f2532598ece1e0b3\", \"0x2d44736a74ee82cb16c42d5ef8a9d0da58e96f7d9a9fc017f2532598ece1e0b2\"...]\n")
                        print(Fore.BLUE + f"\n{emoji.emojize(':footprints:')} Input messageHashArray: {msghash_array}" + Fore.RESET)
                        
                        sig_array = input("\nEnter digital signature array: [\"0xc7349eea5aa143f0bc043743f2ad0d1c37a2a47718bd649663ee8359e31c756047a60d6f623dc8d64ce78235ef0ce7ec1e0df7510a38b66527fb47f80c18aa371b\", \"0xc7349eea5aa143f0bc043743f2ad0d1c37a2a47718bd649663ee8359e31c756047a60d6f623dc8d64ce78235ef0ce7ec1e0df7510a38b66527fb47f80c18aa371c\"...]\n")
                        print(Fore.BLUE + f"\n{emoji.emojize(':fountain_pen:')}  Input digitalSignatureArray: {sig_array}" + Fore.RESET)
                        
                        ethaddr_array = input("\nEnter ethereum address array: [\"0xa6c56C26e5758CaC9D2fF67cc3687843F0AEE908\", \"0xa6c56C26e5758CaC9D2fF67cc3687843F0AEE907\"]\n")
                        print(Fore.BLUE + f"\n{emoji.emojize(':chains:')} Input ethereumAddressArray: {ethaddr_array}" + Fore.RESET)

                        setter_base = '''contract.functions.''' + chosen_method + '(' + uuid_array + ', ' + msghash_array + ', ' + sig_array + ', ' + ethaddr_array + ')'
                        print(f"Setter Base: {setter_base}")       
                    elif (function_name == "setESVItemCreate"):
                        print(Fore.BLUE + f"\n  Function Selected: {chosen_function}" + Fore.RESET)
                        account_id = input("\nEnter acount id:  e.g. 904\n")
                        setter_base = '''contract.functions.''' + chosen_method + '(' + str(account_id) + ')'
                    elif (function_name == "setMultiESVItemCreate"):
                        print(Fore.BLUE + f"\n  Function Selected: {chosen_function}" + Fore.RESET)
                        account_id_array = input("\nEnter acount id array: [integer1, integer2...]\n")
                        setter_base = '''contract.functions.''' + chosen_method + '(' + str(account_id_array) + ')'
                    elif (function_name == "setAdminCreate"):
                        print(Fore.BLUE + f"\n  Function Selected: {chosen_function}" + Fore.RESET)
                        admin_addr = input("\nEnter admin ethereum address to register: e.g. \"0x3Bc1D006EeF6cdf608097fCdfDD0CBCeB6011e94\"\n")
                        setter_base = '''contract.functions.''' + chosen_method + '(' + str(admin_addr) + ')'
                    elif (function_name == "setAdminDelete"):
                        print(Fore.BLUE + f"\n  Function Selected: {chosen_function}" + Fore.RESET)
                        admin_del_addr = input("\nEnter admin ethereum address to register: e.g. \"0x793960215a519cddeFE3e51B0FeDAbB9D377ec95\"\n")
                        setter_base = '''contract.functions.''' + chosen_method + '(' + str(admin_del_addr) + ')'
                    elif (function_name == "setMultiAdminCreate"):
                        print(Fore.BLUE + f"\n  Function Selected: {chosen_function}" + Fore.RESET)
                        admin_array = input("\nEnter admin address array to create: [\"0x3Bc1D006EeF6cdf608097fCdfDD0CBCeB6011e94\", \"0x793960215a519cddeFE3e51B0FeDAbB9D377ec95\"...]\n")   
                        sorted_admin_list = sort_ether_addresses(admin_array)
                        print(Fore.YELLOW + f"\n{emoji.emojize(':abacus:')}  Sorted Admin List: {sorted_admin_list}" + Fore.RESET)
                        setter_base = '''contract.functions.''' + chosen_method + '(' + str(sorted_admin_list) + ')'
                    elif (function_name == "setMultiAdminDelete"):
                        print(Fore.BLUE + f"\n  Function Selected: {chosen_function}" + Fore.RESET)
                        admin_array = input("\nEnter admin address array to delete: [\"0xCA35b7d915458EF540aDe6068dFe2F44E8fa733c\", \"0x793960215a519cddeFE3e51B0FeDAbB9D377ec95\"...]\n")
                        sorted_admin_list = sort_ether_addresses(admin_array)
                        print(Fore.YELLOW + f"\n{emoji.emojize(':abacus:')}  Sorted Admin List: {sorted_admin_list}" + Fore.RESET)
                        setter_base = '''contract.functions.''' + chosen_method + '(' + str(sorted_admin_list) + ')'
                    elif (function_name == "setESVItemSignatureUpdate"):
                        print(Fore.BLUE + f"\n  Function Selected: {chosen_function}" + Fore.RESET)
                        uuid_integer = input("\nEnter UUID to set: e.g. 904\n")
                        msg_hash_bytes32 = input("\nEnter message hash: e.g. \"0x2d44736a74ee82cb16c42d5ef8a9d0da58e96f7d9a9fc017f2532598ece1e0b3\"\n")
                        sig_bytes = input("\nEnter digital signature: e.g. \"0xc7349eea5aa143f0bc043743f2ad0d1c37a2a47718bd649663ee8359e31c756047a60d6f623dc8d64ce78235ef0ce7ec1e0df7510a38b66527fb47f80c18aa371b\"\n")
                        eth_addr = input("\nEnter ethereum address to store: e.g.\"0xa6c56C26e5758CaC9D2fF67cc3687843F0AEE908\"\n")
                        setter_base = '''contract.functions.''' + chosen_method + '(' + uuid_integer + ', ' + msg_hash_bytes32 + ', ' + sig_bytes + ', ' + eth_addr + ')'                    
                    txn_details = {'chainId': chain_id, 'gas': gas_limit, 'gasPrice': gas_price, 'nonce': max(nonce, local_nonce, remote_nonce)}
                    setter = setter_base + '''.buildTransaction(''' + str(txn_details) + ')'    
                    txn_dict = eval(setter)
                    print(Fore.LIGHTBLUE_EX + f"\nTransaction Dictionary:\n{txn_dict}\n" + Fore.RESET)
                    signed_setter = '''(w3.eth.account.signTransaction(''' + str(txn_dict) + ', private_key = "' + wallet_private_key + '")).rawTransaction'
                    signed_txn = eval(signed_setter)
                    sent_txn_cmd = '''w3.eth.sendRawTransaction(''' + str(signed_txn) + ')'
                    txn_hash = eval(sent_txn_cmd)
                    construct_hex = '''(''' + str(txn_hash) + ').hex()'
                    txn_hash_hex = "0x" + eval(construct_hex)
                    result_checker = '''w3.eth.waitForTransactionReceipt(''' + str(txn_hash) + ')'
                    receipt = eval(result_checker)
                    print(Fore.LIGHTWHITE_EX + f"\nTransaction Receipt: {receipt}\nReceipt Datatype: {type(receipt)}\n" + Fore.RESET)
                    receipt_status = receipt.get('status')
                    gas_used = receipt.get('cumulativeGasUsed')
                    block_included_in = receipt.get('blockNumber')
                    if (str(receipt_status) == "0"):
                        print(Fore.RED + f"\nTransaction Reverted!\n{emoji.emojize(':dna:')} Transaction Hash: {txn_hash_hex}\n{emoji.emojize(':fuel_pump:')} Total Gas Used: {gas_used}\n{emoji.emojize(':hammer:')} Block Included In: {block_included_in}\n" + Fore.RESET)
                    else:
                        print(Fore.GREEN + f"\n{emoji.emojize(':check_mark:')}  Transaction Success! \n{emoji.emojize(':dna:')}  Transaction Hash: {txn_hash_hex}\n{emoji.emojize(':fuel_pump:')}  Total Gas Used: {gas_used}\n{emoji.emojize(':hammer:')}  Block Included In: {block_included_in}\n" + Fore.RESET)
                    output = (f"\n{emoji.emojize(':clipboard:')} Log History: {chosen_function} was executed.\n")
                    return output
                except ValueError as value_error:
                    print(f"ValueError: {value_error}")
                    local_nonce = nonce + 1
                    print(f"Incremented Local Nonce + 1: {local_nonce}")
                    gas_price = w3.toWei(str(40 * 1.1), 'gwei')
                    print(f"Incremented Gas Price by 10%: {gas_price}")
                    if "message" in value_error.args[0]:
                        error_message = value_error.args[0]['message']
                        if ("nonce too low" in error_message or "another transaction with same nonce" in error_message or "the tx doesn't have the correct nonce" in error_message or "replacement transaction underpriced" in error_message) and (attempts < 4):
                            print(Fore.YELLOW + f"\n{error_message}\n\nRetrying with higher nonce and gas price...\n" + Fore.RESET)
                            attempts += 1

if __name__ == '__main__':
    print("\nWelcome to ESV v7.6.1\n")
    wallet_address, w3, ws3, contract, chain_id, wallet_private_key = setup()
    loop_again = True
    while (loop_again == True):
        all_functions = list_functions(contract)
        chosen_function = enumerate_functions(all_functions)
        lock = threading.RLock()
        output = execute_function(chosen_function)
        if output is None:
            print(Fore.LIGHTRED_EX + "\nWarning: No Output Returned.\n" + Fore.RESET)
        else:
            print(Fore.LIGHTMAGENTA_EX + output + Fore.RESET)
        choice = input("\nWould you like to quit? (yes [y] | no [n]) \n") or "yes"
        print(f"\n Choice: {choice}\n")
        if (choice == "yes" or choice == "y" or choice == "exit" or choice == "q" or choice == "quit"):
            loop_again = False
            print("\nThank You for using ESV v7.6.1!\n") 