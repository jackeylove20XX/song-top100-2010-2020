# -*- coding: utf-8 -*-
"""Step2: fetch chosen playlists' full tracks per (year, category) -> data/*.json"""
import json, os, sys, time
from pyncm.apis import playlist
import pyncm

pyncm.SetNewSession()

def fetch_tracks(pid, max_n=120):
    tracks, offset = [], 0
    while len(tracks) < max_n:
        batch = playlist.GetPlaylistAllTracks(pid, limit=100, offset=offset)
        songs = batch.get("songs", [])
        if not songs:
            break
        for s in songs:
            if len(tracks) >= max_n:
                break
            ar = s.get("ar") or s.get("artists") or []
            al = s.get("al") or s.get("album") or {}
            tracks.append({"id": s["id"], "name": s.get("name", ""),
                           "artist": "/".join(a.get("name", "") for a in ar[:3]),
                           "album": al.get("name", ""), "fee": s.get("fee", 0)})
        offset += 100
        time.sleep(1.2)
    return tracks

def run(manifest_file, outdir="data"):
    os.makedirs(outdir, exist_ok=True)
    mf = json.load(open(manifest_file, encoding="utf-8"))
    report = []
    for key, chosen in mf.items():
        year, cat = key.rsplit("_", 1)
        if not chosen or not chosen.get("pid"):
            report.append(f"{key}: SKIP(no pid)")
            continue
        pid, pname, creator = chosen["pid"], chosen.get("name", ""), chosen.get("creator", "")
        try:
            tracks = fetch_tracks(pid)
        except Exception as e:
            report.append(f"{key}: FAIL {repr(e)[:80]}")
            continue
        for i, t in enumerate(tracks, 1):
            t["rank"] = i
        out = {"year": int(year), "cat": cat, "pid": pid, "pname": pname, "creator": creator,
               "fetched": len(tracks), "tracks": tracks[:100]}
        with open(f"{outdir}/{key}.json", "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
        report.append(f"{key}: OK pid={pid} fetched={len(tracks)} first='{tracks[0]['name']}-{tracks[0]['artist']}' last='{tracks[len(tracks)-1]['name']}'")
        time.sleep(2.0)
    open("step2_report.txt", "w", encoding="utf-8").write("\n".join(report))
    print("STEP2 DONE", len(report))

if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else "final_manifest.json")
