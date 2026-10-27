#!/usr/bin/env python3
"""Valida il dataset e genera l'API statica in `v1/`.

Uso:
    python3 scripts/build_api.py          # valida e rigenera v1/ e khassidas_meta.json
    python3 scripts/build_api.py --check  # valida e verifica che i file generati siano aggiornati

Sorgenti: `khassida-full.json` e `editions.json` (radice del repo).
Endpoint generati (stessa busta {code, status, data} di alquran.cloud):

    v1/editions.json                    elenco delle edizioni
    v1/khassidas.json                   elenco delle khassida con metadati
    v1/khassida/{number}.json           khassida completa (tutte le edizioni)
    v1/khassida/{number}/{edition}.json khassida con una sola edizione
"""
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEXT_EDITION = "khassida-uthmani"
TRANSLIT_EDITION = "transliteration"
VERSE_LANG_EDITION = {"fr": "fr.translation", "en": "en.translation"}


def envelope(data):
    return {"code": 200, "status": "OK", "data": data}


def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate(khassidas, editions):
    errors = []
    ids = {e["identifier"] for e in editions}
    for n, k in enumerate(khassidas, 1):
        name = k.get("name", f"#{n}")
        if k.get("number") != n:
            errors.append(f"{name}: numero {k.get('number')} atteso {n}")
        for i, v in enumerate(k.get("verses", []), 1):
            if v.get("number") != i:
                errors.append(f"{name} verso {i}: numerazione errata")
            if not v.get("text"):
                errors.append(f"{name} verso {i}: testo arabo mancante")
            for lang in v.get("translations", {}):
                if VERSE_LANG_EDITION.get(lang) not in ids:
                    errors.append(f"{name} verso {i}: lingua '{lang}' senza edizione")
        expected = 1
        for j, b in enumerate(k.get("bayts", []), 1):
            if b["number"] != j:
                errors.append(f"{name} bayt {j}: numerazione errata")
            if b["verseFrom"] != expected or b["verseTo"] < b["verseFrom"]:
                errors.append(f"{name} bayt {j}: intervallo versi non contiguo")
            expected = b["verseTo"] + 1
            for ed in b["translations"]:
                if ed not in ids:
                    errors.append(f"{name} bayt {j}: edizione '{ed}' sconosciuta")
        if k.get("bayts") and expected != len(k["verses"]) + 1:
            errors.append(f"{name}: i bayt non coprono tutti i versi")
    if errors:
        sys.exit("Dataset non valido:\n  " + "\n  ".join(errors))


def available_editions(k):
    eds = {TEXT_EDITION}
    for v in k["verses"]:
        if v.get("transcription"):
            eds.add(TRANSLIT_EDITION)
        eds.update(VERSE_LANG_EDITION[l] for l in v.get("translations", {}))
    for b in k.get("bayts", []):
        eds.update(b["translations"])
    return eds


def meta(k, editions):
    order = [e["identifier"] for e in editions]
    return {
        "number": k["number"],
        "name": k["name"],
        "transliterationName": k["transliterationName"],
        "numberOfVerses": len(k["verses"]),
        "numberOfBayts": len(k.get("bayts", [])),
        "meter": k["meter"],
        "editions": sorted(available_editions(k), key=order.index),
    }


def single_edition(k, edition):
    """Khassida ridotta a una sola edizione: `verses` o `bayts` a seconda di dove vive."""
    out = {key: k[key] for key in ("number", "name", "transliterationName", "meter")}
    out["edition"] = edition["identifier"]
    ident = edition["identifier"]
    if ident in (TEXT_EDITION, TRANSLIT_EDITION):
        field = "text" if ident == TEXT_EDITION else "transcription"
        out["verses"] = [{"number": v["number"], "text": v[field]} for v in k["verses"]]
    elif edition.get("unit") == "bayt":
        out["bayts"] = [
            {key: b[key] for key in ("number", "verseFrom", "verseTo", "appNumber") if key in b}
            | {"text": b["translations"][ident]}
            for b in k.get("bayts", [])
            if ident in b["translations"]
        ]
    else:
        lang = edition["language"]
        out["verses"] = [
            {"number": v["number"], "text": v["translations"][lang]}
            for v in k["verses"]
            if lang in v.get("translations", {})
        ]
    return out


def build(out_root):
    khassidas = json.loads((ROOT / "khassida-full.json").read_text(encoding="utf-8"))["data"]["khassidas"]
    editions = json.loads((ROOT / "editions.json").read_text(encoding="utf-8"))["data"]
    validate(khassidas, editions)
    by_id = {e["identifier"]: e for e in editions}

    metas = [meta(k, editions) for k in khassidas]
    dump(out_root / "khassidas_meta.json", envelope(metas))
    dump(out_root / "v1/editions.json", envelope(editions))
    dump(out_root / "v1/khassidas.json", envelope(metas))
    for k, m in zip(khassidas, metas):
        dump(out_root / f"v1/khassida/{k['number']}.json", envelope(k))
        for ident in m["editions"]:
            dump(out_root / f"v1/khassida/{k['number']}/{ident}.json", envelope(single_edition(k, by_id[ident])))
    return len(khassidas)


def tree(root):
    files = [root / "khassidas_meta.json", *sorted((root / "v1").rglob("*.json"))]
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in files if p.exists()}


def main():
    if "--check" in sys.argv:
        with tempfile.TemporaryDirectory() as tmp:
            build(Path(tmp))
            if tree(Path(tmp)) != tree(ROOT):
                sys.exit("I file generati non sono aggiornati: esegui python3 scripts/build_api.py")
        print("OK: dataset valido e API aggiornata")
        return
    shutil.rmtree(ROOT / "v1", ignore_errors=True)
    n = build(ROOT)
    print(f"Generati gli endpoint per {n} khassida in v1/")


if __name__ == "__main__":
    main()
