# 🧯 Bosse Boot — röst

Röstsättningen sker med ElevenLabs `eleven_v3` via
[`../../tools/rosta-podd.js`](../../tools/rosta-podd.js). Gränser, chunkning och
hela taggöversättningen står i [`../../ROSTNING.md`](../../ROSTNING.md) — den
här filen är bara Bosses del.

## Identitet i pipelinen

| | |
| --- | --- |
| Talarnyckel i manus | `**BOSSE:**` |
| `voice_id` | står i [`../../roster.json`](../../roster.json) under `roster.BOSSE` |
| Miljövariabel som åsidosätter | `ROST_BOSSE` |
| Unisont med Vera | `**BÅDA:**` — används på slutvinjetten |

## Hans regiord

Regi ska vara sällsynt. Moderatorn kastar en replik som bär samma regiord som
talarens förra — tre `*(surt)*` i rad är ingen karaktär, det är en tic.

| Regiord | När |
| --- | --- |
| `*(skrattar)*` | ofta — det är hans grundläge, och alltid åt sig själv först |
| `*(surt)*` | när han förlorat en poäng han tyckte var hans |
| `*(nöjt)*` | när han fått rätt, och strax innan han blir generös på ett pinsamt sätt |
| `*(paus)*` | **sparsamt.** Pausen är alltid ett nederlag hos honom, eftersom han annars aldrig pausar |

`*(rakt, utan skämt)*` gäller båda och bara på ankarcitaten. Där kopplas
personligheten bort helt. Det är hela poängen med citaten.

## Prosodi

Snabb, tvärsäker, accelererar när han är osäker. Han fyller varje tystnad inom en
sekund — i manuset syns det som att han sällan lämnar en replik kort.

Två former som måste överleva till ljud:

- **Självavbrottet.** *"Ja, det är ju… vänta. Det är som—"* Tankstrecket i slutet
  betyder att Vera klipper av honom; det ska höras som ett avbrott, inte ett slut.
- **Upptäcktsljudet.** *"Åh."* — egen mening, egen rad om det behövs. Det ska
  låta som att han hellre hade sluppit fatta det.
