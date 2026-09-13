# Röstsättning med ElevenLabs (eleven_v3)

`podd/tools/rosta-podd.js` tar ett manus i `podd/` och röstsätter det med
**Text to Dialogue** — endpointen som är byggd för flera talare i samma
generering, till skillnad från vanlig Text to Speech som bara kan en röst i taget.

```bash
ROST_BOSSE=<voice_id> ROST_VERA=<voice_id> ELEVENLABS_API_KEY=<nyckel> \
  node podd/tools/rosta-podd.js podd/avsnitt-01-mindre-ramverk-mer-java.md
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

**Taggarna skickas på engelska.** API:et validerar dem inte — de är vanlig text
i `inputs[].text`, så en påhittad tagg ger inget felmeddelande. Risken är i
stället att modellen struntar i den, eller läser upp den högt. Samtliga taggar
ElevenLabs dokumenterar är engelska (`[laughs]`, `[whispers]`, `[curious]`,
`[thoughtful]`, `[sighs]`, `[sarcastic]`, `[short pause]` …) och det finns
inget i dokumentationen som säger att svenska motsvarigheter tolkas.

Manuset skrivs ändå på svenska. `TAGGAR`-listan i `rosta-podd.js` är
översättningslagret:

| I manuset | Skickas till API:et |
| --- | --- |
| `*(skrattar)*` | `[laughs]` ✅ |
| `*(paus)*`, `*(kort paus)*` | `[short pause]` ✅ |
| `*(nyfiket)*` | `[curious]` ✅ |
| `*(fundersamt)*` | `[thoughtful]` ✅ |
| `*(road)*` | `[chuckles]` ✅ |
| `*(suckar)*` | `[sighs]` ✅ |
| `*(viskar)*` | `[whispers]` ✅ |
| `*(sarkastiskt)*` | `[sarcastic]` ✅ |
| `*(torrt)*` | `[dryly]` |
| `*(surt)*`, `*(tjurigt)*` | `[annoyed]` |
| `*(motvilligt)*` | `[reluctant]` |
| `*(uppgivet)*` | `[resigned]` |
| `*(bestämt)*` | `[firm]` |
| `*(nöjt)*` | `[pleased]` |
| `*(tvekande)*` | `[hesitant]` |
| `*(skeptiskt)*` | `[skeptical]` |
| `*(varmt)*` | `[warm]` |
| `*(otåligt)*` | `[impatient]` |
| `*(rakt, utan skämt)*` | `[serious]` |

✅ = finns ordagrant i ElevenLabs dokumentation. Övriga är vanliga engelska
känsloord av samma typ som de dokumenterade, men inte explicit listade —
lyssna igenom en kort testgenerering innan du litar på dem.

Ett regi-ord som inte finns i listan faller bort tyst i stället för att bli en
tagg — lägg till det i `TAGGAR` om det ska höras.

## Vad skriptet gör med manuset

| I manuset | Blir |
| --- | --- |
| `**BOSSE:** replik` | en `inputs`-tur med Bosses `voice_id` |
| `> ankarcitat` | läggs på föregående talares tur (citatet ska sägas, inte hoppas över) |
| `*(torrt)*`, `*(fundersamt)*`, `*(nyfiket)*` m.fl. | översätts till audiotaggar som `[torrt]`, `[fundersamt]`, `[nyfiket]` — se listan `TAGGAR` i `rosta-podd.js` |
| okänt regi-ord i `*(...)*` | faller bort tyst — lägg till det i `TAGGAR` om det ska bli en audiotagg |
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
  "dialogue_settings": { "stability": 0.5 }
}
```

`settings` har bara **ett** dokumenterat fält: `stability`. Det fanns tidigare
ett `use_audio_tags: true` här — det är inte ett riktigt fält och togs bort.
Audiotaggar aktiveras inte med en flagga; de fungerar genom att stå i texten.

