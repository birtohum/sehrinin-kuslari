"use strict";
const $ = (id) => document.getElementById(id);
const sayi = (x) => Math.round(x).toLocaleString("tr-TR");
const AY = ["Oca", "Şub", "Mar", "Nis", "May", "Haz", "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"];
const AYTAM = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"];
const NS = "http://www.w3.org/2000/svg";
let V, H, il = 33, ay = new Date().getMonth();

const ad = (i) => V.turler[i][1] || V.turler[i][0];
const bil = (i) => V.turler[i][0];
function ekDe(s) {
  const k = s.toLocaleLowerCase("tr"), sesli = [...k].reverse().find((h) => "aıoueiöü".includes(h));
  return `${s}'${"fstkçşhp".includes(k.slice(-1)) ? "t" : "d"}${"aıou".includes(sesli) ? "a" : "e"}`;
}

function takvim() {
  let h = `<span></span>${AY.map((a) => `<span class="ay">${a}</span>`).join("")}`;
  for (const i of V.takvim) {
    const s = V.tr.tur[i], top = s.reduce((a, b) => a + b, 0), enb = Math.max(...s);
    h += `<span class="ad" title="${bil(i)}">${ad(i)}<small>${bil(i)}</small></span>`;
    h += s.map((n, m) => `<i style="background:color-mix(in oklab, var(--hucre1) ${Math.round(100 * Math.pow(n / enb, 0.8))}%, var(--hucre0))" title="${ad(i)}, ${AYTAM[m]}: kayıtların %${Math.round((100 * n) / top)}'i"></i>`).join("");
  }
  $("takvim").innerHTML = h;
}

function ilGoster() {
  const I = V.iller[il], ayKayit = I.kayit[ay], yilKayit = I.kayit.reduce((a, b) => a + b, 0);
  const turlar = Object.entries(I.t).map(([k, s]) => ({ k: Number(k), s, n: s[ay], top: s.reduce((a, b) => a + b, 0) }));
  const buAy = turlar.filter((x) => x.n > 0).sort((a, b) => b.n - a.n);
  const pencere = (s) => s[(ay + 11) % 12] + s[ay] + s[(ay + 1) % 12];
  const puan = (x) => (pencere(x.s) / x.top) * Math.log(1 + x.n);
  const misafir = turlar.filter((x) => x.top >= 30 && x.n >= 5 && pencere(x.s) / x.top > 0.5).sort((a, b) => puan(b) - puan(a));
  $("ilOzet").innerHTML = yilKayit < 50
    ? `${ekDe(H.iller[il].ad)} çok az gözlem kaydı var (${sayi(yilKayit)}). Liste güvenilir olmayacak kadar kısa; komşu bir ile bakmayı dene.`
    : `Bütün yılların ${AYTAM[ay].toLocaleLowerCase("tr")} aylarında ${ekDe(H.iller[il].ad)} <b>${buAy.length}</b> kuş türü kaydedilmiş (${sayi(ayKayit)} gözlem). Yıl boyunca bu ilde toplam ${Object.keys(I.t).length} tür görülmüş.`;
  $("listeBaslik").textContent = `${AYTAM[ay]} ayında en çok görülenler`;
  const satir = (x) => `<li><span><span class="tr">${ad(x.k)}</span>${V.turler[x.k][1] ? `<span class="bil">${bil(x.k)}</span>` : ""}</span><span></span><span class="n">${sayi(x.n)}</span></li>`;
  $("liste").innerHTML = buAy.slice(0, 12).map(satir).join("") || "<li><span>Bu ay için kayıt yok.</span></li>";
  $("misafir").innerHTML = misafir.slice(0, 12).map(satir).join("") || "<li><span>Bu ay belirgin bir mevsimlik tür yok.</span></li>";
  document.querySelectorAll(".liste li").forEach((li) => (li.style.gridTemplateColumns = "26px 1fr 0 64px"));
  [...$("aylar").children].forEach((b, m) => { b.classList.toggle("secili", m === ay); b.setAttribute("aria-checked", m === ay); });
  $("il").value = il;
  [...$("harita").querySelectorAll("path")].forEach((e) => (e.style.stroke = Number(e.dataset.i) === il ? "var(--vurgu)" : ""));
  history.replaceState(null, "", `?il=${il + 1}&ay=${ay + 1}`);
}

function harita() {
  const s = $("harita"); s.setAttribute("viewBox", `0 0 ${H.w} ${H.h}`);
  const n = V.iller.map((x) => Object.keys(x.t).length), enb = Math.max(...n);
  H.iller.forEach((p, i) => {
    const e = document.createElementNS(NS, "path"); e.setAttribute("d", p.d); e.dataset.i = i;
    e.style.fill = `color-mix(in oklab, var(--hucre1) ${Math.round(100 * Math.sqrt(n[i] / enb))}%, var(--kara))`;
    const t = document.createElementNS(NS, "title"); t.textContent = `${p.ad}: ${n[i]} tür`; e.appendChild(t);
    e.onclick = () => { il = i; ilGoster(); $("ilOzet").scrollIntoView({ behavior: "smooth", block: "center" }); };
    s.appendChild(e);
  });
  H.iller.forEach((p, i) => { const t = document.createElementNS(NS, "text"); t.setAttribute("x", p.x); t.setAttribute("y", p.y + 3); t.setAttribute("text-anchor", "middle"); t.textContent = n[i]; s.appendChild(t); });
}

async function baslat() {
  [V, H] = await Promise.all([fetch("veri/kuslar.json").then((r) => r.json()), fetch("veri/harita.json").then((r) => r.json())]);
  $("kayitSay").textContent = sayi(V.tr.kayit.reduce((a, b) => a + b, 0));
  $("turSay").textContent = sayi(Object.keys(V.tr.tur).length);
  [...H.iller.keys()].sort((a, b) => H.iller[a].ad.localeCompare(H.iller[b].ad, "tr")).forEach((i) => $("il").add(new Option(H.iller[i].ad, i)));
  AY.forEach((a, m) => { const b = document.createElement("button"); b.textContent = a; b.setAttribute("role", "radio"); b.onclick = () => { ay = m; ilGoster(); }; $("aylar").appendChild(b); });
  const p = new URLSearchParams(location.search);
  if (Number(p.get("il")) >= 1 && Number(p.get("il")) <= 81) il = Number(p.get("il")) - 1;
  if (Number(p.get("ay")) >= 1 && Number(p.get("ay")) <= 12) ay = Number(p.get("ay")) - 1;
  $("il").onchange = (e) => { il = Number(e.target.value); ilGoster(); };
  takvim(); harita(); ilGoster();
}
baslat();
