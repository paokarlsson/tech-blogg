"""vardar.py — laddar en poddvärd ur podd/vardar/<mapp>/ och bygger de
systemprompter hen uppträder under.

En värd är fyra filer och ett tillstånd:

    PROFIL.md          vem hen är          — alltid med i prompten
    BAKGRUND.md        varför hen är så    — alltid med, men får aldrig berättas
    UNDERSTROMMAR.md   dagsform            — en rad lottas per avsnitt
    ROST.md            hur hen låter       — används av rosta-podd.js, inte här

Bosse och Vera läser dessutom samma text olika, och det är strukturellt snarare
än spelat: Bosse får texten med förbehållen bortstädade och läser något mer
tvärsäkert än det är. Vera får bara tesen och förbehållen och läser en text som
vägrar bestämma sig. Att de är oense om vad texten säger är alltså inbyggt.
"""

import random
import re
from dataclasses import dataclass, field
from pathlib import Path

from llm import PODD, las

VARDMAPP = PODD / "vardar"

# Ord som markerar att texten tar ett förbehåll.
HEDGAR = [
    "kanske", "jag tror", "tror jag", "verkar", "känns", "ungefär",
    "möjligen", "antagligen", "sannolikt", "jag vet inte", "inte säker",
    "snarare", "lite av", "skulle kunna", "min känsla", "är oklart",
    "i praktiken oftast", "för mig", "min erfarenhet", "inte självklart",
]

# Vilka värdar som finns, och hur de skiljer sig åt mekaniskt. Allt annat om dem
# står i deras egna filer.
UPPSATTNING = {
    "BOSSE": {"mapp": "bosse", "lasart": "utan_forbehall", "minne": 6},
    "VERA": {"mapp": "vera", "lasart": "bara_forbehall", "minne": 14},
}

# Stående regler i studion. Ligger i systemprompten, syns aldrig i manuset.
# Punkt 1 är motmedlet mot att två modeller blir sams på tur tolv.
STAENDE_STUDIO = """
STÅENDE REGLER I STUDION — de gäller före allt annat:

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
8. Du svarar med två fält: "tanke" och "replik". Tanken är vad du faktiskt
   tycker just nu — den hörs inte i mikrofonen och medprataren får aldrig veta
   den. Den får gärna motsäga repliken. Repliken är det du säger högt.
9. Din bakgrund är din, inte lyssnarens. Den ska höras som tyngd, aldrig
   berättas som historia. Du refererar aldrig till den som en anekdot du drar.
"""

# Ett annat läge: ingen medpratare, ingen publik, ingen som avbryter.
STAENDE_FORARBETE = """
STÅENDE REGLER FÖR FÖRARBETET:

1. Ingen hör det här. Du sitter ensam kvällen före och tänker igenom texten.
   Du behöver inte vara rolig, artig eller sammanhängande.
2. Du får bara påstå sakförhållanden som står i texten du fått. Allt annat
   formulerar du som fråga eller misstanke, aldrig som påstående.
3. Punkterna är saker du vill SÄGA, inte ämnen du vill "ta upp". Skriv
   "en logg-fasad är fyra klasser du själv får förvalta", inte "diskutera loggning".
4. Ingen punkt får vara en sammanfattning av texten. Sammanfattningar är inte
   poddbara. Du letar efter det du reagerar på.
5. Dina egna minnen och erfarenheter får du använda fritt här — det är det enda
   stället i hela produktionen där du får hitta på något som inte står i texten.
   De ska vara dina, konkreta och små. Inte poänger. Inte liknelser.
6. Du skriver i första person, på svenska, utan rubriker och utan punchlines.
"""


def meningar(text: str):
    """Grov meningsdelning. Räcker för svensk brödtext."""
    bitar = re.split(r"(?<=[.!?])\s+", text.strip())
    return [b.strip() for b in bitar if b.strip()]


def har_hedge(mening: str) -> bool:
    lag = mening.lower()
    return any(h in lag for h in HEDGAR)


def punkter_ur(md: str) -> list:
    """Plockar ut `- `-raderna ur en markdownfil. Används för underströmmar."""
    return [r[2:].strip() for r in md.splitlines() if r.startswith("- ")]


