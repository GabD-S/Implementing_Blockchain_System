#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/applications-module.h"

using namespace ns3;

NS_LOG_COMPONENT_DEFINE ("CloudStorageSimple");

int main (int argc, char *argv[])
{
  // Parse command line
  uint32_t nBuyers = 5;
  uint32_t nProviders = 3;
  uint32_t nNetworkAgents = 2;
  
  CommandLine cmd;
  cmd.AddValue ("buyers", "Number of buyer agents", nBuyers);
  cmd.AddValue ("providers", "Number of provider agents", nProviders);
  cmd.AddValue ("network", "Number of network agents", nNetworkAgents);
  cmd.Parse (argc, argv);
  
  Time::SetResolution (Time::NS);
  LogComponentEnable ("CloudStorageSimple", LOG_LEVEL_INFO);
  
  uint32_t totalNodes = nBuyers + nProviders + nNetworkAgents;
  
  NS_LOG_INFO ("Multi-Agent Cloud Storage Simulation");
  NS_LOG_INFO ("Buyers: " << nBuyers << ", Providers: " << nProviders << ", Network: " << nNetworkAgents);
  
  // Create nodes
  NodeContainer allNodes;
  allNodes.Create (totalNodes);
  
  // Install Internet stack
  InternetStackHelper stack;
  stack.Install (allNodes);
  
  // Create star topology
  NodeContainer hubNode;
  hubNode.Create (1);
  stack.Install (hubNode);
  
  PointToPointHelper pointToPoint;
  pointToPoint.SetDeviceAttribute ("DataRate", StringValue ("5Mbps"));
  pointToPoint.SetChannelAttribute ("Delay", StringValue ("2ms"));
  
  // Connect all nodes to hub
  Ipv4AddressHelper address;
  address.SetBase ("10.1.0.0", "255.255.0.0");
  
  for (uint32_t i = 0; i < totalNodes; ++i)
  {
    NetDeviceContainer link = pointToPoint.Install (hubNode.Get(0), allNodes.Get(i));
    address.Assign (link);
    address.NewNetwork ();
  }
  
  // Enable global routing
  Ipv4GlobalRoutingHelper::PopulateRoutingTables ();
  
  NS_LOG_INFO ("Network topology created with " << totalNodes << " agents");
  
  // Run simulation
  Simulator::Stop (Seconds (60.0));
  Simulator::Run ();
  Simulator::Destroy ();
  
  NS_LOG_INFO ("Simulation completed successfully!");
  
  return 0;
}
