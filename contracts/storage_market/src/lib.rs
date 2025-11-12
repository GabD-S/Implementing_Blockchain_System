#![cfg_attr(not(feature = "std"), no_std, no_main)]

#[ink::contract]
pub mod storage_market {
    use ink::prelude::string::String;
    use ink::prelude::vec::Vec;
    use ink::storage::Mapping;

    #[derive(scale::Encode, scale::Decode, scale_info::TypeInfo, Clone, Debug, PartialEq, Eq)]
    #[cfg_attr(feature = "std", derive(::ink::storage::traits::StorageLayout))]
    pub enum DealState {
        Proposed,
        Agreed,
        Failed,
        Completed,
    }

    #[derive(scale::Encode, scale::Decode, scale_info::TypeInfo, Clone, Debug, PartialEq, Eq)]
    #[cfg_attr(feature = "std", derive(::ink::storage::traits::StorageLayout))]
    pub struct ProviderProfile {
        pub metadata_hash: Option<String>,
        pub active: bool,
    }

    #[derive(scale::Encode, scale::Decode, scale_info::TypeInfo, Clone, Debug, PartialEq, Eq)]
    #[cfg_attr(feature = "std", derive(::ink::storage::traits::StorageLayout))]
    pub struct StorageDeal {
        pub buyer: AccountId,
        pub provider: AccountId,
        pub file_cid: String,
        pub buyer_accepted: bool,
        pub provider_accepted: bool,
        pub state: DealState,
    }

    #[ink(storage)]
    pub struct StorageMarket {
        providers: Mapping<AccountId, ProviderProfile>,
        deals: Mapping<u128, StorageDeal>,
        next_deal_id: u128,
    }

    #[ink(event)]
    pub struct ProviderRegistered {
        #[ink(topic)]
        provider: AccountId,
    }

    #[ink(event)]
    pub struct DealRequested {
        #[ink(topic)]
        deal_id: u128,
        #[ink(topic)]
        buyer: AccountId,
        #[ink(topic)]
        provider: AccountId,
        file_cid: String,
    }

    #[ink(event)]
    pub struct DealAgreed {
        #[ink(topic)]
        deal_id: u128,
    }

    #[ink(event)]
    pub struct DealCompleted {
        #[ink(topic)]
        deal_id: u128,
    }

    impl StorageMarket {
        #[ink(constructor)]
        pub fn new() -> Self {
            Self { providers: Mapping::default(), deals: Mapping::default(), next_deal_id: 0 }
        }

        #[ink(message)]
        pub fn register_provider(&mut self, metadata_hash: Option<String>) -> bool {
            let who = self.env().caller();
            let profile = ProviderProfile { metadata_hash, active: true };
            self.providers.insert(who, &profile);
            self.env().emit_event(ProviderRegistered { provider: who });
            true
        }

        #[ink(message)]
        pub fn request_storage(&mut self, provider: AccountId, file_cid: String) -> u128 {
            let buyer = self.env().caller();
            let deal_id = self.next_deal_id;
            self.next_deal_id = self.next_deal_id.saturating_add(1);
            let deal = StorageDeal { buyer, provider, file_cid: file_cid.clone(), buyer_accepted: false, provider_accepted: false, state: DealState::Proposed };
            self.deals.insert(deal_id, &deal);
            self.env().emit_event(DealRequested { deal_id, buyer, provider, file_cid });
            deal_id
        }

        #[ink(message)]
        pub fn accept_buyer(&mut self, deal_id: u128) -> bool {
            let caller = self.env().caller();
            match self.deals.get(deal_id) {
                Some(mut d) => {
                    if d.buyer != caller { return false; }
                    if matches!(d.state, DealState::Completed | DealState::Failed) { return false; }
                    d.buyer_accepted = true;
                    if d.buyer_accepted && d.provider_accepted { d.state = DealState::Agreed; self.env().emit_event(DealAgreed { deal_id }); }
                    self.deals.insert(deal_id, &d);
                    true
                }
                None => false,
            }
        }