@dataclass
class Vard:
    namn: str                       # BOSSE / VERA — nyckeln i manus och roster.json
    mapp: Path
    profil: str
    bakgrund: str
    understrom: str
    lasart: str
    minne: int                      # hur många tidigare turer hen ser
    vy: str = ""                    # sätts per segment
    forarbete: dict = field(default_factory=dict)
    agenda_fran: str = ""           # punktlistan hen fått av den andre
    agenda_till: str = ""           # namnet på den hen skickade sin lista till

    # ---------------------------------------------------------------- texten

    def se_text(self, seg: dict) -> str:
        kalltext = seg.get("källtext", [])
        if self.lasart == "utan_forbehall":
            ut = []
            for stycke in kalltext:
                kvar = [m for m in meningar(stycke) if not har_hedge(m)]
                if kvar:
                    ut.append(" ".join(kvar))
            return "\n\n".join(ut) if ut else "(inget kvar när förbehållen tagits bort)"

        if self.lasart == "bara_forbehall":
            tes = seg.get("tes", seg.get("tema", ""))
            ut = [m for stycke in kalltext for m in meningar(stycke) if har_hedge(m)]
            huvud = f"Avsnittets tes enligt texten: {tes}"
            if not ut:
                return huvud + "\n\n(texten tar inga förbehåll alls här)"
            return (huvud + "\n\nTextens förbehåll, ordagrant:\n"
                    + "\n".join(f"– {m}" for m in ut))

        return "\n\n".join(kalltext)

    def hela_texten(self, segment: list) -> str:
        return "\n\n".join(
            f"## Segment {s.get('nummer')} · {s.get('tema')}\n{self.se_text(s)}"
            for s in segment)

    # ---------------------------------------------------------- systemprompter

    def _huvud(self) -> str:
        return (
            f"Du ÄR {self.namn}. Du spelar inte {self.namn}, du är det. Du svarar "
            f"alltid i första person, på svenska.\n\n"
            f"Du känner inte till någon karaktärsbeskrivning av din samtalspartner "
            f"och du ska inte försöka gissa dig till hur hen kommer att reagera. "
            f"Du vet bara vad hen faktiskt har sagt eller skickat till dig.\n\n"
            f"=== DIN PROFIL ===\n{self.profil}\n\n"
            f"=== DIN BAKGRUND (du bär den, du berättar den inte) ===\n{self.bakgrund}\n\n"
            f"=== DIN UNDERSTRÖM IDAG (hemlig, sägs aldrig rakt ut) ===\n{self.understrom}\n"
        )

    def systemprompt_forarbete(self) -> str:
        return self._huvud() + STAENDE_FORARBETE

    def systemprompt_studio(self, nummer: str) -> str:
        delar = [self._huvud()]
        if self.forarbete:
            delar.append("=== DITT EGET FÖRARBETE (du minns det, ingen annan ser det) ===\n"
                         + rendera_forarbete(self.forarbete, nummer))
        if self.agenda_till:
            delar.append(f"=== DU SKICKADE DIN PUNKTLISTA TILL {self.agenda_till} I GÅR KVÄLL ===\n"
                         f"Hen har läst den. Du vet inte hur noga.")
        if self.agenda_fran:
            delar.append(self.agenda_fran)
        delar.append(STAENDE_STUDIO)
        return "\n\n".join(delar)


def ladda(namn: str, rnd: random.Random, understrom: str = None) -> Vard:
    namn = namn.upper()
    spec = UPPSATTNING[namn]
    mapp = VARDMAPP / spec["mapp"]
    saknas = [f for f in ("PROFIL.md", "BAKGRUND.md", "UNDERSTROMMAR.md")
              if not (mapp / f).exists()]
    if saknas:
        raise SystemExit(f"{mapp} saknar {', '.join(saknas)}")
    val = understrom or rnd.choice(punkter_ur(las(mapp / "UNDERSTROMMAR.md")))
    return Vard(namn=namn, mapp=mapp,
                profil=las(mapp / "PROFIL.md"),
                bakgrund=las(mapp / "BAKGRUND.md"),
                understrom=val, lasart=spec["lasart"], minne=spec["minne"])


def ladda_alla(fro: int = None, understrommar: dict = None) -> dict:
    rnd = random.Random(fro)
    understrommar = understrommar or {}
    return {n: ladda(n, rnd, understrommar.get(n)) for n in UPPSATTNING}


# ------------------------------------------------------------------ förarbetet

def rendera_forarbete(fa: dict, nummer: str = None) -> str:
    """Värdens egna anteckningar. Punkterna filtreras till aktuellt segment — en
    agent som ser hela sin lista i varje segment betar av den som en lista."""
    punkter = fa.get("punkter", [])
    if nummer:
        punkter = [p for p in punkter
                   if str(p.get("segment", "")).zfill(2) == str(nummer).zfill(2)]
    rader = [f"Så här landade texten hos dig: {fa.get('helhetsintryck', '')}",
             f"Det som provocerar dig mest: {fa.get('provokationen', '')}",
             f"Där du själv står svagast (säg det aldrig högt): {fa.get('svag_punkt', '')}"]
    for h in fa.get("historier", []):
        rader.append(f"Något du kom att tänka på, och som du får berätta om det passar: "
                     f"{h.get('historia', '')}")
    if punkter:
        rader.append("Punkter du bestämde dig för att få sagt här:")
        rader += [f"– {p['punkt']}  (ditt skäl: {p.get('varfor', '')})" for p in punkter]
    else:
        rader.append("Du hade inga förberedda punkter för just det här segmentet. "
                     "Du får ta det som det kommer.")
    return "\n".join(rader)


def rendera_agenda(avsandare: str, fa: dict) -> str:
    """Punktlistan som faktiskt skickas över kvällen före. Bara punkterna —
    skälen bakom dem stannar hos avsändaren, så mottagaren vet vad som kommer
    men inte varför."""
    punkter = fa.get("punkter", [])
    if not punkter:
        return ""
    rader = [f"=== HÅLLPUNKTER DU FICK AV {avsandare} I GÅR KVÄLL ===",
             f"{avsandare} skickade den här listan inför inspelningen. Du vet vad "
             f"hen tänker ta upp, men inte varför, och du har inte lovat något "
             f"om den.", ""]
    rader += [f"{i}. ({p.get('segment', '??')}) {p['punkt']}"
              for i, p in enumerate(punkter, 1)]
    return "\n".join(rader)
