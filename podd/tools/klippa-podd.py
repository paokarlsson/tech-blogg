#!/usr/bin/env python3
"""klippa-podd.py — fas 3 av tre. Klipparen sållar fram godbitarna.

    python3 podd/tools/klippa-podd.py podd/<slug>.plan.json --torrkor
    python3 podd/tools/klippa-podd.py podd/<slug>.plan.json

Klipparen får det råa bandet ett segment i taget, numrerat, och svarar med vilka
turnummer som överlever. Hen **får bara ta bort** — aldrig skriva om, aldrig slå
ihop två repliker, aldrig byta ordning.

Det är inte estetik. Varje sakpåstående i bandet är spårbart till källtexten, och
en omskriven replik har ingen källa längre. Klipparen som får redigera språk blir
också klipparen som råkar förbättra ett argument, och då är spårbarheten borta.

Ankarcitatet är undantaget som skyddas i kod: hittar klipparen på att klippa bort
turen som bär det tvingas den tillbaka in, och sades det aldrig i studion läggs
det till som citatrad efter sista repliken.

Ut:
    podd/<slug>.klippt.md   ← går direkt in i podd/tools/rosta-podd.js
"""

import argparse
import json
from pathlib import Path

from llm import Budget, Logg, MODELL, PODD, ROT, kalla_json, las

KLIPP_SCHEMA = {
    "type": "object",
    "properties": {
        "behall": {"type": "array", "items": {"type": "integer"}},
        "hojdpunkt": {"type": "integer"},
        "motivering": {"type": "string", "maxLength": 500},
    },
    "required": ["behall", "hojdpunkt", "motivering"],
    "additionalProperties": False,
}

KLIPP_SYSTEM = """Du är klippare. Du får ett rått band från en poddinspelning och
ska välja vad som överlever till sändning.

Du FÅR BARA TA BORT. Du skriver aldrig om en replik, slår aldrig ihop två, byter
aldrig ordning. Skälet är inte estetiskt: varje påstående i bandet är spårbart
till källtexten, och en omskriven replik har ingen källa längre.

Du svarar med JSON. "behall" är en stigande lista av turnummer som ska vara kvar.

BEHÅLL:
– turen där någon faktiskt ändrar sig, eller vägrar på ett avslöjande sätt
– den första repliken som sätter oenigheten, och den sista som landar segmentet
– skämt som bara den ena av dem kunde ha sagt
– turen som innehåller ankarcitatet, alltid, orörd
– frågan om du behåller svaret, och svaret om du behåller frågan
– ett minne eller en historia som faktiskt kostar talaren något att berätta

KLIPP:
– uppvärmning. De första turerna är nästan alltid folk som hittar tonen.
– varje tur som säger samma sak som en tidigare tur, även bättre formulerad
– artighet, erkännanden som inte kostar något, transportsträckor
– turer som förklarar ett skämt som redan tagit
– historier som blev en poäng i stället för ett minne
– allt som blir obegripligt om man inte hört något du redan klippt bort

Sikta på segmentets ordbudget. Hellre för kort: ett segment som slutar en replik
för tidigt låter medvetet, ett som slutar en replik för sent låter oredigerat.

"hojdpunkt" är turnumret du skulle klippa ut som trailer för avsnittet."""


def kor_klippning(seg, turer, args, budget: Budget, logg: Logg) -> list:
    nummer, tema = seg.get("nummer", "??"), seg.get("tema", "")
    ankare = seg.get("ankare", [])
    ordbudget = seg.get("ordbudget", 450)
    if not turer:
        return []

    band = "\n".join(f"[{i}] {t['roll']}: {t['replik']}" for i, t in enumerate(turer, 1))
    ord_in = sum(len(t["replik"].split()) for t in turer)

    if args.torrkor:
        print(f"  segment {nummer}: {len(turer)} turer, {ord_in} ord, "
              f"budget {ordbudget} ord")
        return turer

    user = (
        f"SEGMENT {nummer} · {tema}\n"
        f"Segmentets tes: {seg.get('tes', '')}\n"
        f"Konfliktform: {seg.get('konfliktform', 'duell')}\n"
        f"Enligt planen ska {seg.get('vinnare', 'ingen')} stå kvar starkast här.\n"
        f"Ankarcitat som måste finnas kvar ordagrant: {ankare or '(inget)'}\n"
        f"Ordbudget: {ordbudget} ord. Bandet är {ord_in} ord i {len(turer)} turer.\n\n"
        f"RÅTT BAND:\n{band}\n\n"
        f"Välj vilka turnummer som överlever."
    )
    klipp = kalla_json(KLIPP_SYSTEM, user, budget, KLIPP_SCHEMA,
                       modell=args.modell, effort=args.effort, max_tokens=16000,
                       cacha_system=False)

    giltiga = sorted({i for i in klipp.get("behall", []) if 1 <= i <= len(turer)})
    if not giltiga:
        print(f"  ⚠ klipparen behöll inget i segment {nummer} — behåller bandet orört")
        giltiga = list(range(1, len(turer) + 1))

    # Ankaret är segmentets ankare även när klipparen glömmer det.
    for citat in ankare:
        if citat[:40] in " ".join(turer[i - 1]["replik"] for i in giltiga):
            continue
        barare = next((i for i, t in enumerate(turer, 1) if citat[:40] in t["replik"]), None)
        if barare:
            giltiga = sorted(set(giltiga) | {barare})
            print(f"  ↩ tvingade tillbaka tur {barare} — den bär ankarcitatet")

    kvar = [turer[i - 1] for i in giltiga]
    ord_kvar = sum(len(t["replik"].split()) for t in kvar)
    hojd = klipp.get("hojdpunkt")

    logg.skriv({"fas": "klippning", "segment": nummer, "turer_in": len(turer),
                "turer_kvar": len(kvar), "ord_in": ord_in, "ord_kvar": ord_kvar,
                "ordbudget": ordbudget, "behall": giltiga, "hojdpunkt": hojd,
                "motivering": klipp.get("motivering", ""),
                "usd": round(budget.spenderat, 4)})

    print(f"\n─── {nummer} · {tema} " + "─" * 34)
    print(f"  {len(turer)} turer → {len(kvar)}   ·   {ord_in} → {ord_kvar} ord "
          f"(budget {ordbudget})")
    print(f"  {klipp.get('motivering', '')[:200]}")
    if hojd and 1 <= hojd <= len(turer):
        print(f"  ★ {turer[hojd - 1]['roll']}: {turer[hojd - 1]['replik'][:70]}")

    # Sades ankaret aldrig läggs det som citatrad. rosta-podd.js fogar en
    # `>`-rad till föregående talare, så den hamnar hos den som talade sist.
    sagt = " ".join(t["replik"] for t in kvar)
    saknade = [c for c in ankare if c[:40] not in sagt]
    if saknade:
        kvar += [{"roll": "CITAT", "replik": c} for c in saknade]
        print(f"  + lade till {len(saknade)} ankarcitat som ingen sa i studion")
    return kvar


