"""ham/ (GBIF önbelleği) → veri/kuslar.json"""
import json, re, unicodedata
from pathlib import Path
KOK = Path(__file__).resolve().parent.parent
HAM = KOK / "ham"

def oku(ad):
    f = HAM / ad
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else None
def anahtar(yol, **q):
    return yol.replace("/", "_") + "_" + "_".join(f"{k}-{v}" for k, v in sorted(q.items())).replace(".", "-")[:150] + ".json"

def sade(s):
    s = s.replace("İ", "I").replace("ı", "i")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z]", "", s)

iller = json.load(open(KOK / "../alti-ipucu/araclar/iller.json", encoding="utf-8"))  # [plaka, ad, lat, lon]
plaka = {sade(a): k for k, a, _, _ in iller}
EK = {"afyon": 3, "kmaras": 46, "kahramanmaras": 46, "zinguldak": 67, "zonguldak": 67, "icel": 33, "mersin": 33, "sanliurfa": 63, "hakkari": 30, "kinkkale": 71, "kirikkale": 71, "karabuk": 78, "bartin": 74, "duzce": 81}
gid = {}
for i in range(1, 90):
    j = oku(anahtar("occurrence/search", country="TR", gadmGid=f"TUR.{i}_1", limit=1))
    if j and j["results"]:
        ad = j["results"][0]["gadm"]["level1"]["name"]
        k = plaka.get(sade(ad)) or EK.get(sade(ad))
        if not k:
            print("eşleşmedi:", f"TUR.{i}_1", ad)
        gid[f"TUR.{i}_1"] = k
assert len(set(gid.values()) - {None}) == 81, sorted(set(range(1, 82)) - set(gid.values()))

tur_ix, turler = {}, []
def ix(k):
    if k not in tur_ix:
        tur_ix[k] = len(turler); turler.append(k)
    return tur_ix[k]

ilv = [{"kayit": [0] * 12, "t": {}} for _ in range(81)]
for g, k in gid.items():
    for ay in range(1, 13):
        j = oku(anahtar("occurrence/search", country="TR", taxonKey=212, gadmGid=g, month=ay, limit=0, facet="speciesKey", facetLimit=400))
        if not j:
            continue
        d = ilv[k - 1]
        d["kayit"][ay - 1] = j["count"]
        for c in (j["facets"][0]["counts"] if j["facets"] else []):
            s = d["t"].setdefault(ix(c["name"]), [0] * 12); s[ay - 1] = c["count"]
tr = {"kayit": [0] * 12, "tur": {}}
for ay in range(1, 13):
    j = oku(anahtar("occurrence/search", country="TR", taxonKey=212, month=ay, limit=0, facet="speciesKey", facetLimit=600))
    tr["kayit"][ay - 1] = j["count"]
    for c in j["facets"][0]["counts"]:
        s = tr["tur"].setdefault(ix(c["name"]), [0] * 12); s[ay - 1] = c["count"]

# adlar
adlar = []
for k in turler:
    sp = oku(anahtar(f"species/{k}")) or {}
    vn = oku(anahtar(f"species/{k}/vernacularNames", limit=100)) or {"results": []}
    trad = [v["vernacularName"].strip() for v in vn["results"] if v.get("language") in ("tur", "tr") and v.get("vernacularName")]
    # Türkçe harf içeren ve çok kelimeli olmayan adı tercih et; büyük/küçük harfi düzelt
    trad.sort(key=lambda a: (not any(h in a for h in "çğıöşüÇĞİÖŞÜ"), len(a)))
    bil = sp.get("canonicalName") or sp.get("scientificName") or str(k)
    t = None
    if trad:
        a = trad[0].replace("I", "ı").replace("İ", "i").lower()
        t = a[0].replace("i", "İ").upper() + a[1:]
    adlar.append([bil, t, sp.get("class") == "Aves"])

# Yaygın Türkçe adlar (GBIF'te eksik ya da hatalı yazılanlar)
ELLE = {"Ciconia ciconia": "Leylek", "Phoenicopterus roseus": "Flamingo", "Hirundo rustica": "Kır kırlangıcı", "Merops apiaster": "Arıkuşu",
        "Grus grus": "Turna", "Apus apus": "Ebabil", "Pelecanus onocrotalus": "Ak pelikan", "Platalea leucorodia": "Kaşıkçı", "Cuculus canorus": "Guguk kuşu",
        "Oriolus oriolus": "Sarıasma", "Upupa epops": "İbibik", "Coracias garrulus": "Gökkuzgun", "Ciconia nigra": "Kara leylek", "Pernis apivorus": "Arı şahini",
        "Luscinia megarhynchos": "Bülbül", "Fringilla montifringilla": "Dağ ispinozu", "Tadorna ferruginea": "Angut", "Anas crecca": "Çamurcun",
        "Acrocephalus scirpaceus": "Saz kamışçını", "Parus major": "Büyük baştankara", "Aquila pomarina": "Küçük orman kartalı", "Aquila clanga": "Büyük orman kartalı", "Cyanistes caeruleus": "Mavi baştankara", "Columba livia": "Kaya güvercini", "Streptopelia decaocto": "Kumru"}
for a in adlar:
    if a[0] in ELLE:
        a[1] = ELLE[a[0]]
    elif a[1]:
        a[1] = a[1].replace("Calı", "Çalı").replace("calı", "çalı")

# takvim: ulusal kaydı ≥ 1500, mevsimselliği yüksek, Türkçe adlı türler; zirve ayına göre sıralı
aday = []
for i, s in tr["tur"].items():
    t = sum(s)
    if t < 1500 or not adlar[i][1]:
        continue
    pay = max(s) / t
    aday.append((pay, i, s.index(max(s))))
import math
UNLU = ["Ciconia ciconia", "Phoenicopterus roseus", "Hirundo rustica", "Merops apiaster", "Grus grus", "Apus apus", "Pelecanus onocrotalus",
        "Platalea leucorodia", "Cuculus canorus", "Oriolus oriolus", "Upupa epops", "Coracias garrulus", "Ciconia nigra", "Pernis apivorus", "Luscinia megarhynchos", "Fringilla montifringilla", "Tadorna ferruginea", "Anas crecca"]
bilden = {a[0]: i for i, a in enumerate(adlar)}
zorunlu = [bilden[b] for b in UNLU if b in bilden and str(bilden[b]) in map(str, tr["tur"]) or (b in bilden and bilden[b] in tr["tur"])]
aday.sort(key=lambda x: -x[0] * math.log(sum(tr["tur"][x[1]])))
secim = list(dict.fromkeys(zorunlu + [i for _, i, _ in aday]))[:30]
zirve = {i: tr["tur"][i].index(max(tr["tur"][i])) for i in secim}
takvim = sorted(secim, key=lambda i: (zirve[i], -max(tr["tur"][i]) / sum(tr["tur"][i])))
cikti = {"turler": [a[:2] for a in adlar], "tr": tr, "iller": ilv, "takvim": takvim}
(KOK / "veri").mkdir(exist_ok=True)
json.dump(cikti, open(KOK / "veri/kuslar.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("tür", len(turler), "Türkçe adlı", sum(1 for a in adlar if a[1]), "ulusal kayıt", sum(tr["kayit"]))
print("takvim:", [adlar[i][1] for i in takvim])
print("il tür sayısı min/max", min(len(x["t"]) for x in ilv), max(len(x["t"]) for x in ilv))
