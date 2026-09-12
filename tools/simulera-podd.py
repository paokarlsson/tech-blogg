#!/usr/bin/env python3
"""
simulera-podd.py — genererar ett poddmanus genom att låta två separata
Claude-instanser samtala, under en röstlös regissör.

    python3 tools/simulera-podd.py podd/<slug>.plan.json --torrkor
    python3 tools/simulera-podd.py podd/<slug>.plan.json

Arkitektur
----------
Tre roller, tre helt skilda kontexter. Ingen av dem delar minne med någon annan.

    BOSSE-agent            VERA-agent
      egen bibel             egen bibel
      egen underström        egen underström
      egen vy av texten      egen vy av texten
      eget minnesfönster     eget minnesfönster
            \\                  /
             \\                /
              REGISSÖR (talar aldrig)
              ser allt · avvisar turer · skickar privata lappar

Sluten kontext
--------------
Varje anrop är en ny process utan historik. Ingen `--resume`, ingen
`--continue`, ingen sessionspersistens. Modellen har exakt det minne som det
här skriptet väljer att rendera in i prompten — ingenting annat. Dessutom:

    --safe-mode              ingen CLAUDE.md, inga skills, hooks, plugins, MCP
    --tools ""               inga verktyg alls, ren textgenerering
    --system-prompt          ersätter standardprompten helt
    --no-session-persistence inget skrivs till disk, inget går att återuppta
    --strict-mcp-config      ignorerar all MCP-konfiguration
    --disable-slash-commands
    --permission-prompts none

Kör alltid `--torrkor` först. Då byggs alla kontexter och skrivs ut, budgeten
redovisas, och inget anrop görs.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

ROT = Path(__file__).resolve().parent.parent

# Måste matcha TAGGAR-listan i tools/rosta-podd.js, annars faller regiordet
# tyst bort vid röstsättningen.
REGIORD = ["skrattar", "paus", "kort paus", "torrt", "surt", "tjurigt", "nöjt",
           "motvilligt", "tvekande", "skeptiskt", "nyfiket", "fundersamt",
           "road", "suckar", "viskar", "sarkastiskt", "uppgivet", "bestämt",
           "varmt", "otåligt", "rakt, utan skämt"]

# Ord som markerar att texten tar ett förbehåll. Bosse får en text där de är
# bortstädade — han läser något mer tvärsäkert än det är, och blir uppriktigt
# angripen. Vera får bara förbehållen — hon läser en text som vägrar bestämma
# sig. Att de är oense om vad texten säger är alltså strukturellt, inte spelat.
HEDGAR = [
    "kanske", "jag tror", "tror jag", "verkar", "känns", "ungefär",
    "möjligen", "antagligen", "sannolikt", "jag vet inte", "inte säker",
    "snarare", "lite av", "skulle kunna", "min känsla", "är oklart",
    "i praktiken oftast", "för mig", "min erfarenhet", "inte självklart",
]

# Underströmmar. Slås per avsnitt, oberoende av inlägget — det är det som gör
# att samma text kan ge fem olika avsnitt. Ingen av dem känner den andres.
UNDERSTROMMAR = {
    "BOSSE": [
        "Du kom oförberedd. Du har läst rubriken och sista stycket. Du döljer det genom att prata snabbt och ställa frågor.",
        "Du vill återuppta något ni bråkade om förra veckan och letar efter en öppning hela avsnittet.",
        "Du gjorde faktiskt det du lovade förra gången. Det gick dåligt. Du berättar det inte förrän du blir tvungen.",
        "Du är ovanligt angelägen om att bli omtyckt idag. Du vet inte varför.",
        "Du är trött. Du orkar inte försvara något i mer än två repliker.",
    ],
    "VERA": [
        "Du bestämde dig innan du läst klart. Du märker det halvvägs in och backar utan att kommentera det.",
        "Du är på oväntat gott humör. Du tänker inte förklara varför.",
        "Du har en poäng du vill fram till och du styr dit tålmodigt, även när samtalet vill åt annat håll.",
        "Du håller faktiskt med om huvudtesen men vägrar säga det rakt ut förrän mycket sent.",
        "Du är irriterad på något som inte har med det här att göra och det färgar din exakthet.",
    ],
}

# Stående regler per roll. Ligger i systemprompten, syns aldrig i manuset.
# Punkt 1 hos båda är motmedlet mot att två modeller blir sams på tur tolv.
STAENDE = """
STÅENDE REGLER — de gäller före allt annat:

