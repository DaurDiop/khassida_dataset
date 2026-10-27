#!/usr/bin/env python3
"""Importa le traduzioni it/en/fr dell'app Karamati Khatou Yadi nel dataset.

Uso:
    python3 scripts/import_karamati.py /percorso/karamati-khatou-yadi

Importa solo le khassida pubblicate nell'app (quelle con traduzione it, en
e fr in `traduzioni/`). Le altre khassida del dataset restano invariate.

Nell'app ogni traduzione copre un verso intero (bayt), mentre nel dataset
ogni elemento di `verses` è un segmento (emistichio). Le traduzioni vengono
quindi salvate in un nuovo array `bayts` di ogni khassida; ogni bayt indica
quali `verses` copre (`verseFrom`..`verseTo`). Le khassida divise in più parti
nel dataset (es. "Jazbu 1".."Jazbu 4") vengono allineate in sequenza;
`appNumber` conserva la numerazione continua dell'app.

L'allineamento viene verificato confrontando il testo arabo (senza
diacritici): se un segmento differisce lo script lo segnala, e si ferma se
la somiglianza è troppo bassa.
"""
import difflib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FULL = ROOT / "khassida-full.json"
LANGS = ("it", "en", "fr")
EDITION = "{}.karamati"
MIN_SIMILARITY = 0.85


def norm(s):
    s = re.sub(r"[ً-ٰٟۖ-ۭ]", "", s)
    s = re.sub(r"[^ء-ي]", "", s)
    return s.replace("ى", "ي").replace("ٱ", "ا")


def base_name(name):
    return re.sub(r"_\d+$", "", name.lower().replace(" ", "_"))


def read_translation(path):
    rows = {}
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        n, ar, tr = (p.strip() for p in line.split(" | ", 2))
        rows[int(n)] = (ar, tr)
    return rows


def main(app_dir):
    app_dir = Path(app_dir)
    full = json.loads(FULL.read_text(encoding="utf-8"))
    khassidas = full["data"]["khassidas"]

    ids = sorted(p.name[: -len("-it.txt")] for p in (app_dir / "traduzioni/it").glob("*-it.txt"))
    warnings = []
    for app_id in ids:
        tr = {l: read_translation(app_dir / f"traduzioni/{l}/{app_id}-{l}.txt") for l in LANGS}
        parts = [k for k in khassidas if base_name(k["name"]) == app_id]
        if not parts:
            sys.exit(f"{app_id}: nessuna khassida corrispondente nel dataset")
        for k in parts:
            k["bayts"] = []
        segments = [(k, v) for k in parts for v in k["verses"]]

        pos = 0
        for n in sorted(tr["it"]):
            ar = tr["it"][n][0]
            segs = [s for s in re.split(r"[۞•]", ar) if norm(s)]
            chunk = segments[pos : pos + len(segs)]
            if len(chunk) < len(segs):
                sys.exit(f"{app_id} v{n}: il dataset ha meno segmenti dell'app")
            part = chunk[0][0]
            if any(k is not part for k, _ in chunk):
                sys.exit(f"{app_id} v{n}: il verso attraversa due parti del dataset")
            for s, (k, v) in zip(segs, chunk):
                sim = difflib.SequenceMatcher(None, norm(s), norm(v["text"])).ratio()
                if sim < MIN_SIMILARITY:
                    sys.exit(f"{app_id} v{n}: testo non allineato ({sim:.2f})\n  app: {s}\n  dataset: {v['text']}")
                if sim < 1:
                    warnings.append(f"{k['name']} verso {v['number']}: dataset «{v['text']}» / app «{s.strip()}»")
            bayt = {
                "number": len(part["bayts"]) + 1,
                "verseFrom": chunk[0][1]["number"],
                "verseTo": chunk[-1][1]["number"],
                "text": " ۞ ".join(v["text"] for _, v in chunk),
                "translations": {EDITION.format(l): tr[l][n][1] for l in LANGS if n in tr[l]},
            }
            if len(parts) > 1:
                bayt["appNumber"] = n
            part["bayts"].append(bayt)
            pos += len(segs)
        if pos != len(segments):
            sys.exit(f"{app_id}: {len(segments) - pos} segmenti del dataset non coperti dall'app")
        print(f"{app_id}: {len(tr['it'])} versi -> {', '.join(k['name'] for k in parts)}")

    FULL.write_text(json.dumps(full, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for w in warnings:
        print("ATTENZIONE (testo diverso):", w)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
