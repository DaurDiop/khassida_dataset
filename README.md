# Khassida Dataset API (Custom Serigne Touba Style)

Un dataset strutturato dei Khassida di Serigne Touba, ottimizzato per la recitazione e lo studio, con un'organizzazione ispirata a `alquran.cloud` ma semplificata per la poesia araba.

## Caratteristiche
- **Testo Arabo Uthmani**: Formattato per la massima leggibilità tradizionale.
- **Metadati Poetici**: Include il numero progressivo del Khassida, il nome arabo e la translitterazione.
- **Versi Puliti**: Ogni verso contiene solo il testo arabo, la trascrizione fonetica e le traduzioni (fr, en, ecc.).
- **Senza Campi Coranici**: Rimosse informazioni non pertinenti come `juz`, `page`, `sajda`, ecc.

## Struttura del Repository
```text
/v1
  /editions.json      - Versioni disponibili (Arabo, Traduzioni, Trascrizione)
  /khassidas_meta.json - Elenco dei Khassida con metadati (numero, nome, metrica)
  /khassida-full.json  - Dataset completo con tutti i versi e le traduzioni
```

## Esempio di Struttura Verso
```json
{
  "number": 5,
  "text": "وَجَّهْتُ كُلَّ الْحَمْدِ وَالشُّكُورِ",
  "transcription": "Wajjahtu kulla-l hamdi wa-sh shukuri",
  "translations": {
    "fr": "J'ai dirigé toutes les louanges et remerciements..."
  }
}
```

## Utilizzo
I file JSON sono pronti per essere caricati in un database (MongoDB, PostgreSQL) o serviti tramite un'API REST personalizzata.

---
*Creato con il supporto di Manus AI per la comunità Mouride.*