1. Du får ge med dig HÖGST EN GÅNG per segment, i högst en mening. Resten av
   segmentet håller du din linje. Att söka samförstånd är fel beteende här.
2. Du säger aldrig "det beror på". Aldrig.
3. Du skriver EN replik. Inte en scen, inte flera turer, ingen regianvisning
   utöver de tillåtna nedan. Ingen inledande namnetikett.
4. Du får bara påstå sakförhållanden som står i den text du fått. Hittar du på
   ett faktum kastas repliken. Är du osäker: fråga i stället för att påstå.
5. Ingen punchline. Ingen sammanfattning. Du talar som någon mitt i ett samtal,
   inte som någon som håller föredrag.
6. Tillåtna regianvisningar, sparsamt: *(skrattar)* *(paus)* *(kort paus)*
   *(torrt)* *(surt)* *(nöjt)* *(motvilligt)* *(tvekande)* *(skeptiskt)*
7. Du kan avbryta med tankstreck i slutet om du klipper av den andre.
"""


def las(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def meningar(text: str):
    """Grov meningsdelning. Räcker för svensk brödtext."""
    bitar = re.split(r"(?<=[.!?])\s+", text.strip())
    return [b.strip() for b in bitar if b.strip()]


def har_hedge(mening: str) -> bool:
    lag = mening.lower()
    return any(h in lag for h in HEDGAR)


def vy_bosse(kalltext) -> str:
    """Texten med förbehållen bortstädade. Låter mer tvärsäker än den är."""
    ut = []
    for stycke in kalltext:
        kvar = [m for m in meningar(stycke) if not har_hedge(m)]
        if kvar:
            ut.append(" ".join(kvar))
    return "\n\n".join(ut) if ut else "(inget kvar när förbehållen tagits bort)"


def vy_vera(kalltext, tes: str) -> str:
    """Bara tesen och förbehållen. Låter som en text som vägrar bestämma sig."""
    ut = [m for stycke in kalltext for m in meningar(stycke) if har_hedge(m)]
    huvud = f"Avsnittets tes enligt texten: {tes}"
    if not ut:
        return huvud + "\n\n(texten tar inga förbehåll alls här)"
    return huvud + "\n\nTextens förbehåll, ordagrant:\n" + "\n".join(f"– {m}" for m in ut)


@dataclass
class Roll:
    namn: str
    bibel: str
    understrom: str
    minne: int            # hur många tidigare turer rollen ser
    vy: str = ""          # sätts per segment

    def systemprompt(self) -> str:
        return (
            f"Du ÄR {self.namn}. Du spelar inte {self.namn}, du är det. Du svarar "
            f"alltid i första person, på svenska, i en inspelad poddstudio.\n\n"
            f"Du känner inte till någon karaktärsbeskrivning av din samtalspartner "
            f"och du ska inte försöka gissa dig till hur hen kommer att reagera. "
            f"Du vet bara vad hen faktiskt har sagt högt.\n\n"
            f"=== DIN KARAKTÄR ===\n{self.bibel}\n\n"
            f"=== DIN UNDERSTRÖM IDAG (hemlig, sägs aldrig rakt ut) ===\n{self.understrom}\n"
            f"{STAENDE}"
        )


@dataclass
class Budget:
    tak: float
    spenderat: float = 0.0
    anrop: int = 0

    def lagg(self, usd: float):
        self.spenderat += usd
        self.anrop += 1
        if self.spenderat > self.tak:
            raise SystemExit(
                f"\nBUDGETTAK NÅTT: {self.spenderat:.2f} USD > {self.tak:.2f} USD "
                f"efter {self.anrop} anrop. Avbryter."
            )


@dataclass
class Logg:
    sokvag: Path
    rader: list = field(default_factory=list)

    def skriv(self, post: dict):
        self.rader.append(post)
        with self.sokvag.open("a", encoding="utf-8") as f:
            f.write(json.dumps(post, ensure_ascii=False) + "\n")


def seglflaggor() -> list:
    """Flaggorna som försluter kontexten."""
    bas = [
        "--tools", "",
        "--output-format", "json",
        "--no-session-persistence",
        "--strict-mcp-config",
        "--disable-slash-commands",
        "--permission-prompts", "none",
    ]
    # --bare sluter hårdast men läser bara ANTHROPIC_API_KEY, aldrig OAuth.
    # Utan nyckel är --safe-mode motsvarigheten som fungerar med inloggning.
    return (["--bare"] if os.environ.get("ANTHROPIC_API_KEY") else ["--safe-mode"]) + bas


def kalla(system: str, user: str, model: str, budget: Budget,
          schema: dict = None, forsok: int = 3) -> str:
    """Ett anrop, en ny process, ingen historik. Returnerar svarstexten."""
    cmd = ["claude", "-p", user, "--system-prompt", system, "--model", model]
    cmd += seglflaggor()
    if schema:
        cmd += ["--json-schema", json.dumps(schema)]

    for n in range(forsok):
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if r.returncode == 0:
            try:
                d = json.loads(r.stdout)
            except json.JSONDecodeError:
                time.sleep(2 * (n + 1))
                continue
            if not d.get("is_error"):
                budget.lagg(d.get("total_cost_usd", 0.0))
                return d.get("result", "").strip()
        time.sleep(2 * (n + 1))
    raise SystemExit(f"Anropet misslyckades {forsok} gånger.\n{r.stderr[:500]}")


# ---------------------------------------------------------------- regissören

REGI_SCHEMA = {
    "type": "object",
    "properties": {
        "beslut": {"type": "string", "enum": ["behall", "gor_om", "avsluta"]},
        "skal": {"type": "string", "maxLength": 200},
        "lapp": {"type": "string", "maxLength": 200},
    },
    "required": ["beslut", "skal", "lapp"],
    "additionalProperties": False,
}

REGI_SYSTEM = """Du är regissör för en poddinspelning. Du talar aldrig i mikrofonen.
Du ser allt: båda karaktärerna, källtexten, hela transkriptet.