- **`stability`** — API:et tar ett tal 0–1, inte etiketten från webb-UI:ns
  slider. Ungefärlig mappning: `0.0` = Creative (mest uttrycksfull,
  hallucinerar ibland), `0.5` = Natural (balanserad, närmast
  referensinspelningen), `1.0` = Robust (stabil men reagerar svagt på taggar,
  ungefär som v2). `0.5` är rätt default här; sänk mot `0.0` om taggarna känns
  underspelade. (Skickar man strängen direkt, t.ex. `"natural"`, svarar API:et
  `HTTP 422 float_parsing`.)
- **`seed`** — fast värde ger reproducerbara omtagningar. Byt bara medvetet.
- **`language_code`** — `sv`. Ignoreras om modellen inte stöder koden.

## Omtagningar

Blev request 7 dålig? Rendera bara den:

```bash
node podd/tools/rosta-podd.js podd/avsnitt-01-*.md --from 7 --to 7
```

Manifestet skrivs varje körning, så filnamnen är stabila.

## Foga ihop

```bash
node podd/tools/klipp-ihop.js podd/audio/avsnitt-01-mindre-ramverk-mer-java
```

Bygger `intro → part-001 → cut → part-002 → cut → … → outro` och kodar om till
en fil. Antalet delar läses ur `manifest.json`, så det följer manuset av sig
självt. `--dry-run` skriver ut ffmpeg-kommandot utan att köra det.

Vilka sfx-filer som används står i `roster.json` under `klippning`:

```json
"klippning": {
  "intro": "sfx/signatur.mp3",
  "mellan_segment": "sfx/cut.mp3",
  "outro": "sfx/outro.mp3"
}
```

Saknas en av dem hoppas den bara över — man ska kunna lyssna igenom ett avsnitt
innan vinjetterna är klara.

Skriptet använder ffmpeg:s concat-**filter**, inte concat-demuxern med
`-c copy`. Dialogspåren kommer från ElevenLabs i `mp3_44100_128`, men
sfx-filerna kommer från annat håll och kan ha annan samplerate eller
kanaluppsättning — då ger `-c copy` en fil som spelar upp fel efter första
skarven. Filtret samplar om, till priset av en omkodning.

Kräver ffmpeg: `sudo apt install -y ffmpeg`.

Cue:er som ska mixas *inuti* ett dialogspår (i stället för mellan två) bär
`request` och `efterTur` i `manifest.json` och får läggas in för hand i en DAW
— positionerna är angivna i turindex, inte tidsstämplar.

## Musik och ljudeffekter

Text to Dialogue ger bara röstspåren. Signaturmusik, slutvinjett och
Förbehållsklockan genereras med en annan endpoint — ElevenLabs **Sound
Effects** (`/v1/sound-generation`), samma nyckel — via `podd/tools/generera-sfx.js`:

```bash
node --env-file=podd/.env podd/tools/generera-sfx.js            # allt som saknas
node --env-file=podd/.env podd/tools/generera-sfx.js --dry-run  # visa recepten
node --env-file=podd/.env podd/tools/generera-sfx.js sfx/signatur.mp3 --force
```

Recepten ligger i `podd/roster.json` under `ljud_recept`, med utfilens sökväg
som nyckel:

```json
"ljud_recept": {
  "sfx/signatur.mp3": {
    "text": "Kort podcast-signatur, fyra mjuka synthtoner, lugnt tempo…",
    "duration_seconds": 6,
    "prompt_influence": 0.4
  }
}
```

- **`duration_seconds`** — 0,5–22 s. Utelämnas den får modellen välja själv.
- **`prompt_influence`** — 0–1. Högt värde följer prompten hårdare, lågt ger
  modellen mer eget spelrum.

Filer som redan finns hoppas över, så en körning utan argument fyller bara
luckorna. `--force` skriver över — bra när man vill prova en ny prompt.

Signaturen används i båda ändar av avsnittet (intro och slutvinjett); den
behöver alltså inte genereras två gånger. Var cue:erna hör hemma står i
`manifest.json`, men positionerna är angivna som request + turindex, inte
tidsstämplar — själva mixen är fortfarande ett handarbete.

## Kostnad

Text to Dialogue debiteras per tecken, och audiotaggar räknas. Torrkörningen
skriver ut totalen — kolla den mot kvoten innan du kör skarpt. Sound Effects
debiteras separat per generering, så `--force` på ett långt recept är inte
gratis.
