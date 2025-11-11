# acc_matches_animation.py
import json, pandas as pd, matplotlib.pyplot as plt, imageio
from pathlib import Path
with open("racional_resultados.json") as f:
    data = json.load(f)
matches = pd.DataFrame(data["matches"]); providers = pd.DataFrame(data["providers"])
provider_ids = sorted(providers["id"].tolist())
acc = {pid:0 for pid in provider_ids}
frames = []
TMP = Path("frames_tmp"); TMP.mkdir(exist_ok=True)
for i, r in matches.iterrows():
    if r["accepted"]:
        acc[int(r["provider_id"])] += 1
    fig, ax = plt.subplots(figsize=(6,4))
    s = [acc[pid] for pid in provider_ids]
    ax.bar([str(x) for x in provider_ids], s)
    ax.set_ylim(0, max(3, max(s)+1))
    ax.set_title(f"step {i+1}")
    p = TMP / f"frame_{i:03d}.png"
    fig.savefig(p, bbox_inches="tight"); plt.close(fig)
    frames.append(str(p))
with imageio.get_writer("acc_matches_animation.gif", mode="I", duration=0.6) as w:
    for f in frames:
        w.append_data(imageio.imread(f))
# cleanup
for f in frames:
    Path(f).unlink()