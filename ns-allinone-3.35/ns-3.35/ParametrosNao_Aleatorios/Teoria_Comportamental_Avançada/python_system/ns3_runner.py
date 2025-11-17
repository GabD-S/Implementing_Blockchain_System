#!/usr/bin/env python3
"""
Build and run the ns-3 scratch/storage_net.cc with parameters, parse output.
Falls back to synthetic metrics if build/run fails, so pipeline keeps working.
"""
import os, subprocess, json

def find_ns3_root(start_dir: str) -> str:
    d = os.path.abspath(start_dir)
    for _ in range(10):
        if os.path.exists(os.path.join(d, 'wscript')) and os.path.isdir(os.path.join(d, 'scratch')):
            return d
        nd = os.path.dirname(d)
        if nd == d:
            break
        d = nd
    # Fallback to known typical path
    candidate = os.path.abspath(os.path.join(start_dir, '../../../../..', 'ns-3.35'))
    return candidate

NS3_ROOT = find_ns3_root(os.path.dirname(__file__))

def run_ns3(n_nodes=10, data_rate='5Mbps', delay='20ms', loss_rate=0.0, out_csv='storage_net_metrics.csv'):
    try:
        cmd_build = ["./waf", "--run", f"scratch/storage_net --nNodes={n_nodes} --dataRate={data_rate} --delay={delay} --lossRate={loss_rate} --out={out_csv}"]
        proc = subprocess.run(cmd_build, cwd=NS3_ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=600)
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr[-500:])
        csv_path = os.path.join(NS3_ROOT, out_csv)
        if os.path.exists(csv_path):
            return parse_csv(csv_path)
    except Exception as e:
        # Fallback synthetic metrics
        return {
            'nodes': n_nodes,
            'dataRate': data_rate,
            'delay': delay,
            'lossRate': loss_rate,
            'source': 'fallback'
        }

def parse_csv(path):
    out = {}
    with open(path, 'r') as f:
        next(f)
        for line in f:
            k,v = line.strip().split(',',1)
            out[k] = v
    out['source'] = 'ns3'
    return out

if __name__ == '__main__':
    print(json.dumps(run_ns3(), indent=2))
