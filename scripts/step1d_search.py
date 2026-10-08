# -*- coding: utf-8 -*-
"""Step1d: targeted second pass for weak years (hua 2010-2015 + better acg 2010-2012)."""
import json, time, pyncm
from pyncm.apis import cloudsearch

pyncm.SetNewSession()

TARGETS = {
    **{f"{y}_hua": [f"{y}年度最热新歌TOP100", f"{y}年度热歌TOP100", f"{y}年度热歌榜",
                    f"{y}年度最热歌曲", f"{y}年度热议单曲", f"{y}年度中文歌",
                    f"{y}年度华语热歌", f"{y}年度金曲榜"] for y in range(2010, 2017)},
    "2010_acg": [f"2010年度动漫歌曲", "2010动漫歌曲排行榜", "2010年最具人气动漫歌曲", "2010年度ACG"],
    "2011_acg": [f"2011年度动漫歌曲", "2011年最具人气动漫歌曲", "2011动漫歌曲排行榜", "2011年度ACG"],
    "2012_acg": [f"2012年度动漫歌曲", "2012年最具人气动漫歌曲", "2012动漫歌曲排行榜", "2012年度ACG"],
}

mf = json.load(open("manifest1c.json", encoding="utf-8"))
for key, kws in TARGETS.items():
    y, cat = key.rsplit("_", 1)
    seen = {c["id"] for c in mf.get(key, [])}
    good = list(mf.get(key, []))
    for kw in kws:
        try:
            r = cloudsearch.GetSearchResult(keyword=kw, stype=cloudsearch.PLAYLIST,
                                            limit=50, offset=0)
        except Exception as e:
            print(f"ERR {key} {kw}: {repr(e)[:60]}")
            continue
        for p in r.get("result", {}).get("playlists", []):
            name = p.get("name", "")
            if str(y) not in name or p["id"] in seen:
                continue
            seen.add(p["id"])
            tc = p.get("trackCount", 0)
            if not (60 <= tc <= 400):
                continue
            # 华语榜要求：歌名里含中文相关词，且不含明显外语榜特征
            if cat == "hua":
                keep = any(w in name for w in ("华语", "中文", "国语", "金曲", "热歌", "最热", "新歌"))
                bad = any(w in name for w in ("Billboard", "billboard", "B榜", "UK榜", "UK ", "欧美",
                                              "英文", "DJ", "K-POP", "KPOP", "melon", "日本", "韩国"))
                if not keep or bad:
                    continue
            else:
                keep = any(w in name for w in ("动漫", "二次元", "动画", "ACG", "acg", "新番"))
                if not keep:
                    continue
            item = {"id": p["id"], "name": name, "tc": tc,
                    "creator": (p.get("creator") or {}).get("nickname", "")}
            good.append(item)
            print(f"{key} + [{tc}] {name} @{item['creator']}")
        time.sleep(1.2)
    # 保留全部（最多40），排序交给 step1e
    mf[key] = good[:40]
json.dump(mf, open("manifest1c.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("STEP1D DONE")