Ditt jobb är att hålla samtalet levande. Du bedömer den sist sagda repliken och
svarar med JSON.

KASTA repliken (gor_om) om något av detta gäller:
– den är längre än ungefär 55 ord, alltså en föreläsning
– den innehåller ett sakpåstående som inte finns i källtexten
– den håller med föregående replik utan att tillföra något
– den skulle kunna ha sagts av den andra karaktären utan att kännas fel
– den sammanfattar i stället för att driva
– den är artig på ett sätt som ingen av dem är
– den bär samma regianvisning som talarens förra replik. Regi ska vara sällsynt;
  tre *(surt)* i rad är ingen karaktär, det är en tic. Högst var tredje replik.

AVSLUTA segmentet (avsluta) när tesen har brutits isär och minst en av dem har
ändrat sig eller grävt ner sig hörbart. Hellre för tidigt än för sent.

Annars: behall.

Fältet "lapp" är en hemlig instruktion som viskas till NÄSTA talare innan hen
svarar. Använd den aktivt för att skapa friktion — inte för att styra innehåll,
utan tillstånd: "du blir otålig nu", "du har just insett att du har fel men säg
det inte än", "svara med ett enda ord", "avbryt hen mitt i meningen", "du tappar
tråden och kommer inte tillbaka till den".

