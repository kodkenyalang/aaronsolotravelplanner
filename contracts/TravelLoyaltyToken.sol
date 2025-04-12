// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title TravelLoyaltyToken
 * @dev ERC20 token for the travel manager loyalty program
 */
contract TravelLoyaltyToken is ERC20, Ownable {
    // Addresses allowed to mint tokens
    mapping(address => bool) public minters;
    
    // Events
    event MinterAdded(address minter);
    event MinterRemoved(address minter);
    
    constructor() ERC20("Travel Loyalty Token", "TLT") {
        // Set deployer as initial minter
        minters[msg.sender] = true;
    }
    
    /**
     * @dev Add a minter
     * @param _minter The address of the minter to add
     */
    function addMinter(address _minter) external onlyOwner {
        require(_minter != address(0), "Invalid minter address");
        minters[_minter] = true;
        emit MinterAdded(_minter);
    }
    
    /**
     * @dev Remove a minter
     * @param _minter The address of the minter to remove
     */
    function removeMinter(address _minter) external onlyOwner {
        require(minters[_minter], "Not a minter");
        minters[_minter] = false;
        emit MinterRemoved(_minter);
    }
    
    /**
     * @dev Mint tokens to a user
     * @param _to The recipient of the tokens
     * @param _amount The amount of tokens to mint
     */
    function mint(address _to, uint256 _amount) external {
        require(minters[msg.sender], "Only minters can mint");
        _mint(_to, _amount);
    }
}
