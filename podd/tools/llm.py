"""llm.py — allt som pratar med modellen, plus budget och logg.

Varje anrop är fristående: ett systemmeddelande, ett användarmeddelande, inget
minne mellan anropen. Det minne en agent har är exakt det som renderas in i
prompten av den som anropar — ingenting annat. Det är hela poängen med
uppdelningen, och därför finns det ingen samtalshistorik här.

Nyckel: ANTHROPIC_API_KEY i podd/.env (eller i miljön). Filen är git-ignorerad.

    ANTHROPIC_API_KEY=sk-ant-...

Beroende:

    pip install anthropic
"""

import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
PODD = TOOLS.parent
ROT = PODD.parent

# Modellval. Poddarna och klipparen gör den svåra bedömningen, moderatorn den
# snabba — men alla tre kör samma modell som standard. Det som skiljer dem åt är
# `effort`, som styr hur mycket modellen tänker innan den svarar.
MODELL = "claude-opus-5"

# USD per miljon tokens: (in, ut). Cacheläsning ≈ 0,1× in, cacheskrivning ≈ 1,25× in.
PRISLISTA = {
    "claude-opus-5": (5.0, 25.0),
    "claude-opus-4-8": (5.0, 25.0),
    "claude-sonnet-5": (2.0, 10.0),
    "claude-haiku-4-5": (1.0, 5.0),
}


def las_env(fil: Path = None):
    """Läser podd/.env utan beroenden. Rör aldrig en variabel som redan är satt
    i miljön — den som exporterar en nyckel i skalet ska vinna över filen."""
    fil = fil or PODD / ".env"
    if not fil.exists():
        return
    for rad in fil.read_text(encoding="utf-8").splitlines():
        rad = rad.strip()
        if not rad or rad.startswith("#") or "=" not in rad:
            continue
        nyckel, varde = rad.split("=", 1)
        nyckel = nyckel.strip()
        if nyckel and nyckel not in os.environ:
            os.environ[nyckel] = varde.strip().strip('"').strip("'")


_klient = None


def klient():
    global _klient
    if _klient is not None:
        return _klient
    las_env()
    try:
        import anthropic
    except ImportError:
        raise SystemExit(
            "Paketet 'anthropic' saknas.\n\n    pip install anthropic\n")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        raise SystemExit(
            "ANTHROPIC_API_KEY saknas.\n\n"
            f"Lägg den i {(PODD / '.env').relative_to(ROT)} (git-ignorerad):\n\n"
            "    ANTHROPIC_API_KEY=sk-ant-...\n")
    _klient = anthropic.Anthropic()
    return _klient


@dataclass
class Budget:
    """Tak i USD. Varje anrop bokförs, och taket avbryter körningen i stället
    för att låta en loop i en simulering kosta pengar hela natten."""
    tak: float
    spenderat: float = 0.0
    anrop: int = 0
    tokens_in: int = 0
    tokens_ut: int = 0
    cachelast: int = 0

    def bokfor(self, modell: str, usage) -> float:
        pris_in, pris_ut = PRISLISTA.get(modell, PRISLISTA[MODELL])
        skrivet = getattr(usage, "cache_creation_input_tokens", 0) or 0
        last = getattr(usage, "cache_read_input_tokens", 0) or 0
        färskt = getattr(usage, "input_tokens", 0) or 0
        ut = getattr(usage, "output_tokens", 0) or 0
        usd = (färskt * pris_in + skrivet * pris_in * 1.25 + last * pris_in * 0.1
               + ut * pris_ut) / 1_000_000
        self.spenderat += usd
        self.anrop += 1
        self.tokens_in += färskt + skrivet + last
        self.tokens_ut += ut
        self.cachelast += last
        if self.spenderat > self.tak:
            raise SystemExit(
                f"\nBUDGETTAK NÅTT: {self.spenderat:.2f} USD > {self.tak:.2f} USD "
                f"efter {self.anrop} anrop. Avbryter.")
        return usd

    def rad(self) -> str:
        return (f"{self.anrop} anrop · {self.spenderat:.2f} USD av {self.tak:.2f} "
                f"· {self.tokens_in} in / {self.tokens_ut} ut "
                f"· {self.cachelast} lästa ur cache")


@dataclass
class Logg:
    """En rad JSON per händelse. Det är den här filen man läser efteråt när ett
    avsnitt blev dåligt och man vill veta var det gick fel."""
    sokvag: Path
    rader: list = field(default_factory=list)

    def skriv(self, post: dict):
        self.rader.append(post)
        self.sokvag.parent.mkdir(parents=True, exist_ok=True)
        with self.sokvag.open("a", encoding="utf-8") as f:
            f.write(json.dumps(post, ensure_ascii=False) + "\n")


def kalla(system: str, user: str, budget: Budget, *, modell: str = MODELL,
          schema: dict = None, effort: str = "medium", max_tokens: int = 8000,
          cacha_system: bool = True) -> str:
    """Ett anrop, inget minne. Returnerar svarstexten.

    `schema` sätter structured output — svaret är då garanterat giltig JSON mot
    schemat, vilket är skillnaden mot att be modellen snällt om JSON och sedan
    städa i efterhand.

    `cacha_system` cachar systemprompten. Karaktärsfilerna är långa och identiska
    över alla turer i ett segment, så det är där pengarna finns: en cacheläsning
    kostar en tiondel av färsk inmatning. Kontrollera att det fungerar genom att
    titta på `cachelast` i budgetraden — är den noll cachar du inget."""
    c = klient()
    systemblock = [{"type": "text", "text": system}]
    if cacha_system:
        systemblock[0]["cache_control"] = {"type": "ephemeral"}

    argument = dict(
        model=modell,
        max_tokens=max_tokens,
        system=systemblock,
        messages=[{"role": "user", "content": user}],
        output_config={"effort": effort},
    )
    if schema:
        argument["output_config"]["format"] = {"type": "json_schema", "schema": schema}

    svar = _skicka(c, argument)

    if svar.stop_reason == "refusal":
        detalj = getattr(svar, "stop_details", None)
        raise SystemExit(f"Modellen avböjde begäran ({getattr(detalj, 'category', '?')}). "
                         f"Det här är en podd om Java — titta på prompten, något är fel.")
    budget.bokfor(modell, svar.usage)
    text = next((b.text for b in svar.content if b.type == "text"), "")
    return text.strip()


def _skicka(c, argument: dict):
    """Serverside fallback: avböjer modellen av policyskäl körs samma begäran om
    på en annan modell inom samma anrop. Kan den här SDK-versionen inte flaggan
    skickas begäran om utan den i stället för att dö."""
    import anthropic
    try:
        return c.beta.messages.create(
            betas=["server-side-fallback-2026-07-01"], fallbacks="default", **argument)
    except (anthropic.BadRequestError, TypeError) as fel:
        if "fallback" not in str(fel).lower() and "beta" not in str(fel).lower():
            raise
        return c.messages.create(**argument)


def kalla_json(system: str, user: str, budget: Budget, schema: dict, **kw) -> dict:
    """Som kalla(), men kräver ett objekt tillbaka."""
    rasvar = kalla(system, user, budget, schema=schema, **kw)
    try:
        return json.loads(rasvar)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", rasvar, re.S)
        if not m:
            raise SystemExit(f"Fick inget JSON tillbaka:\n{rasvar[:400]}")
        return json.loads(m.group(0))


def las(p: Path) -> str:
    return p.read_text(encoding="utf-8")
