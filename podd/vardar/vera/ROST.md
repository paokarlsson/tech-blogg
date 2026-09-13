# 🔪 Vera Void — röst

Röstsättningen sker med ElevenLabs `eleven_v3` via
[`../../tools/rosta-podd.js`](../../tools/rosta-podd.js). Gränser, chunkning och
hela taggöversättningen står i [`../../ROSTNING.md`](../../ROSTNING.md) — den
här filen är bara Veras del.

## Identitet i pipelinen

| | |
| --- | --- |
| Talarnyckel i manus | `**VERA:**` |
| `voice_id` | står i [`../../roster.json`](../../roster.json) under `roster.VERA` |
| Miljövariabel som åsidosätter | `ROST_VERA` |
| Unisont med Bosse | `**BÅDA:**` — används på slutvinjetten |

## Hennes regiord

Regi ska vara sällsynt. Moderatorn kastar en replik som bär samma regiord som
talarens förra.

| Regiord | När |
| --- | --- |
| `*(torrt)*` | grundläget när hon konstaterar något förödande |
| `*(motvilligt)*` | eftergiften. Ett ord, och sedan aldrig mer om det |
| `*(tvekande)*` | sällsynt, och betyder att hon faktiskt inte vet |
| `*(skeptiskt)*` | på frågekedjorna, inte på invändningarna |
| `*(skrattar)*` | **max en gång per avsnitt.** Då betyder det något |

`*(rakt, utan skämt)*` gäller båda och bara på ankarcitaten. Där kopplas
personligheten bort helt. Det är hela poängen med citaten.

## Prosodi

Torrt och långsamt, och saktar in ytterligare när hon blir oense. Där Bosse går
fortare saktar hon in — det är hela eskaleringsgrammatiken och den bär mer av
komiken än orden gör.

Tre former som måste överleva till ljud:

- **Ettordsturen.** *"Nej."* · *"Var?"* · *"Mitt."* En replik på ett ord får inte
  klippas bort som transportsträcka, och den ska inte få en audiotagg — den
  klarar sig på tystnaden runt omkring.
- **Pausen hon vägrar fylla.** Skrivs inte ut som regi. Den uppstår av att hennes
  replik är slut och Bosses nästa är för snabb.
- **Ekot.** Hon upprepar motpartens nyckelord platt, som ett konstaterande. Det
  ska låta oförändrat — ingen ironi i tonen, det är det som gör det grymt.
