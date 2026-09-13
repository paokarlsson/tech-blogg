#!/usr/bin/env python3
"""forarbete.py — fas 1 av tre. Kvällen före inspelningen.

    python3 podd/tools/forarbete.py podd/<slug>.plan.json --torrkor
    python3 podd/tools/forarbete.py podd/<slug>.plan.json

Varje värd sitter ensam med sin egen vy av inlägget och tänker igenom det: vad
hen tycker, vad som provocerar, vad hen associerar till, vilka historier ur det
egna yrkeslivet som texten drar igång, och vilka punkter hen tänker få sagda.

De två anropen är helt skilda. Ingen av dem ser den andres anteckningar, och
ingen av dem vet ens att den andra sitter och gör samma sak.

Det enda som korsar gränsen är **hållpunkterna**: den ena skickar sin punktlista
till den andra (`--agenda`, default vera → bosse). Bara punkterna skickas.
Skälen bakom dem stannar hos avsändaren, så mottagaren vet vad som kommer men
inte varför.

Historierna är det enda stället i hela produktionen där en agent får hitta på
något som inte står i källtexten. Allt annat är spårbart, och klipparen i fas 3
kastar det som inte är det.

Ut:
    podd/<slug>.forarbete.json          maskinläsbart, in i fas 2
    podd/vardar/<vard>/forarbete/<slug>.md   läsbart, rätta gärna för hand
"""

import argparse
import json
from pathlib import Path

from llm import Budget, Logg, MODELL, PODD, ROT, kalla_json, las
from vardar import ladda_alla

FORARBETE_SCHEMA = {
    "type": "object",
    "properties": {
        "helhetsintryck": {"type": "string", "maxLength": 800},
        "provokationen": {"type": "string", "maxLength": 350},
        "associationer": {
            "type": "array",
            "items": {"type": "string", "maxLength": 200},
        },
        "historier": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "utlosare": {"type": "string", "maxLength": 160},
                    "historia": {"type": "string", "maxLength": 600},
                    "poang": {"type": "string", "maxLength": 200},
                },
                "required": ["utlosare", "historia", "poang"],
                "additionalProperties": False,
            },
        },
        "svag_punkt": {"type": "string", "maxLength": 350},
        "punkter": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "segment": {"type": "string"},
                    "punkt": {"type": "string", "maxLength": 200},
                    "varfor": {"type": "string", "maxLength": 250},
                },
                "required": ["segment", "punkt", "varfor"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["helhetsintryck", "provokationen", "associationer", "historier",
                 "svag_punkt", "punkter"],
    "additionalProperties": False,
}

UPPDRAG = """Du sitter ensam kvällen före inspelningen med texten framför dig.
Ingen lyssnar. Du ska inte skriva ett manus — du ska tänka igenom vad du tycker,
och lämna dig själv material att gå in i studion med.

Läs texten en gång till, långsamt, och svara med JSON:

helhetsintryck — vad texten egentligen gör på dig. Var ärlig, även om svaret är
  att den är trist, eller att du blir provocerad av något litet och petigt.

provokationen — den enskilda meningen eller idén i texten som irriterar dig mest.
  Citera den och säg varför den sätter sig.

associationer — 3 till 5 saker texten får dig att tänka på. Fritt. De behöver
  inte höra ihop med varandra och de behöver inte vara kloka. Korta.

historier — 2 eller 3 minnen ur ditt eget yrkesliv som texten drar upp.
  "utlosare" är vad i texten som satte igång det. "historia" är vad som hände,
  konkret och litet: en kväll, ett möte, ett system, en person. "poang" är vad du
  skulle använda den till i ett gräl.
  Det här är enda gången du får hitta på något som inte står i texten. Så gör det
  ordentligt — men håll dig till sådant som stämmer med den du är, och gör dem
  små. En historia med sensmoral är en dålig historia.

svag_punkt — stället där DU står svagast. Vad skulle en påläst motståndare sätta
  fingret på? Du tänker inte säga det högt, men du vill veta om det innan du går
  in i studion.

punkter — 4 till 8 saker du vill få sagt, var och en knuten till ett
  segmentnummer ur listan ovan. "punkt" är repliken du siktar mot, kort och rak.
  "varfor" är ditt privata skäl och lämnar aldrig det här dokumentet.
"""


def skriv_markdown(vard, slug: str, fa: dict, plan: dict) -> Path:
    mapp = vard.mapp / "forarbete"
    mapp.mkdir(parents=True, exist_ok=True)
    fil = mapp / f"{slug}.md"
    rader = [f"# Förarbete · {slug}", "",
             f"> {vard.namn}s egna anteckningar kvällen före inspelningen.",
             f"> Ingen annan ser det här. Rätta gärna för hand — fas 2 läser",
             f"> `podd/{slug}.forarbete.json`, så ändra där om ändringen ska gälla.", "",
             f"**Källa:** `{plan.get('källa', '')}`  ",
             f"**Underström:** {vard.understrom}", "",
             "---", "",
             "## Helhetsintryck", "", fa.get("helhetsintryck", ""), "",
             "## Det som provocerar mest", "", fa.get("provokationen", ""), "",
             "## Associationer", ""]
    rader += [f"- {a}" for a in fa.get("associationer", [])]
    rader += ["", "## Historier", ""]
    for h in fa.get("historier", []):
        rader += [f"### {h.get('utlosare', '')}", "", h.get("historia", ""), "",
                  f"*Skulle använda den till:* {h.get('poang', '')}", ""]
    rader += ["## Där jag står svagast", "", fa.get("svag_punkt", ""), "",
              "## Hållpunkter", "",
              "| Segment | Punkt | Varför (privat) |", "| --- | --- | --- |"]
    rader += [f"| {p.get('segment', '')} | {p.get('punkt', '')} | {p.get('varfor', '')} |"
              for p in fa.get("punkter", [])]
    fil.write_text("\n".join(rader) + "\n", encoding="utf-8")
    return fil


