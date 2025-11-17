#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/applications-module.h"
#include <fstream>

using namespace ns3;

int main (int argc, char *argv[])
{
  uint32_t nNodes = 4;
  std::string dataRate = "5Mbps";
  std::string delay = "10ms";
  double lossRate = 0.0; // not wired here, placeholder
  std::string out = "storage_net_metrics.csv";

  CommandLine cmd;
  cmd.AddValue ("nNodes", "Number of nodes", nNodes);
  cmd.AddValue ("dataRate", "Link data rate", dataRate);
  cmd.AddValue ("delay", "Link delay", delay);
  cmd.AddValue ("lossRate", "Packet loss rate (placeholder)", lossRate);
  cmd.AddValue ("out", "Output CSV file", out);
  cmd.Parse (argc, argv);

  NodeContainer nodes;
  nodes.Create (nNodes);

  PointToPointHelper p2p;
  p2p.SetDeviceAttribute ("DataRate", StringValue (dataRate));
  p2p.SetChannelAttribute ("Delay", StringValue (delay));

  NetDeviceContainer devices;
  for (uint32_t i=0; i<nNodes-1; ++i) {
    NodeContainer pair (nodes.Get(i), nodes.Get(i+1));
    NetDeviceContainer d = p2p.Install (pair);
    for (auto it = d.Begin(); it != d.End(); ++it) {
      devices.Add(*it);
    }
  }

  InternetStackHelper stack;
  stack.Install (nodes);

  Ipv4AddressHelper address;
  std::vector<Ipv4InterfaceContainer> ifaces;
  for (uint32_t i=0; i<nNodes-1; ++i) {
    std::ostringstream subnet;
    subnet << "10.1." << i+1 << ".0";
    address.SetBase (Ipv4Address (subnet.str ().c_str()), "255.255.255.0");
    NetDeviceContainer pairDevs;
    pairDevs.Add (devices.Get (2*i));
    pairDevs.Add (devices.Get (2*i+1));
    auto iface = address.Assign (pairDevs);
    ifaces.push_back (iface);
  }

  uint16_t port = 9000;
  UdpEchoServerHelper echoServer (port);
  ApplicationContainer serverApps = echoServer.Install (nodes.Get (nNodes-1));
  serverApps.Start (Seconds (1.0));
  serverApps.Stop (Seconds (10.0));

  UdpEchoClientHelper echoClient (Ipv4Address ("10.1.1.2"), port);
  echoClient.SetAttribute ("MaxPackets", UintegerValue (100));
  echoClient.SetAttribute ("Interval", TimeValue (Seconds (0.05)));
  echoClient.SetAttribute ("PacketSize", UintegerValue (256));
  ApplicationContainer clientApps = echoClient.Install (nodes.Get (0));
  clientApps.Start (Seconds (2.0));
  clientApps.Stop (Seconds (10.0));

  Simulator::Stop (Seconds (10.0));
  Simulator::Run ();
  Simulator::Destroy ();

  // Write simplistic metrics
  std::ofstream f (out.c_str());
  f << "metric,value\n";
  f << "nodes," << nNodes << "\n";
  f << "dataRate," << dataRate << "\n";
  f << "delay," << delay << "\n";
  f << "lossRate," << lossRate << "\n";
  f.close();
  return 0;
}
