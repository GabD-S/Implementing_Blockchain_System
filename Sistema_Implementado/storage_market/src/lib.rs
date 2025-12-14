#![cfg_attr(not(feature = "std"), no_std, no_main)]

#[ink::contract]
pub mod storage_market {
    use ink::prelude::string::String;
    use ink::storage::Mapping;

    #[derive(scale::Encode, scale::Decode, Clone)]
    #[cfg_attr(feature = "std", derive(scale_info::TypeInfo, Debug))]
    #[cfg_attr(feature = "std", derive(ink::storage::traits::StorageLayout))]
    pub struct ProviderProfile {
        pub capacity: u64,
        pub price_per_gb: u128,
        pub active: bool,
    }

    #[derive(scale::Encode, scale::Decode, Clone)]
    #[cfg_attr(feature = "std", derive(scale_info::TypeInfo, Debug))]
    #[cfg_attr(feature = "std", derive(ink::storage::traits::StorageLayout))]
    pub struct StorageDeal {
        pub buyer: AccountId,
        pub provider: AccountId,
        pub file_cid: String,
        pub size: u64,
        pub duration: u64,
        pub value: Balance,
        pub completed: bool,
    }

    #[ink(storage)]
    pub struct StorageMarketContract {
        providers: Mapping<AccountId, ProviderProfile>,
        deals: Mapping<u32, StorageDeal>,
        next_id: u32,
        owner: AccountId,
    }

    #[ink(event)]
    pub struct ProviderRegistered {
        #[ink(topic)]
        provider: AccountId,
    }

    #[ink(event)]
    pub struct DealCreated {
        #[ink(topic)]
        deal_id: u32,
    }

    #[ink(event)]
    pub struct DealCompleted {
        #[ink(topic)]
        deal_id: u32,
    }

    impl StorageMarketContract {
        #[ink(constructor)]
        pub fn new() -> Self {
            Self {
                providers: Mapping::default(),
                deals: Mapping::default(),
                next_id: 0,
                owner: Self::env().caller(),
            }
        }

        #[ink(message)]
        pub fn register_provider(&mut self, capacity: u64, price_per_gb: u128) -> bool {
            let caller = self.env().caller();
            let profile = ProviderProfile {
                capacity,
                price_per_gb,
                active: true,
            };
            self.providers.insert(caller, &profile);
            self.env().emit_event(ProviderRegistered { provider: caller });
            true
        }

        #[ink(message, payable)]
        pub fn create_deal(
            &mut self,
            provider: AccountId,
            file_cid: String,
            size: u64,
            duration: u64,
        ) -> u32 {
            let buyer = self.env().caller();
            let value = self.env().transferred_value();

            let deal_id = self.next_id;
                    
            self.next_id = self
                .next_id
                .checked_add(1)
                .expect("deal id overflow");
                

            let deal = StorageDeal {
                buyer,
                provider,
                file_cid,
                size,
                duration,
                value,
                completed: false,
            };

            self.deals.insert(deal_id, &deal);
            self.env().emit_event(DealCreated { deal_id });

            deal_id
        }

        #[ink(message)]
        pub fn complete_deal(&mut self, deal_id: u32) -> bool {
            if let Some(mut deal) = self.deals.get(deal_id) {
                if deal.completed {
                    return false;
                }
                deal.completed = true;
                self.deals.insert(deal_id, &deal);
                self.env().emit_event(DealCompleted { deal_id });
                true
            } else {
                false
            }
        }

        #[ink(message)]
        pub fn get_provider(&self, who: AccountId) -> Option<ProviderProfile> {
            self.providers.get(who)
        }

        #[ink(message)]
        pub fn get_deal(&self, deal_id: u32) -> Option<StorageDeal> {
            self.deals.get(deal_id)
        }
    }
}
