#!/usr/bin/env python3
"""simulera-podd.py — fas 2 av tre. Själva inspelningen.

    python3 podd/tools/simulera-podd.py podd/<slug>.plan.json --torrkor
    python3 podd/tools/simulera-podd.py podd/<slug>.plan.json

Tre roller, tre helt skilda kontexter. Ingen av dem delar minne med någon annan.

    BOSSE-agent              VERA-agent
      egen profil              egen profil
      egen bakgrund            egen bakgrund
      egen underström          egen underström
      eget förarbete           eget förarbete
      egen vy av texten        egen vy av texten
      eget minnesfönster       eget minnesfönster
            \\                    /
             \\                  /
               MODERATOR (talar aldrig)
               ser allt · kastar turer · viskar lappar

Varje tur är en **tanke** och en **replik**. Tanken hörs aldrig av medprataren,
ligger kvar i talarens eget minnesfönster, och syns för moderatorn — och det är
så moderatorn upptäcker någon som säger sig övertygad utan att vara det.

Moderatorn håller tre saker i schack samtidigt:

    LOOPEN         går de i cirkel? (ordöverlapp mot talarens egna repliker)
    FÖR LÄTT       börjar de bli sams? (ordöverlapp mot föregående replik)
                   högst en eftergift per person och segment, spärrat i kod
    FÖR SVÅRT      har ingen rört sig på länge? då är det inte ett samtal

Ut:
    podd/<slug>.ratape.md      läsbart rått band, med tankarna i HTML-kommentarer
    podd/<slug>.ratape.json    in i fas 3
    podd/<slug>.simulering.jsonl   varje tur, varje moderatorbeslut, varje krona
"""

import argparse
import json
import re
from pathlib import Path

from llm import Budget, Logg, MODELL, PODD, ROT, kalla_json, las
from vardar import ladda_alla, rendera_agenda

# Måste matcha TAGGAR-listan i podd/tools/rosta-podd.js, annars faller regiordet
# tyst bort vid röstsättningen.
REGIORD = ["skrattar", "paus", "kort paus", "torrt", "surt", "tjurigt", "nöjt",
           "motvilligt", "tvekande", "skeptiskt", "nyfiket", "fundersamt",
           "road", "suckar", "viskar", "sarkastiskt", "uppgivet", "bestämt",
           "varmt", "otåligt", "rakt, utan skämt"]

TUR_SCHEMA = {
    "type": "object",
    "properties": {
        "tanke": {"type": "string", "maxLength": 260},
        "replik": {"type": "string", "maxLength": 700},
    },
    "required": ["tanke", "replik"],
    "additionalProperties": False,
}

MOD_SCHEMA = {
    "type": "object",
    "properties": {
        "beslut": {"type": "string", "enum": ["behall", "gor_om", "avsluta"]},
        "skal": {"type": "string", "maxLength": 200},
        "lapp": {"type": "string", "maxLength": 200},
        "eftergift": {"type": "boolean"},
    },
    "required": ["beslut", "skal", "lapp", "eftergift"],
    "additionalProperties": False,
}

MOD_SYSTEM = """Du är moderator för en poddinspelning. Du talar aldrig i mikrofonen.
Du ser allt: källtexten, hela transkriptet — och det talaren TÄNKTE innan hen sa
sin replik. Tanken hörs aldrig av medprataren.

Ditt jobb är att hålla samtalet levande. Du bedömer den sist sagda repliken och
svarar med JSON.

KASTA repliken (gor_om) om något av detta gäller:
– den är längre än ungefär 55 ord, alltså en föreläsning
– den innehåller ett sakpåstående som inte finns i källtexten. Undantag: talarens
  egna minnen och erfarenheter, som hen får berätta fritt.
– den håller med föregående replik utan att tillföra något
– den skulle kunna ha sagts av den andra karaktären utan att kännas fel
– den sammanfattar i stället för att driva
– den är artig på ett sätt som ingen av dem är
– den upprepar något talaren redan sagt i det här segmentet, om än med andra ord.
  Två personer som går i cirkel är ett dött avsnitt.
– den ger upp en position som talarens egen tanke visar att hen inte har gett upp.
  Att kapitulera artigt är den vanligaste lögnen i det här formatet.
– den berättar talarens bakgrund som en anekdot i stället för att bära den
– den bär samma regianvisning som talarens förra replik. Regi ska vara sällsynt;
  tre *(surt)* i rad är ingen karaktär, det är en tic. Högst var tredje replik.

AVSLUTA segmentet (avsluta) när tesen har brutits isär och minst en av dem har
ändrat sig eller grävt ner sig hörbart. Hellre för tidigt än för sent.

Annars: behall.

Sätt "eftergift" till true om repliken faktiskt lämnar mark till den andre —
medger en poäng, backar från ett påstående, byter fot. Var strikt: att låta
vänlig är ingen eftergift, att säga "okej, där har du rätt" är det.

Fältet "lapp" är en hemlig instruktion som viskas till NÄSTA talare innan hen
svarar. Använd den aktivt för att skapa friktion — inte för att styra innehåll,
utan tillstånd: "du blir otålig nu", "du har just insett att du har fel men säg
det inte än", "svara med ett enda ord", "avbryt hen mitt i meningen", "du tappar
tråden och kommer inte tillbaka till den".

Du håller tre saker i schack samtidigt:
– LOOPEN. Går de i cirkel, bryt med en lapp som tvingar in något nytt.
– DET FÖR LÄTTA. Börjar de bli sams, putta isär dem.
– DET FÖR SVÅRA. Har ingen rört sig på länge är det inte heller ett samtal.
  Skriv då en lapp som tvingar fram rörelse hos den som står svagast."""