Viktigast av allt: BÖRJAR DE BLI SAMS — putta isär dem. Två personer som
konvergerar är ett dött avsnitt. Skriv lappen därefter."""


def konvergens(transkript) -> float:
    """Billigt lokalt mått: ordöverlapp mellan de två sista replikerna."""
    if len(transkript) < 2:
        return 0.0
    a = set(re.findall(r"\w+", transkript[-1]["replik"].lower()))
    b = set(re.findall(r"\w+", transkript[-2]["replik"].lower()))
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


def rendera_transkript(transkript, fonster: int) -> str:
    if not transkript:
        return "(inget sagt än — du öppnar segmentet)"
    valda = transkript[-fonster:] if fonster > 0 else transkript
    return "\n".join(f"{t['roll']}: {t['replik']}" for t in valda)


def kor_segment(seg, bosse: Roll, vera: Roll, model_roll: str, model_regi: str,
                budget: Budget, logg: Logg, maxturer: int, torrkor: bool):
    nummer, tema = seg.get("nummer", "??"), seg.get("tema", "")
    kalltext = seg.get("källtext", [])
    ankare = seg.get("ankare", [])
    bosse.vy = vy_bosse(kalltext)
    vera.vy = vy_vera(kalltext, seg.get("tes", tema))

    print(f"\n─── SEGMENT {nummer} · {tema} " + "─" * 30)

    if torrkor:
        print(f"\n[BOSSES VY AV TEXTEN]\n{bosse.vy}\n")
        print(f"[VERAS VY AV TEXTEN]\n{vera.vy}\n")
        print(f"[ANKARE] {ankare or '(inget)'}")
        print(f"[BOSSES SYSTEMPROMPT] {len(bosse.systemprompt())} tecken")
        print(f"[VERAS SYSTEMPROMPT]  {len(vera.systemprompt())} tecken")
        return []

    transkript, lapp = [], ""
    turordning = [vera, bosse] if int(nummer or 0) % 2 == 0 else [bosse, vera]

    for i in range(maxturer):
        roll = turordning[i % 2]
        andre = turordning[(i + 1) % 2]

        user = (
            f"=== TEXTEN DU HAR LÄST (segment {nummer}: {tema}) ===\n{roll.vy}\n\n"
            f"=== SAMTALET HITTILLS ===\n{rendera_transkript(transkript, roll.minne)}\n\n"
            f"=== DIN MEDPRATARE HETER {andre.namn} ===\n\n"
            + (f"=== VISKAT TILL DIG PRECIS NU ===\n{lapp}\n\n" if lapp else "")
            + "Säg din nästa replik. Bara repliken."
        )
        replik = kalla(roll.systemprompt(), user, model_roll, budget)
        replik = re.sub(rf"^\*?\*?{roll.namn}:?\*?\*?\s*", "", replik).strip()
        # Modellen skriver (surt); rosta-podd.js läser *(surt)*. Normalisera.
        replik = re.sub(r"(?<!\*)\((" + "|".join(REGIORD) + r")\)(?!\*)",
                        r"*(\1)*", replik)

        transkript.append({"roll": roll.namn, "replik": replik})
        konv = konvergens(transkript)

        regi_user = (
            f"KÄLLTEXT (allt som får påstås):\n" + "\n".join(kalltext) + "\n\n"
            f"ANKARCITAT som ska sägas ordagrant innan segmentet slutar:\n"
            f"{ankare or '(inget i det här segmentet)'}\n\n"
            f"TRANSKRIPT:\n{rendera_transkript(transkript, 0)}\n\n"
            f"Tur {i+1} av högst {maxturer}. Ordöverlapp mot föregående replik: "
            f"{konv:.2f} (över 0.35 = de börjar bli sams).\n\n"
            f"Bedöm den sista repliken, sagd av {roll.namn}."
        )
        regi = json.loads(kalla(REGI_SYSTEM, regi_user, model_regi, budget, REGI_SCHEMA))

        logg.skriv({"segment": nummer, "tur": i + 1, "roll": roll.namn,
                    "replik": replik, "konvergens": round(konv, 3),
                    "regi": regi, "usd": round(budget.spenderat, 4)})

        if regi["beslut"] == "gor_om":
            print(f"  ✗ {roll.namn}: {replik[:60]}…  ({regi['skal'][:60]})")
            transkript.pop()
            lapp = regi["lapp"]
            continue

        print(f"  {roll.namn}: {replik[:78]}")
        lapp = regi["lapp"]

        if regi["beslut"] == "avsluta":
            print(f"  ── segmentet slut: {regi['skal'][:70]}")
            break

    return transkript


def main():
    ap = argparse.ArgumentParser(description="Simulera ett poddavsnitt med två skilda agenter.")
    ap.add_argument("plan", type=Path, help="podd/<slug>.plan.json")
    ap.add_argument("--torrkor", action="store_true", help="bygg kontexter, anropa inte")
    ap.add_argument("--budget", type=float, default=8.0, help="tak i USD (default 8)")
    ap.add_argument("--model-roll", default="sonnet")
    ap.add_argument("--model-regi", default="sonnet")
    ap.add_argument("--maxturer", type=int, default=18, help="turer per segment")
    ap.add_argument("--minne-bosse", type=int, default=6,
                    help="turer bakåt Bosse ser (kort = han glömmer och upprepar sig)")
    ap.add_argument("--minne-vera", type=int, default=14,
                    help="turer bakåt Vera ser (långt = hon är exakt)")
    ap.add_argument("--fro", type=int, default=None, help="fast val av underströmmar")
    ap.add_argument("--segment", type=str, default=None, help="t.ex. 01,03")
    args = ap.parse_args()

    plan = json.loads(las(args.plan))
    slug = plan.get("slug", args.plan.stem.replace(".plan", ""))
    segment = plan.get("segment", [])
    if args.segment:
        valda = {s.strip() for s in args.segment.split(",")}
        segment = [s for s in segment if s.get("nummer") in valda]

    bibel = las(ROT / "podd" / "PERSONLIGHETER.md")

    def klipp(rubrik, nasta):
        i, j = bibel.find(rubrik), bibel.find(nasta)
        return bibel[i:j].strip() if i >= 0 and j > i else bibel

    import random
    rnd = random.Random(args.fro)
    bosse = Roll("BOSSE", klipp("## 2. 🧯", "## 3. 🔪"),
                 rnd.choice(UNDERSTROMMAR["BOSSE"]), args.minne_bosse)
    vera = Roll("VERA", klipp("## 3. 🔪", "## 4. Kemin"),
                rnd.choice(UNDERSTROMMAR["VERA"]), args.minne_vera)

    print(f"Avsnitt: {slug}  ·  {len(segment)} segment  ·  modell {args.model_roll}")
    print(f"Sluten kontext: claude {' '.join(seglflaggor()[:3])} … (ingen resume, ingen persistens)")
    print(f"BOSSES underström: {bosse.understrom}")
    print(f"VERAS underström:  {vera.understrom}")

    budget = Budget(args.budget)
    utfil = ROT / "podd" / f"{slug}.simulerat.md"
    loggfil = ROT / "podd" / f"{slug}.simulering.jsonl"
    if not args.torrkor and loggfil.exists():
        loggfil.unlink()
    logg = Logg(loggfil)

    allt = []
    for seg in segment:
        allt.append((seg, kor_segment(seg, bosse, vera, args.model_roll,
                                      args.model_regi, budget, logg,
                                      args.maxturer, args.torrkor)))

    if args.torrkor:
        turer = len(segment) * args.maxturer
        print(f"\nTorrkörning klar. {len(segment)} segment × högst {args.maxturer} turer "
              f"= högst {turer} repliker, vardera ett roll- plus ett regissörsanrop "
              f"≈ {turer * 2} anrop. Grovt ~0,01–0,03 USD styck.")
        return

    rader = [f"# Beroendeframkallande · {slug}", "",
             f"> Simulerat manus. Två skilda agenter, röstlös regissör.",
             f"> Bosses underström: {bosse.understrom}",
             f"> Veras underström: {vera.understrom}", "",
             f"**Källa:** `{plan.get('källa', '')}`", "", "---", ""]
    for seg, turer in allt:
        rader += [f"### {seg.get('nummer')} · {seg.get('tema')}", ""]
        for t in turer:
            rader += [f"**{t['roll']}:** {t['replik']}", ""]
        rader += ["---", ""]
    rader += ["", f"*{budget.anrop} anrop, {budget.spenderat:.2f} USD.*"]
    utfil.write_text("\n".join(rader), encoding="utf-8")

    print(f"\nSkrev {utfil.relative_to(ROT)}  ({budget.anrop} anrop, {budget.spenderat:.2f} USD)")
    print(f"Logg:  {loggfil.relative_to(ROT)}")


if __name__ == "__main__":
    main()
