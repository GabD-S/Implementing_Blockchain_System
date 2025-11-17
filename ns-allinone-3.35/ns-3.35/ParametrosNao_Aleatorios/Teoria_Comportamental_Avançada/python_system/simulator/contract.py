from dataclasses import dataclass
from enum import Enum

class DealState(Enum):
    Proposed = 0
    Agreed = 1
    Failed = 2
    Completed = 3

@dataclass
class StorageDeal:
    buyer: int
    provider: int
    file_cid: str
    buyer_accepted: bool = False
    provider_accepted: bool = False
    state: DealState = DealState.Proposed

class StorageMarketContract:
    def __init__(self):
        self.providers = {}
        self.deals = {}
        self.next_id = 0
        self.events = []

    def registerProvider(self, provider_id: int, metadata_hash: str = "") -> bool:
        self.providers[provider_id] = {"metadataHash": metadata_hash, "active": True}
        self.events.append(("ProviderRegistered", {"provider": provider_id}))
        return True

    def requestStorage(self, buyer_id: int, provider_id: int, file_cid: str) -> int:
        did = self.next_id
        self.next_id += 1
        self.deals[did] = StorageDeal(buyer=buyer_id, provider=provider_id, file_cid=file_cid)
        self.events.append(("DealRequested", {"dealId": did, "buyer": buyer_id, "provider": provider_id, "fileCid": file_cid}))
        return did

    def acceptBuyer(self, buyer_id: int, deal_id: int) -> bool:
        d = self.deals.get(deal_id)
        if not d or d.buyer != buyer_id or d.state in (DealState.Completed, DealState.Failed):
            return False
        d.buyer_accepted = True
        if d.buyer_accepted and d.provider_accepted:
            d.state = DealState.Agreed
            self.events.append(("DealAgreed", {"dealId": deal_id}))
        return True

    def acceptProvider(self, provider_id: int, deal_id: int) -> bool:
        d = self.deals.get(deal_id)
        if not d or d.provider != provider_id or d.state in (DealState.Completed, DealState.Failed):
            return False
        d.provider_accepted = True
        if d.buyer_accepted and d.provider_accepted:
            d.state = DealState.Agreed
            self.events.append(("DealAgreed", {"dealId": deal_id}))
        return True

    def completeStorage(self, buyer_id: int, deal_id: int) -> bool:
        d = self.deals.get(deal_id)
        if not d or d.buyer != buyer_id or d.state != DealState.Agreed:
            return False
        d.state = DealState.Completed
        self.events.append(("DealCompleted", {"dealId": deal_id}))
        return True
