# -*- coding: utf-8 -*-
"""Step3: merge data/*.json -> data.js (window.SITE_DATA), validate coverage."""
import glob, json, re

out = {}
log = []
for f in sorted(glob.glob("data/*.json")):
    d = json.load(open(f, encoding="utf-8"))
    key = f"{d['year']}_{d['cat']}"
    bad = [t for t in d["tracks"] if not t.get("id") or not t.get("name")]
    if bad:
        log.append(f"{key}: dropped {len(bad)} invalid tracks")
    tracks = [t for t in d["tracks"] if t.get("id") and t.get("name")]
    for i, t in enumerate(tracks, 1):
        t["rank"] = i
    out[key] = {"year": d["year"], "cat": d["cat"], "pid": d.get("pid"),
                "pname": d.get("pname", ""), "creator": d.get("creator", ""),
                "fetched": d.get("fetched", len(tracks)), "tracks": tracks}
    log.append(f"{key}: tracks={len(tracks)} pid={d.get('pid')} pname={d.get('pname','')[:30]}")

missing = [(y, c) for y in range(2010, 2021) for c in ("hua", "acg")
           if f"{y}_{c}" not in out]
js = "window.SITE_DATA = " + json.dumps(out, ensure_ascii=False, separators=(",", ":")) + ";"
open("data.js", "w", encoding="utf-8").write(js)
log.append(f"years_missing={missing}")
open("step3_report.txt", "w", encoding="utf-8").write("\n".join(log))
print("BUILD OK entries=%d size=%.0fKB missing=%s" % (
    len(out), len(js) / 1024, missing))