def konvergens(transkript) -> float:
    """Billigt lokalt mått: ordöverlapp mellan de två sista replikerna."""
    if len(transkript) < 2:
        return 0.0
    a = set(re.findall(r"\w+", transkript[-1]["replik"].lower()))
    b = set(re.findall(r"\w+", transkript[-2]["replik"].lower()))
    if not a or not b:
        return 0.0
    return len(a & b) / min(len(a), len(b))


def upprepning(transkript, vardnamn: str) -> float:
    """Störst ordöverlapp mellan senaste repliken och talarens EGNA tidigare
    repliker. Fångar den som maler samma sak i nya ord — loopen, alltså."""
    egna = [t["replik"] for t in transkript[:-1] if t["roll"] == vardnamn]
    a = set(re.findall(r"\w+", transkript[-1]["replik"].lower()))
    if not egna or not a:
        return 0.0
    varden = []
    for tidigare in egna:
        b = set(re.findall(r"\w+", tidigare.lower()))
        if b:
            varden.append(len(a & b) / min(len(a), len(b)))
    return max(varden) if varden else 0.0


def rendera_transkript(transkript, fonster: int, for_vard: str = None) -> str:
    """Renderar samtalet. for_vard får dessutom se sina egna tankar — ingen
    annans. Det är hela poängen med att tanken är ett eget fält."""
    if not transkript:
        return "(inget sagt än — du öppnar segmentet)"
    valda = transkript[-fonster:] if fonster > 0 else transkript
    rader = []
    for t in valda:
        if for_vard and t["roll"] == for_vard and t.get("tanke"):
            rader.append(f"(du tänkte: {t['tanke']})")
        rader.append(f"{t['roll']}: {t['replik']}")
    return "\n".join(rader)


def stada_replik(text: str, namn: str) -> str:
    text = re.sub(rf"^\*?\*?{namn}:?\*?\*?\s*", "", text or "").strip()
    # Modellen skriver (surt); rosta-podd.js läser *(surt)*. Normalisera.
    return re.sub(r"(?<!\*)\((" + "|".join(REGIORD) + r")\)(?!\*)", r"*(\1)*", text)


