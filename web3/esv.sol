pragma solidity ^0.5.3;
pragma experimental ABIEncoderV2;

contract ESV_7_8
{
    uint256[] accountIDs;
    
    string[] accountSignatures;
    mapping(string => bool) Signatures;

    string[] accountMessageHashes;
    mapping(string => bool) MessageHashes;

    address[] etherAddrs;
    mapping(address => bool) ethAddresses;

    address[] adminAddresses;
    mapping(address => bool) admins;

    mapping(uint256 => ESVItem) accounts;

    address payable owner;
    
    struct ESVItem 
    {
        bool exists;
        bool hasSigned;
        string messageHash;
        string signature;
        address ethAddress;
    }
    
    modifier onlyContractOwner 
    {
        require (msg.sender == owner, "Only contract owner can call this function!");
        _;
    }
    
    modifier onlyAdmins() 
    {
        require(admins[msg.sender], "Only adminstrators can call this function!");
        _;
    }

    constructor() public 
    { 
        owner = msg.sender; 
        setAdminCreate(owner);
    }
    
    function getContractOwner() view public returns (address)
    {
        return owner;
    }

    function setESVItemCreate(uint256 _userUUID) public onlyAdmins
    {
        require(accounts[_userUUID].exists == false, "ESV Item already exists, failed to re-add!");     // prevent gas wastage on redundant add
        {
            ESVItem memory newESVItem = ESVItem(true, false, "", "", address(0));
            accounts[_userUUID] = newESVItem;
            accountIDs.push(_userUUID);
        }
    }

    function getESVItem(uint256 _userUUID) view public returns (bool, bool, string memory, string memory, address) 
    {
        return (accounts[_userUUID].exists, accounts[_userUUID].hasSigned, accounts[_userUUID].messageHash, accounts[_userUUID].signature,  accounts[_userUUID].ethAddress);
    }

    function getAllESVItemIDs() view public returns(uint256[] memory) 
    {
        return accountIDs;
    }

    function getESVItemCount() view public returns (uint) 
    {
        return accountIDs.length;
    }

    function setESVItemDelete(uint256 _userUUID) public onlyAdmins
    {
        delete accounts[_userUUID];
        for (uint j = 0; j < accountIDs.length; j++) 
        {
            if(accountIDs[j] == _userUUID)
            {
                delete accountIDs[j];
                uint256 lastESVItemID = accountIDs[accountIDs.length - 1];  
                accountIDs[j] = lastESVItemID;                                   
                accountIDs.pop();
                break;
            }
        }
    }

    function setESVItemSignatureUpdate(uint256 _userUUID, string memory _msg, string memory _sig, bytes memory _ethaddr) public 
    // assumes message, signature or address cannot be independently updated as this would break verification
    {
        require (accounts[_userUUID].exists == true, "ESVItem not created before update!");                       
        address ethAddress = bytesToAddress(_ethaddr);
        require(ethAddresses[ethAddress] == false, "Eth Address already in system!");
        accounts[_userUUID] = ESVItem(true, true, _msg, _sig, ethAddress);
        accountMessageHashes.push(_msg);
        MessageHashes[_msg] = true;
        accountSignatures.push(_sig);
        Signatures[_sig] = true;
        etherAddrs.push(ethAddress);
        ethAddresses[ethAddress] = true;
    }
    
    function setMultiESVItemSignatureUpdate(uint256[] memory _userUUID, string[] memory _msg, string[] memory _sig, bytes[] memory _ethaddr ) public
    {
        require(_userUUID.length == _msg.length,  "Hashes don't equal ESVItems!");
        require(_userUUID.length == _sig.length,  "Signatures don't equal ESVItems!");
        require(_userUUID.length == _ethaddr.length,  "Addresses don't equal ESVItems!");
        require(_userUUID.length > 0, "ESVItem array not non-zero!");
        uint256 lastAcct = 0;                                       
        for (uint i = 0; i < _userUUID.length; i++)
        {
            require (accounts[_userUUID[i]].exists == true, "ESVItem not created before update!"); 
            uint256 pendingAcct = _userUUID[i]; 
            address ethAddress = bytesToAddress(_ethaddr[i]);
            require(pendingAcct > lastAcct, "Duplicate ESVItem detected!");
            require(ethAddresses[ethAddress] == false, "Address already in system!");
            lastAcct = pendingAcct;
            accounts[_userUUID[i]] = ESVItem(true, true, _msg[i], _sig[i], ethAddress);
            accountMessageHashes.push(_msg[i]);
            MessageHashes[_msg[i]] = true;
            accountSignatures.push(_sig[i]);
            Signatures[_sig[i]] = true;
            etherAddrs.push(ethAddress);
            ethAddresses[ethAddress] = true;
        }
    }
    
    function bytesToAddress(bytes memory source) internal pure returns(address addr) 
    {
        assembly 
        {
            addr := mload(add(source, 0x14))
        }
    }
    
    function getMultiESVItem(uint256[] memory _userUUID) view public returns (ESVItem[] memory)
    {
        require(_userUUID.length > 0, "Multiple ESVItems not provided!");
        ESVItem[] memory accounts_array = new ESVItem[](_userUUID.length);
        uint256 lastAcct = 0;
        
        quickSort(_userUUID, int(0), int(_userUUID.length - 1));
        
        for (uint i = 0; i < _userUUID.length; i++)
        {
            require(accounts[_userUUID[i]].exists == true, "ESVItem doesn't exist in system!");
            uint256 pendingAcct = _userUUID[i]; 
            require(pendingAcct > lastAcct, "Duplicate ESVItem retrieval attempted!");
            lastAcct = pendingAcct;
            ESVItem storage account = accounts[_userUUID[i]];
            accounts_array[i] = account;
        }
        return accounts_array;
    }
    
    function setMultiESVItemCreate(uint256[] memory _accts) public onlyAdmins
    {
        require(_accts.length > 0, "Multiple ESVItems not provided!");
        uint256 lastAcct = 0;                                       // start at the zeroeth account uuid
        quickSort(_accts, int(0), int(_accts.length - 1));          // prevents false duplicate account validation when UUIDS in passed in array are specified in descending or mixed order [false positive]
        for (uint i = 0; i < _accts.length; i++)
        {
            uint256 pendingAcct = _accts[i];                        // helps to ensure uniqueness on chain by force-ingesting in ascending integer order
            require(pendingAcct > lastAcct, "Duplicate ESVItem retrieval attempted!");
            require(accounts[_accts[i]].exists == false, "ESVItem attempted already exists in system!");
            lastAcct = pendingAcct;
            if (accounts[pendingAcct].exists == false) 
            {
                ESVItem memory newESVItem = ESVItem(true, false, "", "", address(0));
                accounts[pendingAcct] = newESVItem;
                accountIDs.push(pendingAcct);
            }            
        }
    }
    
    function quickSort(uint[] memory arr, int left, int right) internal pure 
    {
        int i = left;
        int j = right;
        if (i == j) return;
        uint pivot = arr[uint(left + (right - left) / 2)];
        while (i <= j) 
        {
            while (arr[uint(i)] < pivot) i++;
            while (pivot < arr[uint(j)]) j--;
            if (i <= j) 
            {
                (arr[uint(i)], arr[uint(j)]) = (arr[uint(j)], arr[uint(i)]);
                i++;
                j--;
            }
        }
        if (left < j)
            quickSort(arr, left, j);
        if (i < right)
            quickSort(arr, i, right);
    }

    function setESVItemSignatureDelete(uint256 _userUUID) public
    {
        require(accounts[_userUUID].exists, "ESVItem Address doesn't exist!");
        require(accounts[_userUUID].hasSigned, "ESVItem Address not signed!");
        {
            string memory signatureExpired = accounts[_userUUID].signature;
            address ethAddress = accounts[_userUUID].ethAddress;
            ethAddresses[ethAddress] = false;
            accounts[_userUUID].messageHash = "";
            accounts[_userUUID].signature = "";
            accounts[_userUUID].ethAddress = address(0);
            accounts[_userUUID].hasSigned = false;            
            for (uint j = 0; j < accountSignatures.length; j++) 
            {
                if (keccak256(abi.encodePacked(accountSignatures[j])) == keccak256(abi.encodePacked(signatureExpired)))
                {
                    delete accountSignatures[j];
                    delete accountMessageHashes[j];                                                    
                    delete etherAddrs[j];
                    string memory lastESVItemSig = accountSignatures[accountSignatures.length - 1];
                    string memory lastMsgHash = accountMessageHashes[accountMessageHashes.length - 1]; 
                    accountSignatures[j] = lastESVItemSig;
                    accountMessageHashes[j] = lastMsgHash;  
                    accountSignatures.pop();
                    accountMessageHashes.pop();
                    etherAddrs.pop();
                    break;
                }
            }
        }
    }
    
    function setAdminCreate(address _addr) public onlyContractOwner
    {
        require(admins[_addr] == false, "admin already exists!");
        admins[_addr] = true;
        adminAddresses.push(_addr);
    }
    function setAdminDelete(address _addr) public onlyContractOwner
    {
        require(_addr != owner, "Can't remove contract owner as admin!");
        delete admins[_addr]; // 10000 gas refund
        for (uint j = 0; j < adminAddresses.length; j++) 
        {
            if (adminAddresses[j] == _addr) 
            {
                delete adminAddresses[j];
                address lastAdminAddr = adminAddresses[adminAddresses.length - 1];  
                adminAddresses[j] = lastAdminAddr;                                    // swaps last element with vacated position
                adminAddresses.pop();                                                 // deletes the last element and recover gas
                break;
            }
        }
    }
    function setMultiAdminCreate(address[] memory _addrs) public onlyContractOwner
    {
        address lastAddr = address(0);
        for (uint j = 0; j < _addrs.length; j++) 
        {
            address pendingAddr = _addrs[j];
            require(pendingAddr > lastAddr, "Duplicates detected in input list!");
            lastAddr = pendingAddr;
            require(admins[_addrs[j]] == false, "Admin already exists!");
            admins[_addrs[j]] = true;
            adminAddresses.push(_addrs[j]);
        }
    }
    
    function setMultiAdminDelete(address[] memory _addrs) public onlyContractOwner
    {
        address lastAddr = address(0);
        for (uint i = 0; i < _addrs.length; i++) 
        {
            address pendingAddr = _addrs[i];
            require(pendingAddr > lastAddr, "Duplicates detected in input list!");
            lastAddr = pendingAddr;
            require(pendingAddr != owner, "Can't remove contract owner as admin!");
            delete admins[pendingAddr];  // 10000 gas refund
            for (uint j = 0; j < adminAddresses.length; j++) 
            {
                if (adminAddresses[j] == pendingAddr) 
                {
                    address lastAdminAddr = adminAddresses[adminAddresses.length - 1];  
                    delete adminAddresses[j];
                    adminAddresses[j] = lastAdminAddr;                               // swaps last element with vacated position
                    adminAddresses.pop();                                            // deletes the last element and recover gas
                    break;
                }
            }
        }
    }

    function getSignatureAddress(bytes32 hash, bytes memory signature) public pure returns (address)
    {
        bytes32 r;
        bytes32 s;
        uint8 v;

        if (signature.length != 65)   // Check the signature length
        {
            return (address(0));
        }

        assembly 
        {
            r := mload(add(signature, 0x20))
            s := mload(add(signature, 0x40))
            v := byte(0, mload(add(signature, 0x60)))
        }

        if (v < 27)     // Version of signature should be 27 or 28, but 0 and 1 are also possible versions
        {
            v += 27;
        }

        if (v != 27 && v != 28)    // If the version is correct return the signer address
        {
            return (address(0));
        } 
        else 
        {
            return ecrecover(hash, v, r, s);    // solium-disable-next-line arg-overflow
        }
    }
    
    function getAllAdmins() view public returns(address[] memory)
    {
        return adminAddresses;
    }

    function getSignatureCount() view public returns (uint) 
    {
        return accountSignatures.length;
    }
    
    function getMessageHashCount() view public returns (uint) 
    {
        return accountMessageHashes.length;
    }
    
    function getEthereumAddressCount() view public returns (uint)
    {
        return etherAddrs.length;
    }
    
    function getAdminCount() view public returns (uint) 
    {
        return adminAddresses.length;
    }
}


