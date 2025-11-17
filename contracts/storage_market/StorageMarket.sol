// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

contract StorageMarket {
    enum DealState { Proposed, Agreed, Failed, Completed }

    struct ProviderProfile {
        string metadataHash;
        bool active;
    }

    struct StorageDeal {
        address buyer;
        address provider;
        string fileCid;
        bool buyerAccepted;
        bool providerAccepted;
        DealState state;
    }

    mapping(address => ProviderProfile) private providers;
    mapping(uint256 => StorageDeal) private deals;
    uint256 private nextDealId;

    event ProviderRegistered(address indexed provider);
    event DealRequested(uint256 indexed dealId, address indexed buyer, address indexed provider, string fileCid);
    event DealAgreed(uint256 indexed dealId);
    event DealCompleted(uint256 indexed dealId);

    constructor() {
        nextDealId = 0;
    }

    function registerProvider(string calldata metadataHash) external returns (bool) {
        providers[msg.sender] = ProviderProfile({ metadataHash: metadataHash, active: true });
        emit ProviderRegistered(msg.sender);
        return true;
    }

    function requestStorage(address provider, string calldata fileCid) external returns (uint256) {
        uint256 dealId = nextDealId;
        nextDealId += 1;
        deals[dealId] = StorageDeal({
            buyer: msg.sender,
            provider: provider,
            fileCid: fileCid,
            buyerAccepted: false,
            providerAccepted: false,
            state: DealState.Proposed
        });
        emit DealRequested(dealId, msg.sender, provider, fileCid);
        return dealId;
    }

    function acceptBuyer(uint256 dealId) external returns (bool) {
        StorageDeal storage d = deals[dealId];
        if (d.buyer != msg.sender) return false;
        if (d.state == DealState.Completed || d.state == DealState.Failed) return false;
        d.buyerAccepted = true;
        if (d.buyerAccepted && d.providerAccepted) {
            d.state = DealState.Agreed;
            emit DealAgreed(dealId);
        }
        return true;
    }

    function acceptProvider(uint256 dealId) external returns (bool) {
        StorageDeal storage d = deals[dealId];
        if (d.provider != msg.sender) return false;
        if (d.state == DealState.Completed || d.state == DealState.Failed) return false;
        d.providerAccepted = true;
        if (d.buyerAccepted && d.providerAccepted) {
            d.state = DealState.Agreed;
            emit DealAgreed(dealId);
        }
        return true;
    }

    function completeStorage(uint256 dealId) external returns (bool) {
        StorageDeal storage d = deals[dealId];
        if (d.buyer != msg.sender) return false;
        if (d.state != DealState.Agreed) return false;
        d.state = DealState.Completed;
        emit DealCompleted(dealId);
        return true;
    }

    function getDeal(uint256 dealId) external view returns (
        address buyer,
        address provider,
        string memory fileCid,
        bool buyerAccepted,
        bool providerAccepted,
        DealState state
    ) {
        StorageDeal storage d = deals[dealId];
        return (d.buyer, d.provider, d.fileCid, d.buyerAccepted, d.providerAccepted, d.state);
    }

    function isProviderActive(address account) external view returns (bool) {
        return providers[account].active;
    }
}
