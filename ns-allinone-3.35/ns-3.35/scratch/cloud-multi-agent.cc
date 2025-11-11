#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/applications-module.h"
#include <iostream>
#include <fstream>
#include <vector>
#include <map>

using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("MultiAgentCloudStorage");

struct BuyerAgent {
  uint32_t id;
  double budget;
  uint32_t storageNeeded;
  double maxPrice;
  uint32_t transactions;
  double totalSpent;
};

struct ProviderAgent {
  uint32_t id;
  uint32_t capacity;
  uint32_t available;
  double pricePerGB;
  uint32_t transactions;
  double totalEarned;
  double reputation;
};

struct NetworkAgent {
  uint32_t id;
  uint32_t transactionsFacilitated;
  double commissionRate;
  double totalCommission;
};

struct Transaction {
  uint32_t buyerId;
  uint32_t providerId;
  uint32_t networkId;
  uint32_t storageGB;
  double price;
  double timestamp;
  bool successful;
};

std::vector<BuyerAgent> g_buyers;
std::vector<ProviderAgent> g_providers;
std::vector<NetworkAgent> g_networkAgents;
std::vector<Transaction> g_transactions;

void InitializeAgents(uint32_t nBuyers, uint32_t nProviders, uint32_t nNetwork);
void SimulateTransaction();
void PrintStatistics();

void InitializeAgents(uint32_t nBuyers, uint32_t nProviders, uint32_t nNetwork) {
  Ptr<UniformRandomVariable> uniformRandom = CreateObject<UniformRandomVariable>();
  
  for (uint32_t i = 0; i < nBuyers; i++) {
    BuyerAgent buyer;
    buyer.id = i;
    buyer.budget = uniformRandom->GetValue(500.0, 2000.0);
    buyer.storageNeeded = uniformRandom->GetInteger(10, 100);
    buyer.maxPrice = uniformRandom->GetValue(0.05, 0.25);
    buyer.transactions = 0;
    buyer.totalSpent = 0.0;
    g_buyers.push_back(buyer);
    
    NS_LOG_INFO("Buyer " << i << " - Budget: $" << buyer.budget 
                << ", Needs: " << buyer.storageNeeded << "GB");
  }
  
  for (uint32_t i = 0; i < nProviders; i++) {
    ProviderAgent provider;
    provider.id = i;
    provider.capacity = uniformRandom->GetInteger(500, 2000);
    provider.available = provider.capacity;
    provider.pricePerGB = uniformRandom->GetValue(0.08, 0.20);
    provider.transactions = 0;
    provider.totalEarned = 0.0;
    provider.reputation = uniformRandom->GetValue(0.7, 1.0);
    g_providers.push_back(provider);
    
    NS_LOG_INFO("Provider " << i << " - Capacity: " << provider.capacity 
                << "GB, Price: $" << provider.pricePerGB << "/GB");
  }
  
  for (uint32_t i = 0; i < nNetwork; i++) {
    NetworkAgent network;
    network.id = i;
    network.transactionsFacilitated = 0;
    network.commissionRate = uniformRandom->GetValue(0.02, 0.08);
    network.totalCommission = 0.0;
    g_networkAgents.push_back(network);
    
    NS_LOG_INFO("Network Agent " << i << " - Commission: " 
                << (network.commissionRate * 100) << "%");
  }
}

