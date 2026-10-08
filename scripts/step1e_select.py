# -*- coding: utf-8 -*-
"""Step1e v2: robust auto-selection, hard content gates + blacklist."""
import json, re

mf = json.load(open("manifest1c.json", encoding="utf-8"))

ACG_WORDS = ("动漫", "二次元", "动画", "ACG", "acg", "音游", "gal")
HUA_WORDS = ("华语", "中文", "国语", "金曲", "热歌", "新歌", "最热", "热门")
HUA_BLACK = ("Billboard", "billboard", "B榜", "UK", "欧美", "英文", "DJ", "KPOP", "K-POP",
             "melon", "音源", "韩国", "日本", "iTunes", "跑步", "Hardstyle", "Dubstep",
             "DJMag", "电音", "榜单DJ", "Apple", "YOUTOBE", "YouTube", "Vocaloid", "盐浦")
ACG_BLACK = ("印度歌",)

ACG = ["百首好听的动漫歌曲", "动漫推荐TOP100", "最具人气的动漫歌曲", "最具人气动漫歌曲",
       "动漫歌曲人气榜", "人气动漫歌曲", "ACG动漫歌曲排行", "iTunes", "补番推荐",
       "动漫歌曲精选", "动漫op、ed、插曲", "人气榜TOP100", "二次元热曲", "动感新势力", "动漫"]
HUA = ["年度最热新歌TOP100", "年度最热新歌", "年度最热歌曲", "年度热议单曲",
       "最热歌曲", "华语年终榜", "华语精选", "华语乐坛经典", "热歌榜", "华语金曲",
       "华语歌曲排行榜", "华语", "中文", "热歌", "金曲"]

def cross_year(name, y):
    yrs = {int(s) for s in re.findall(r"20\d\d", name)}
    yrs.discard(y)
    return bool(yrs)

final, rows = {}, []
for y in range(2010, 2021):
    for cat in ("hua", "acg"):
        cands = mf.get(f"{y}_{cat}", [])
        pr = HUA if cat == "hua" else ACG
        gate = HUA_WORDS if cat == "hua" else ACG_WORDS
        black = HUA_BLACK if cat == "hua" else ACG_BLACK
        scored = []
        for c in cands:
            name = c["name"]
            if not any(w in name for w in gate):
                continue
            if any(b in name for b in black):
                continue
            if cat == "hua" and not any(w in name for w in gate):
                continue
            tiers = [i for i, pat in enumerate(pr) if pat in name]
            if not tiers and cat == "hua":
                continue
            tier = min(tiers) if tiers else len(pr)
            pen = 1 if cross_year(name, y) else 0
            official = 0 if c["creator"] == "网易云音乐" else 1
            tcpen = (abs(c["tc"] - 100) ** 1.5) * 0.08
            score = tier * 2 + pen * 4 + official + tcpen
            scored.append((score, c["id"], c))
        if scored:
            scored.sort(key=lambda t: t[0])
            _, _, c = scored[0]
            warn = " ★跨年混合" if cross_year(c["name"], y) else ""
            final[f"{y}_{cat}"] = {"pid": c["id"], "name": c["name"], "creator": c["creator"], "tc": c["tc"]}
            rows.append(f"{y} {cat}: {c['id']} tc={c['tc']} 《{c['name'][:40]}》 by {c['creator'][:12]}{warn}")
        else:
            final[f"{y}_{cat}"] = None
            rows.append(f"{y} {cat}: ★无候选")
json.dump({k: (v or {}) for k, v in final.items()}, open("final_manifest.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
open("step1e_summary.txt", "w", encoding="utf-8").write("\n".join(rows))
print("OK " + str(sum(1 for v in final.values() if v)) + "/22")
