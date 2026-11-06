"""GBIF → Türkiye kuş gözlemleri: il × ay × tür kayıt sayıları + Türkçe adlar. Yanıtlar ham/ altında önbelleklenir."""
import json, time, urllib.parse, urllib.request
from pathlib import Path
KOK = Path(__file__).resolve().parent.parent
HAM = KOK / "ham"; HAM.mkdir(exist_ok=True)
UA = "sehrinin-kuslari (github.com/birtohum/sehrinin-kuslari)"
def al(yol, **q):
    f = HAM / (yol.replace("/", "_") + "_" + "_".join(f"{k}-{v}" for k, v in sorted(q.items())).replace(".", "-")[:150] + ".json")
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    url = f"https://api.gbif.org/v1/{yol}?" + urllib.parse.urlencode(q)
    for d in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60) as r:
                j = json.loads(r.read().decode("utf-8")); break
        except Exception as e:
            print("hata", e, url, flush=True); time.sleep(5 * (d + 1))
    else:
        return None
    f.write_text(json.dumps(j, ensure_ascii=False), encoding="utf-8"); time.sleep(0.4)
    return j
# 1) GADM il kimlikleri → ad
gid = {}
for i in range(1, 90):
    g = f"TUR.{i}_1"
    j = al("occurrence/search", country="TR", gadmGid=g, limit=1)
    if j and j["results"]:
        gid[g] = j["results"][0]["gadm"]["level1"]["name"]
print(len(gid), "il", flush=True)
# 2) il × ay tür sayımları (kuşlar = taxonKey 212)
tur = set()
for g in gid:
    for ay in range(1, 13):
        j = al("occurrence/search", country="TR", taxonKey=212, gadmGid=g, month=ay, limit=0, facet="speciesKey", facetLimit=400)
        if j and j["facets"]:
            for c in j["facets"][0]["counts"]:
                tur.add(c["name"])
    print(g, gid[g], len(tur), flush=True)
# 3) Türkiye geneli ay × tür
for ay in range(1, 13):
    j = al("occurrence/search", country="TR", taxonKey=212, month=ay, limit=0, facet="speciesKey", facetLimit=600)
    for c in j["facets"][0]["counts"]:
        tur.add(c["name"])
print("tür", len(tur), flush=True)
# 4) tür adları (bilimsel + Türkçe)
for k in sorted(tur):
    al(f"species/{k}")
    al(f"species/{k}/vernacularNames", limit=100)
json.dump(gid, open(KOK / "ham/gadm_iller.json", "w", encoding="utf-8"), ensure_ascii=False)
print("bitti", flush=True)