def skriv_manus(sokvag: Path, slug: str, kalla_txt: str, vardar: list, klippt):
    """Formatet podd/tools/rosta-podd.js parsar: `### NN · tema` blir brytpunkt,
    `**NAMN:** replik` blir en tur, `> rad` fogas till föregående talare.
    Metadata måste ligga i rader parsern uttryckligen hoppar över — en egen
    `**Underström:**`-rad skulle bli en okänd talare och en varning."""
    rader = [f"# Beroendeframkallande · {slug}", "",
             f"**Källa:** `{kalla_txt}`",
             f"**Medverkande:** {', '.join(vardar)}", "", "---", ""]
    for seg, turer in klippt:
        rader += [f"### {seg.get('nummer')} · {seg.get('tema')}", ""]
        for t in turer:
            if t["roll"] == "CITAT":
                rader += [f"> {t['replik']}", ""]
            else:
                rader += [f"**{t['roll']}:** {t['replik']}", ""]
        rader += ["---", ""]
    sokvag.write_text("\n".join(rader), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description="Fas 3: klipparen sållar det råa bandet.")
    ap.add_argument("plan", type=Path, help="podd/<slug>.plan.json")
    ap.add_argument("--torrkor", action="store_true", help="visa bandet, anropa inte")
    ap.add_argument("--budget", type=float, default=5.0, help="tak i USD (default 5)")
    ap.add_argument("--modell", default=MODELL)
    ap.add_argument("--effort", default="high",
                    choices=["low", "medium", "high", "xhigh", "max"],
                    help="klipparen gör avsnittets enda helhetsbedömning")
    ap.add_argument("--segment", type=str, default=None, help="t.ex. 01,03")
    args = ap.parse_args()

    plan = json.loads(las(args.plan))
    slug = plan.get("slug", args.plan.stem.replace(".plan", ""))

    fil_ratape = PODD / f"{slug}.ratape.json"
    if not fil_ratape.exists():
        raise SystemExit(
            f"Hittar inget rått band ({fil_ratape.relative_to(ROT)}).\n"
            f"Kör fas 2 först:\n\n"
            f"    python3 podd/tools/simulera-podd.py {args.plan}\n")

    band = json.loads(las(fil_ratape))
    allt = [(p["seg"], p["turer"]) for p in band.get("segment", [])]
    if args.segment:
        valda = {s.strip() for s in args.segment.split(",")}
        allt = [(s, t) for s, t in allt if s.get("nummer") in valda]
    if not allt:
        raise SystemExit("Inga segment att klippa.")

    budget = Budget(args.budget)
    logg = Logg(PODD / f"{slug}.simulering.jsonl")
    turer_in = sum(len(t) for _, t in allt)
    print(f"FAS 3 · KLIPPNING   {slug}  ·  {len(allt)} segment, {turer_in} turer "
          f"·  {args.modell} (effort {args.effort})")

    klippt = [(seg, kor_klippning(seg, turer, args, budget, logg)) for seg, turer in allt]

    if args.torrkor:
        print(f"\nTorrkörning klar. Skarp körning gör {len(allt)} anrop, ett per segment.")
        return

    namn = sorted({t["roll"] for _, turer in klippt for t in turer if t["roll"] != "CITAT"})
    utfil = PODD / f"{slug}.klippt.md"
    skriv_manus(utfil, slug, band.get("källa", plan.get("källa", "")), namn, klippt)

    kvar = sum(len(t) for _, t in klippt)
    print(f"\nSkrev {utfil.relative_to(ROT)}  ({turer_in} turer inspelade → {kvar} i sändning)")
    print(budget.rad())
    print(f"\nNästa steg — lyssna igenom manuset först, sedan:\n"
          f"  node --env-file=podd/.env podd/tools/rosta-podd.js {utfil.relative_to(ROT)} --dry-run")


if __name__ == "__main__":
    main()