        #[ink(message)]
        pub fn accept_provider(&mut self, deal_id: u128) -> bool {
            let caller = self.env().caller();
            match self.deals.get(deal_id) {
                Some(mut d) => {
                    if d.provider != caller { return false; }
                    if matches!(d.state, DealState::Completed | DealState::Failed) { return false; }
                    d.provider_accepted = true;
                    if d.buyer_accepted && d.provider_accepted { d.state = DealState::Agreed; self.env().emit_event(DealAgreed { deal_id }); }
                    self.deals.insert(deal_id, &d);
                    true
                }
                None => false,
            }
        }

        #[ink(message)]
        pub fn complete_storage(&mut self, deal_id: u128) -> bool {
            let caller = self.env().caller();
            match self.deals.get(deal_id) {
                Some(mut d) => {
                    if d.buyer != caller { return false; }
                    if !matches!(d.state, DealState::Agreed) { return false; }
                    d.state = DealState::Completed;
                    self.deals.insert(deal_id, &d);
                    self.env().emit_event(DealCompleted { deal_id });
                    true
                }
                None => false,
            }
        }

        #[ink(message)]
        pub fn get_deal(&self, deal_id: u128) -> Option<StorageDeal> { self.deals.get(deal_id) }

        #[ink(message)]
        pub fn is_provider_active(&self, account: AccountId) -> bool { self.providers.get(account).map(|p: ProviderProfile| p.active).unwrap_or(false) }
    }

    #[cfg(test)]
    mod tests {
        use super::*;
        use ink::env::test;
        fn set_caller(account: AccountId) { test::set_caller::<ink::env::DefaultEnvironment>(account); }

        #[ink::test]
        fn provider_registration_and_flow() {
            let accounts = test::default_accounts::<ink::env::DefaultEnvironment>();
            let buyer = accounts.alice; let provider = accounts.bob;
            let mut sm = StorageMarket::new();
            set_caller(provider); assert!(sm.register_provider(Some(String::from("QmProviderMeta")))); assert!(sm.is_provider_active(provider));
            set_caller(buyer); let deal_id = sm.request_storage(provider, String::from("QmFileCid123")); let d = sm.get_deal(deal_id).expect("deal exists");
            assert_eq!(d.state, DealState::Proposed); assert_eq!(d.buyer, buyer); assert_eq!(d.provider, provider);
            set_caller(provider); assert!(sm.accept_provider(deal_id)); let d = sm.get_deal(deal_id).unwrap(); assert!(d.provider_accepted); assert_eq!(d.state, DealState::Proposed);
            set_caller(buyer); assert!(sm.accept_buyer(deal_id)); let d = sm.get_deal(deal_id).unwrap(); assert!(d.buyer_accepted); assert_eq!(d.state, DealState::Agreed);
            assert!(sm.complete_storage(deal_id)); let d = sm.get_deal(deal_id).unwrap(); assert_eq!(d.state, DealState::Completed);
        }

        #[ink::test]
        fn only_parties_can_accept_and_complete() {
            let accounts = test::default_accounts::<ink::env::DefaultEnvironment>();
            let buyer = accounts.alice; let provider = accounts.bob; let other = accounts.charlie;
            let mut sm = StorageMarket::new();
            set_caller(provider); assert!(sm.register_provider(None));
            set_caller(buyer); let deal_id = sm.request_storage(provider, String::from("QmCID"));
            set_caller(other); assert!(!sm.accept_buyer(deal_id)); assert!(!sm.accept_provider(deal_id)); assert!(!sm.complete_storage(deal_id));
            set_caller(provider); assert!(sm.accept_provider(deal_id));
            set_caller(buyer); assert!(sm.accept_buyer(deal_id)); assert!(sm.complete_storage(deal_id));
        }
    }
}
