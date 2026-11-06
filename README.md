# Şehrinde hangi kuşlar var?

**Canlı:** https://birtohum.github.io/sehrinin-kuslari/

Türkiye'deki 3,34 milyon kuş gözlem kaydına dayanan bir göç takvimi. Bir il ve ay seçince şunlar görünür:

- o ay en çok görülen türler;
- o ayın "misafirleri": o ilde kayıtlarının yarısından fazlası o aya ve komşu iki aya düşen türler.

Ayrıca bir harita her ilde kaç tür kaydedildiğini gösterir.

## Veri

- **Kaynak:** GBIF.org Occurrence API'den, Kasım 2026'da çekildi. Kayıtların çoğu eBird, iNaturalist ve izleme programlarından geliyor.
- **Ne kullanıldı:** Yalnızca sayılar, yani il × ay × tür kayıt sayıları (GADM il sınırları). Kayıt düzeyinde veri yayımlanmıyor.
- **Nasıl toplandı:** `araclar/topla.py` yaklaşık 2.200 istekle topladı. Yanıtlar `ham/` klasöründe önbelleğe alındı.
- **Türkçe adlar:** GBIF'teki yerel adlardan alındı. Yaygın türlerin adları elle düzeltildi. Türkçe adı olmayan türler bilimsel adıyla gösteriliyor.

## Sonuçlar

- 567 tür kaydedilmiş. İl başına tür sayısı 103 ile 392 arasında; en çok tür İstanbul'da.
- İstanbul'da nisanda 297 tür kaydı var. Nisanın mevsimlik misafirleri arasında kara sinekkapan, bülbül, leylek ve ibibik bulunuyor.

## Sınırlar

- **Gözlem, sayım değil:** Bunlar gözlem kayıtlarıdır, kuş sayımı değildir. Çok kayıt, gözlemcinin çok olduğu yeri de gösterebilir.
- **Takvimin ölçeği:** Takvim her türü kendi içinde ölçekler. Bir türün ne zaman geldiğini gösterir, ne kadar olduğunu değil.

## Lisans

Kod Apache-2.0. Veri: GBIF.org (CC0, CC BY ve CC BY-NC veri setleri; burada toplu sayılar kullanıldı). Harita il sınırları geoBoundaries'ten (CC BY-SA 2.0).