void SimulateTransaction() {
  if (g_buyers.empty() || g_providers.empty() || g_networkAgents.empty()) return;
  
  Ptr<UniformRandomVariable> uniformRandom = CreateObject<UniformRandomVariable>();
  
  uint32_t buyerIdx = uniformRandom->GetInteger(0, g_buyers.size() - 1);
  uint32_t providerIdx = uniformRandom->GetInteger(0, g_providers.size() - 1);
  uint32_t networkIdx = uniformRandom->GetInteger(0, g_networkAgents.size() - 1);
  
  BuyerAgent& buyer = g_buyers[buyerIdx];
  ProviderAgent& provider = g_providers[providerIdx];
  NetworkAgent& network = g_networkAgents[networkIdx];
  
  bool canAfford = (buyer.budget >= buyer.storageNeeded * provider.pricePerGB);
  bool hasSpace = (provider.available >= buyer.storageNeeded);
  bool priceAcceptable = (provider.pricePerGB <= buyer.maxPrice);
  bool reputationOK = (provider.reputation >= 0.6);
  
  Transaction tx;
  tx.buyerId = buyer.id;
  tx.providerId = provider.id;
  tx.networkId = network.id;
  tx.storageGB = buyer.storageNeeded;
  tx.price = buyer.storageNeeded * provider.pricePerGB;
  tx.timestamp = Simulator::Now().GetSeconds();
  tx.successful = canAfford && hasSpace && priceAcceptable && reputationOK;
  
  if (tx.successful) {
    double commission = tx.price * network.commissionRate;
    
    buyer.budget -= tx.price;
    buyer.totalSpent += tx.price;
    buyer.transactions++;
    
    provider.available -= tx.storageGB;
    provider.totalEarned += (tx.price - commission);
    provider.transactions++;
    provider.reputation = std::min(1.0, provider.reputation + 0.01);
    
    network.totalCommission += commission;
    network.transactionsFacilitated++;
    
    NS_LOG_INFO("SUCCESS at " << tx.timestamp << "s: Buyer " << tx.buyerId 
                << " bought " << tx.storageGB << "GB for $" << tx.price);
  } else {
    if (!hasSpace || !priceAcceptable) {
      provider.reputation = std::max(0.1, provider.reputation - 0.02);
    }
    NS_LOG_INFO("FAILED at " << tx.timestamp << "s: Transaction rejected");
  }
  
  g_transactions.push_back(tx);
}

void PrintStatistics() {
  uint32_t successful = 0;
  double totalVolume = 0.0;
  
  for (const auto& tx : g_transactions) {
    if (tx.successful) {
      successful++;
      totalVolume += tx.price;
    }
  }
  
  std::cout << "\n=== SIMULATION RESULTS ===" << std::endl;
  std::cout << "Total Transactions: " << g_transactions.size() << std::endl;
  std::cout << "Successful: " << successful << std::endl;
  std::cout << "Success Rate: " << (g_transactions.size() > 0 ? 
    (double)successful/g_transactions.size()*100.0 : 0.0) << "%" << std::endl;
  std::cout << "Total Volume: $" << totalVolume << std::endl;
  
  std::cout << "\n--- Buyers ---" << std::endl;
  for (const auto& buyer : g_buyers) {
    std::cout << "Buyer " << buyer.id << ": " << buyer.transactions 
              << " tx, $" << buyer.totalSpent << " spent" << std::endl;
  }
  
  std::cout << "\n--- Providers ---" << std::endl;
  for (const auto& provider : g_providers) {
    double utilization = provider.capacity > 0 ? 
      (double)(provider.capacity - provider.available)/provider.capacity*100.0 : 0.0;
    std::cout << "Provider " << provider.id << ": " << provider.transactions 
              << " tx, $" << provider.totalEarned << " earned, " 
              << utilization << "% used" << std::endl;
  }
  
  std::cout << "\n--- Network Agents ---" << std::endl;
  for (const auto& network : g_networkAgents) {
    std::cout << "Network " << network.id << ": " << network.transactionsFacilitated 
              << " tx, $" << network.totalCommission << " commission" << std::endl;
  }
}

int main(int argc, char *argv[]) {
  uint32_t nBuyers = 8;
  uint32_t nProviders = 5;
  uint32_t nNetworkAgents = 2;
  uint32_t simulationTime = 60;
  
  CommandLine cmd;
  cmd.AddValue("buyers", "Number of buyer agents", nBuyers);
  cmd.AddValue("providers", "Number of provider agents", nProviders);
  cmd.AddValue("network", "Number of network agents", nNetworkAgents);
  cmd.AddValue("time", "Simulation time (seconds)", simulationTime);
  cmd.Parse(argc, argv);
  
  Time::SetResolution(Time::NS);
  LogComponentEnable("MultiAgentCloudStorage", LOG_LEVEL_INFO);
  
  std::cout << "\n🚀 MULTI-AGENT CLOUD STORAGE SIMULATION 🚀" << std::endl;
  std::cout << "Buyers: " << nBuyers << ", Providers: " << nProviders 
            << ", Network: " << nNetworkAgents << std::endl;
  
  InitializeAgents(nBuyers, nProviders, nNetworkAgents);
  
  for (uint32_t i = 5; i <= simulationTime; i += 5) {
    Simulator::Schedule(Seconds(i), &SimulateTransaction);
  }
  
  Simulator::Schedule(Seconds(simulationTime), &PrintStatistics);
  
  Simulator::Stop(Seconds(simulationTime + 1));
  Simulator::Run();
  Simulator::Destroy();
  
  std::cout << "\n✅ SIMULATION COMPLETED! ✅" << std::endl;
  
  return 0;
}
