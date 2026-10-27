# Khassida Dataset API

Un dataset strutturato dei Khassida di Serigne Touba, ottimizzato per la recitazione e lo studio, con un'organizzazione ispirata a [alquran.cloud](https://alquran.cloud/api) ma semplificata per la poesia araba.

L'API è **statica**: ogni endpoint è un file JSON già generato, servito gratuitamente da jsDelivr (o da `raw.githubusercontent.com`). Non serve nessun server.

## Endpoint

Base URL:

```
https://cdn.jsdelivr.net/gh/DaurDiop/khassida_dataset@main/v1
```

| Endpoint | Contenuto |
|---|---|
| `/editions.json` | Edizioni disponibili (testo arabo, trascrizione, traduzioni) |
| `/khassidas.json` | Elenco delle 193 khassida con metadati ed edizioni disponibili |
| `/khassida/{number}.json` | Khassida completa con tutte le edizioni |
| `/khassida/{number}/{edition}.json` | Khassida con una sola edizione (es. `/khassida/9/it.karamati.json`) |

Ogni risposta usa la stessa busta di alquran.cloud:

```json
{ "code": 200, "status": "OK", "data": { ... } }
```

Esempio:

```js
const res = await fetch("https://cdn.jsdelivr.net/gh/DaurDiop/khassida_dataset@main/v1/khassida/9/it.karamati.json");
const { data } = await res.json();
data.bayts.forEach(b => console.log(b.number, b.text));
```

Per fissare una versione stabile sostituisci `@main` con un tag o un commit (es. `@v1.0.0`).

## Edizioni

| Identificatore | Lingua | Unità | Copertura |
|---|---|---|---|
| `khassida-uthmani` | ar | verso | tutte |
| `transliteration` | — | verso | tutte |
| `fr.translation` | fr | verso | quasi tutte |
| `en.translation` | en | verso | parziale |
| `it.karamati` | it | bayt | 16 khassida dell'app Karamati Khatou Yadi |
| `en.karamati` | en | bayt | 16 khassida dell'app Karamati Khatou Yadi |
| `fr.karamati` | fr | bayt | 16 khassida dell'app Karamati Khatou Yadi |

Il campo `editions` in `/khassidas.json` indica quali edizioni sono disponibili per ciascuna khassida.

## Struttura dei dati

Ogni elemento di `verses` è un **segmento** di verso (emistichio). Le traduzioni dell'app [Karamati Khatou Yadi](https://github.com/DaurDiop/karamati-khatou-yadi) traducono invece il **verso intero** (*bayt*, di solito 2 segmenti, 4 in Tawbatun Nasuuh), quindi stanno in un array separato, `bayts`, che indica quali segmenti copre.

```json
{
  "number": 9,
  "name": "Alhamdu Yujaazi",
  "transliterationName": "Alhamdu Yujaazi",
  "meter": "Rajas",
  "verses": [
    {
      "number": 1,
      "text": "الْحَمْدُ لِلَّهِ الَّذِى يُجَازِ",
      "transcription": "al hamdu lil laahil lazii yujaazi",
      "translations": { "fr": "La Louange soit à Dieu qui rétribue ceux qui font du bien," }
    }
  ],
  "bayts": [
    {
      "number": 1,
      "verseFrom": 1,
      "verseTo": 2,
      "text": "الْحَمْدُ لِلَّهِ الَّذِى يُجَازِ ۞ مَنْ أَحْسَنُواْ بِالْخَيْرِ وَالْمَفَازِ",
      "translations": {
        "it.karamati": "La lode appartiene ad Allah, che ricompensa coloro che hanno operato il bene…",
        "en.karamati": "…",
        "fr.karamati": "…"
      }
    }
  ]
}
```

Le khassida divise in più parti nel dataset (es. *Jazbu 1–4*) hanno nei bayt anche `appNumber`, la numerazione continua usata nell'app.

## Struttura del repository

```text
khassida-full.json     sorgente: tutte le khassida con versi e bayt
editions.json          sorgente: elenco delle edizioni
khassidas_meta.json    generato: metadati
v1/                    generato: endpoint dell'API statica
scripts/
  import_karamati.py   importa le traduzioni dall'app Karamati Khatou Yadi
  build_api.py         valida il dataset e rigenera khassidas_meta.json e v1/
```

## Aggiornare il dataset

```bash
# 1. (opzionale) reimporta le traduzioni dell'app
python3 scripts/import_karamati.py ../karamati-khatou-yadi

# 2. valida e rigenera gli endpoint
python3 scripts/build_api.py
```

La CI esegue `python3 scripts/build_api.py --check` a ogni push e fallisce se il dataset non è valido o se `v1/` non è stato rigenerato.

---
*Creato con il supporto di Manus AI per la comunità Mouride.*