def main():
    ap = argparse.ArgumentParser(description="Fas 1: värdarna förbereder sig var för sig.")
    ap.add_argument("plan", type=Path, help="podd/<slug>.plan.json")
    ap.add_argument("--torrkor", action="store_true", help="bygg prompter, anropa inte")
    ap.add_argument("--budget", type=float, default=3.0, help="tak i USD (default 3)")
    ap.add_argument("--modell", default=MODELL)
    ap.add_argument("--effort", default="high",
                    choices=["low", "medium", "high", "xhigh", "max"],
                    help="förarbetet är avsnittets råmaterial — snåla inte här")
    ap.add_argument("--agenda", choices=["vera", "bosse", "ingen"], default="vera",
                    help="vem som skickar sin punktlista till den andre")
    ap.add_argument("--fro", type=int, default=None, help="fast val av underströmmar")
    ap.add_argument("--segment", type=str, default=None, help="t.ex. 01,03")
    args = ap.parse_args()

    plan = json.loads(las(args.plan))
    slug = plan.get("slug", args.plan.stem.replace(".plan", ""))
    segment = plan.get("segment", [])
    if args.segment:
        valda = {s.strip() for s in args.segment.split(",")}
        segment = [s for s in segment if s.get("nummer") in valda]
    if not segment:
        raise SystemExit("Inga segment att arbeta med.")

    vardar = ladda_alla(args.fro)
    budget = Budget(args.budget)
    logg = Logg(PODD / f"{slug}.simulering.jsonl")

    print(f"FAS 1 · FÖRARBETE   {slug}  ·  {len(segment)} segment  ·  {args.modell} "
          f"(effort {args.effort})")
    for v in vardar.values():
        print(f"  {v.namn}s underström: {v.understrom}")

    resultat = {}
    for namn, vard in vardar.items():
        user = (f"=== TEXTEN DU HAR LÄST ===\n{vard.hela_texten(segment)}\n\n"
                f"=== DITT UPPDRAG ===\n{UPPDRAG}")
        if args.torrkor:
            print(f"\n[{namn}] systemprompt {len(vard.systemprompt_forarbete())} tecken, "
                  f"user {len(user)} tecken")
            print(f"[{namn} SER AV TEXTEN, första 500 tecknen]\n"
                  f"{vard.hela_texten(segment)[:500]}…")
            continue

        print(f"\n── {namn} sätter sig med texten ──")
        fa = kalla_json(vard.systemprompt_forarbete(), user, budget,
                        FORARBETE_SCHEMA, modell=args.modell, effort=args.effort,
                        max_tokens=16000)
        resultat[namn] = fa
        vard.forarbete = fa
        logg.skriv({"fas": "forarbete", "vard": namn, "understrom": vard.understrom,
                    "forarbete": fa, "usd": round(budget.spenderat, 4)})

        print(f"  intryck:    {fa.get('helhetsintryck', '')[:100]}…")
        print(f"  provoceras: {fa.get('provokationen', '')[:100]}…")
        for h in fa.get("historier", []):
            print(f"  ▸ historia: {h.get('historia', '')[:90]}…")
        for p in fa.get("punkter", []):
            print(f"  · ({p.get('segment')}) {p.get('punkt', '')[:90]}")
        fil = skriv_markdown(vard, slug, fa, plan)
        print(f"  → {fil.relative_to(ROT)}")

    if args.torrkor:
        print(f"\nTorrkörning klar. Skarp körning gör 2 anrop, ett per värd.")
        return

    avsandare = args.agenda.upper() if args.agenda != "ingen" else None
    if avsandare and resultat.get(avsandare):
        mottagare = next(n for n in vardar if n != avsandare)
        print(f"\n{avsandare} skickade sina hållpunkter till {mottagare} kvällen före.")
    else:
        mottagare = None

    utfil = PODD / f"{slug}.forarbete.json"
    utfil.write_text(json.dumps({
        "slug": slug,
        "källa": plan.get("källa", ""),
        "understrommar": {n: v.understrom for n, v in vardar.items()},
        "agenda": {"fran": avsandare, "till": mottagare},
        "forarbete": resultat,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nSkrev {utfil.relative_to(ROT)}")
    print(budget.rad())
    print(f"\nNästa steg:\n  python3 podd/tools/simulera-podd.py {args.plan}")


if __name__ == "__main__":
    main()
