# Röstsättning med ElevenLabs (eleven_v3)

`tools/rosta-podd.js` tar ett manus i `podd/` och röstsätter det med
**Text to Dialogue** — endpointen som är byggd för flera talare i samma
generering, till skillnad från vanlig Text to Speech som bara kan en röst i taget.

```bash
ROST_BOSSE=<voice_id> ROST_VERA=<voice_id> ELEVENLABS_API_KEY=<nyckel> \
  node tools/rosta-podd.js podd/avsnitt-01-mindre-ramverk-mer-java.md
```

Utan `ELEVENLABS_API_KEY` blir det **torrkörning**: manuset parsas, delas i
requests och budgeten redovisas — men inget anrop görs och ingen kvot bränns.
Kör alltid det först.

## Gränser som faktiskt styr designen

| Gräns | Värde | Konsekvens här |
| --- | --- | --- |
| Tecken per request, Text to Dialogue | **≤ 2 000** summerat över alla `inputs[].text` | Chunkaren har budget 1 800 och hård spärr 2 000 |
| Tecken per request, vanlig TTS med v3 | 3 000 | Gäller *inte* oss — dialogendpointen ligger lägre |
| Unika `voice_id` per request | max 10 | Vi använder 2 |
| Request stitching (`previous_request_ids`) | **stöds inte av `eleven_v3`** | Skarvar måste läggas där ett avbrott ändå låter naturligt |
| Ålder på request-id vid stitching | < 2 timmar, max 3 st | Irrelevant för v3, noterat för v2-fallback |

Att stitching saknas är det som formar chunkningen. Med v2 hade man kunnat sy
ihop godtyckliga bitar med bevarad prosodi. Med v3 går det inte, så varje skarv
hörs — därför läggs de **vid segmentgränserna**, där manuset ändå andas.

Inom ett segment som är för långt delas turerna **jämnt**, inte girigt. Girig
fyllning lämnar en sista request på några tiotal tecken, och en ensam kort replik
utan omgivande dialog låter platt när modellen inte har något sammanhang att
spela mot.

**Audiotaggar räknas mot budgeten.** `[skrattar]`, `[viskar]`, `[allvarligt]` är
vanlig text för modellen, inte ett enum-fält. Ett tätt taggat manus får alltså
färre repliker per request.

## Vad skriptet gör med manuset

| I manuset | Blir |
| --- | --- |
| `**BOSSE:** replik` | en `inputs`-tur med Bosses `voice_id` |
| `> ankarcitat` | läggs på föregående talares tur (citatet ska sägas, inte hoppas över) |
| `*(rakt, utan skämt)*` | översätts till audiotaggen `[allvarligt]` |
| `*Signaturmusik spelar.*` | regi-cue i manifestet — läses **inte** upp |
| `🔔` / `🎻` | sfx-cue i manifestet, mixas in efteråt |
| `**BÅDA:**` | unison-cue — se nedan |
| tabeller, rubriker, QA-protokoll | ignoreras |

### Unison går inte

Text to Dialogue turas om mellan röster; den kan inte lägga två röster ovanpå
varandra. Slutrepliken *"Det fungerar på min maskin!"* flaggas i manifestet och
måste genereras som två separata enkelröst-anrop som läggs som två spår i mixen.
Skriptet varnar för det i stället för att tyst leverera en solo-replik.

## Röst-id

Hämta id:n för kontots röster:

```bash
curl -s -H "xi-api-key: $ELEVENLABS_API_KEY" https://api.elevenlabs.io/v2/voices \
  | python3 -c 'import json,sys; [print(v["voice_id"], v["name"]) for v in json.load(sys.stdin)["voices"]]'
```

Sätt dem som `ROST_BOSSE` / `ROST_VERA` i miljön, eller fyll i `voice_id` direkt
i `podd/roster.json`. **Lägg inte in nycklar i repot** — bara röst-id:n, som inte
är hemliga.

Val av röster: Bosse ska låta snabb och tvärsäker, Vera torr och långsam. Kontrasten
i tempo bär mer av komiken än rösternas klangfärg gör.

## Inställningar

`podd/roster.json`:

```json
{
  "model_id": "eleven_v3",
  "output_format": "mp3_44100_128",
  "language_code": "sv",
  "seed": 20260901,
  "max_tecken_per_request": 1800,
  "dialogue_settings": { "stability": "natural", "use_audio_tags": true }
}
```

- **`stability`** — `creative` (mest uttrycksfull, hallucinerar ibland),
  `natural` (balanserad, närmast referensinspelningen), `robust` (stabil men
  reagerar svagt på taggar, ungefär som v2). `natural` är rätt default här;
  `creative` om taggarna känns underspelade.
- **`seed`** — fast värde ger reproducerbara omtagningar. Byt bara medvetet.
- **`language_code`** — `sv`. Ignoreras om modellen inte stöder koden.

## Omtagningar

Blev request 7 dålig? Rendera bara den:

```bash
node tools/rosta-podd.js podd/avsnitt-01-*.md --from 7 --to 7
```

Manifestet skrivs varje körning, så filnamnen är stabila.

## Foga ihop

```bash
cd podd/audio/avsnitt-01-mindre-ramverk-mer-java
ffmpeg -f concat -safe 0 -i concat.txt -c copy avsnitt-01.mp3
```

`-c copy` funkar eftersom alla delar har samma `output_format`. Sfx-cue:erna i
`manifest.json` bär `request` och `efterTur` och kan läggas in i en DAW eller
med ett filterkomplex — de mixas inte automatiskt.

## Kostnad

Text to Dialogue debiteras per tecken, och audiotaggar räknas. Torrkörningen
skriver ut totalen (avsnitt 1: ca 13 200 tecken över 11 requests) — kolla den mot
kvoten innan du kör skarpt.