def kor_segment(seg, turordning, args, budget: Budget, logg: Logg):
    nummer, tema = seg.get("nummer", "??"), seg.get("tema", "")
    kalltext = seg.get("källtext", [])
    ankare = seg.get("ankare", [])
    for v in turordning:
        v.vy = v.se_text(seg)

    print(f"\n─── SEGMENT {nummer} · {tema} " + "─" * 30)

    if args.torrkor:
        for v in turordning:
            print(f"\n[{v.namn} SER AV TEXTEN]\n{v.vy}")
            print(f"[{v.namn}s SYSTEMPROMPT] {len(v.systemprompt_studio(nummer))} tecken")
        print(f"\n[ANKARE] {ankare or '(inget)'}")
        return []

    # Jämna segment öppnas av den andra värden, så ingen äger öppningen.
    if int(nummer or 0) % 2 == 0:
        turordning = list(reversed(turordning))

    transkript, lapp = [], ""
    eftergifter = {v.namn: 0 for v in turordning}
    sedan_rorelse = 0

    for i in range(args.maxturer):
        vard = turordning[i % 2]
        andre = turordning[(i + 1) % 2]

        user = (
            f"=== TEXTEN DU HAR LÄST (segment {nummer}: {tema}) ===\n{vard.vy}\n\n"
            f"=== SAMTALET HITTILLS ===\n"
            f"{rendera_transkript(transkript, vard.minne, for_vard=vard.namn)}\n\n"
            f"=== DIN MEDPRATARE HETER {andre.namn} ===\n\n"
            + (f"=== VISKAT TILL DIG PRECIS NU AV MODERATORN ===\n{lapp}\n\n" if lapp else "")
            + "Tänk först, säg sedan. Svara med fälten \"tanke\" och \"replik\"."
        )
        tur = kalla_json(vard.systemprompt_studio(nummer), user, budget, TUR_SCHEMA,
                         modell=args.modell, effort=args.effort_vard, max_tokens=8000)
        replik = stada_replik(tur.get("replik", ""), vard.namn)
        if not replik:
            continue

        transkript.append({"roll": vard.namn, "replik": replik,
                           "tanke": tur.get("tanke", "")})
        konv = konvergens(transkript)
        upp = upprepning(transkript, vard.namn)

        mod_user = (
            "KÄLLTEXT (allt som får påstås, utöver talarnas egna minnen):\n"
            + "\n".join(kalltext) + "\n\n"
            f"ANKARCITAT som ska sägas ordagrant innan segmentet slutar:\n"
            f"{ankare or '(inget i det här segmentet)'}\n\n"
            f"TRANSKRIPT:\n{rendera_transkript(transkript, 0)}\n\n"
            f"{vard.namn} TÄNKTE innan repliken: {tur.get('tanke', '(inget)')}\n\n"
            f"Tur {i+1} av högst {args.maxturer}.\n"
            f"Ordöverlapp mot föregående replik: {konv:.2f} (över 0.35 = de börjar bli sams).\n"
            f"Ordöverlapp mot {vard.namn}s egna tidigare repliker: {upp:.2f} "
            f"(över 0.45 = hen maler samma sak igen).\n"
            f"Eftergifter hittills i segmentet: {eftergifter}. Var och en får göra EN.\n"
            f"Turer sedan någon rörde sig: {sedan_rorelse} "
            f"(över 6 = det står still, tvinga fram rörelse med lappen).\n\n"
            f"Bedöm den sista repliken, sagd av {vard.namn}."
        )
        mod = kalla_json(MOD_SYSTEM, mod_user, budget, MOD_SCHEMA,
                         modell=args.modell, effort=args.effort_moderator,
                         max_tokens=4000, cacha_system=False)

        # Eftergiftstaket är spärrat i kod, inte bara i prompten. En moderator
        # som glömmer sin egen regel får inte bestämma över dramaturgin.
        if (mod.get("eftergift") and mod["beslut"] != "avsluta"
                and eftergifter[vard.namn] >= 1):
            mod["beslut"] = "gor_om"
            mod["skal"] = "andra eftergiften i samma segment — " + mod.get("skal", "")
            mod["lapp"] = "du ger dig inte den här gången. Du har redan gett hen en poäng."

        logg.skriv({"fas": "inspelning", "segment": nummer, "tur": i + 1,
                    "vard": vard.namn, "tanke": tur.get("tanke", ""), "replik": replik,
                    "konvergens": round(konv, 3), "upprepning": round(upp, 3),
                    "moderator": mod, "usd": round(budget.spenderat, 4)})

        if mod["beslut"] == "gor_om":
            print(f"  ✗ {vard.namn}: {replik[:58]}…  ({mod['skal'][:58]})")
            transkript.pop()
            lapp = mod["lapp"]
            continue

        print(f"  {vard.namn}: {replik[:78]}")
        if tur.get("tanke"):
            print(f"      ⤷ tänker: {tur['tanke'][:66]}")
        lapp = mod["lapp"]

        if mod.get("eftergift"):
            eftergifter[vard.namn] += 1
            sedan_rorelse = 0
            print(f"      ⤷ eftergift ({eftergifter[vard.namn]}/1 för {vard.namn})")
        else:
            sedan_rorelse += 1

        if mod["beslut"] == "avsluta":
            print(f"  ── segmentet slut: {mod['skal'][:70]}")
            break

    return transkript


