# -*- coding: utf-8 -*-
"""Step1c: collect candidate playlists per year via pyncm (加密通道), save manifest."""
import json, time, sys, requests
from pyncm.apis import cloudsearch

pyncm_SetNewSession = None
import pyncm
pyncm.SetNewSession()  # 匿名会话

YEARS = list(range(2010, 2021))
CATS = {
    "hua": ["{y}年度TOP100", "{y}年度华语", "{y}年度热歌", "{y}年度金曲", "{y} 百首单曲", "{y}年度百首"],
    "acg": ["{y}年度动漫歌曲", "{y}动漫歌曲TOP100", "{y}二次元", "{y}年度动漫", "{y}年度二次元"],
}

manifest = {}
log = []
for cat, kws in CATS.items():
    for y in YEARS:
        cands, seen = [], set()
        for tk in kws:
            kw = tk.format(y=y)
            for attempt in (1, 2):
                try:
                    r = cloudsearch.GetSearchResult(keyword=kw, stype=cloudsearch.PLAYLIST,
                                                    limit=50, offset=0)
                    lst = r.get("result", {}).get("playlists", [])
                    for p in lst:
                        name = p.get("name", "")
                        if str(y) not in name or p["id"] in seen:
                            continue
                        seen.add(p["id"])
                        tc = p.get("trackCount", 0)
                        if not (60 <= tc <= 400):
                            continue
                        cands.append({"id": p["id"], "name": name, "tc": tc,
                                      "creator": (p.get("creator") or {}).get("nickname", "")})
                    if lst:
                        break
                except Exception as e:
                    log.append(f"ERR {y}/{cat}/{kw}: {repr(e)[:80]}")
                    time.sleep(8)
            time.sleep(1.2)
            if len(cands) >= 8:
                break
        cands.sort(key=lambda c: (not (100 <= c["tc"] <= 150), abs(c["tc"] - 100)))
        manifest[f"{y}_{cat}"] = cands[:8]
        sys.stdout.write(f"{y} {cat}: {len(cands)} cands\n"); sys.stdout.flush()

with open("manifest1c.json", "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=1)
lines = []
for y in YEARS:
    for cat, tag in (("hua", "华语"), ("acg", "二次元")):
        v = manifest[f"{y}_{cat}"]
        lines.append(f"{y} {tag}: " + (" | ".join(
            f"{x['id']}[{x['tc']}]'{x['name'][:40]}'@{x['creator'][:8]}" for x in v) or "★无"))
open("step1c_summary.txt", "w", encoding="utf-8").write("\n".join(lines))
if log:
    open("step1c_errors.txt", "w", encoding="utf-8").write("\n".join(log))
print("DONE entries=%d errors=%d" % (len(manifest), len(log)))