def skriv_ratape(sokvag: Path, slug: str, plan: dict, allt):
    rader = [f"# Rått band · {slug}", "",
             f"**Källa:** `{plan.get('källa', '')}`",
             "**Medverkande:** BOSSE, VERA", "",
             "*Oklippt. Tankarna ligger i HTML-kommentarer och hörs inte.*", "",
             "---", ""]
    for seg, turer in allt:
        rader += [f"### {seg.get('nummer')} · {seg.get('tema')}", ""]
        for t in turer:
            rader.append(f"**{t['roll']}:** {t['replik']}")
            if t.get("tanke"):
                rader.append(f"<!-- tänker: {t['tanke']} -->")
            rader.append("")
        rader += ["---", ""]
    sokvag.write_text("\n".join(rader), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description="Fas 2: inspelningen, med moderator.")
    ap.add_argument("plan", type=Path, help="podd/<slug>.plan.json")
    ap.add_argument("--torrkor", action="store_true", help="bygg prompter, anropa inte")
    ap.add_argument("--budget", type=float, default=20.0, help="tak i USD (default 20)")
    ap.add_argument("--modell", default=MODELL)
    ap.add_argument("--effort-vard", default="medium",
                    choices=["low", "medium", "high", "xhigh", "max"],
                    help="hur mycket värdarna tänker per replik")
    ap.add_argument("--effort-moderator", default="low",
                    choices=["low", "medium", "high", "xhigh", "max"],
                    help="moderatorn fäller en snabb dom, inte en utredning")
    ap.add_argument("--maxturer", type=int, default=18, help="turer per segment")
    ap.add_argument("--utan-forarbete", action="store_true",
                    help="kör utan fas 1 — värdarna går in oförberedda")
    ap.add_argument("--segment", type=str, default=None, help="t.ex. 01,03")
    ap.add_argument("--fro", type=int, default=None,
                    help="fast val av underströmmar när förarbete saknas")
    args = ap.parse_args()

    plan = json.loads(las(args.plan))
    slug = plan.get("slug", args.plan.stem.replace(".plan", ""))
    segment = plan.get("segment", [])
    if args.segment:
        valda = {s.strip() for s in args.segment.split(",")}
        segment = [s for s in segment if s.get("nummer") in valda]
    if not segment:
        raise SystemExit("Inga segment att spela in.")

    # Fas 1 bestämmer underströmmarna. Utan den lottas de här i stället.
    fil_forarbete = PODD / f"{slug}.forarbete.json"
    sparat = {}
    if fil_forarbete.exists():
        sparat = json.loads(las(fil_forarbete))
    elif not args.utan_forarbete:
        raise SystemExit(
            f"Hittar inget förarbete ({fil_forarbete.relative_to(ROT)}).\n"
            f"Kör fas 1 först:\n\n"
            f"    python3 podd/tools/forarbete.py {args.plan}\n\n"
            f"Eller kör --utan-forarbete om värdarna ska gå in oförberedda.")

    vardar = ladda_alla(args.fro, sparat.get("understrommar"))
    for namn, vard in vardar.items():
        vard.forarbete = sparat.get("forarbete", {}).get(namn, {})

    agenda = sparat.get("agenda") or {}
    avs, mot = agenda.get("fran"), agenda.get("till")
    if avs and mot and vardar[avs].forarbete:
        vardar[mot].agenda_fran = rendera_agenda(avs, vardar[avs].forarbete)
        vardar[avs].agenda_till = mot

    print(f"FAS 2 · INSPELNING   {slug}  ·  {len(segment)} segment  ·  {args.modell}")
    for v in vardar.values():
        print(f"  {v.namn}: underström «{v.understrom[:60]}…»  "
              f"{len(v.forarbete.get('punkter', []))} förberedda punkter"
              + (f", fick agenda av {avs}" if v.agenda_fran else ""))

    budget = Budget(args.budget)
    logg = Logg(PODD / f"{slug}.simulering.jsonl")
    turordning = [vardar["BOSSE"], vardar["VERA"]]

    allt = [(seg, kor_segment(seg, turordning, args, budget, logg)) for seg in segment]

    if args.torrkor:
        turer = len(segment) * args.maxturer
        print(f"\nTorrkörning klar. {len(segment)} segment × högst {args.maxturer} turer "
              f"= högst {turer} repliker, vardera ett värd- plus ett moderatorsanrop "
              f"≈ {turer * 2} anrop.")
        return

    fil_md = PODD / f"{slug}.ratape.md"
    fil_json = PODD / f"{slug}.ratape.json"
    skriv_ratape(fil_md, slug, plan, allt)
    fil_json.write_text(json.dumps(
        {"slug": slug, "källa": plan.get("källa", ""),
         "segment": [{"seg": s, "turer": t} for s, t in allt]},
        ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nSkrev {fil_md.relative_to(ROT)} och {fil_json.relative_to(ROT)}")
    print(budget.rad())
    print(f"\nNästa steg:\n  python3 podd/tools/klippa-podd.py {args.plan}")


if __name__ == "__main__":
    main()
