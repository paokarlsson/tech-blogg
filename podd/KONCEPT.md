# Poddformatet: **Beroendeframkallande**

> En podd där två personer som har helt fel om precis motsatta saker
> tillsammans råkar hamna nära något som är sant.

Det här dokumentet beskriver hur ett poddmanus *genereras* ur ett blogginlägg i
`src/sv/posts/`. Idén är att inlägget redan bär sin egen dramaturgi — den ska
inte uppfinnas på nytt, den ska packas upp.

---

## 1. Varför just det här inlägget funkar som podd

`2026-09-01-mindre-ramverk-mer-java.md` är skriven i åtta numrerade sektioner
(`01 · Tanken` … `08 · Så här långt har jag kommit`). Det är åtta färdiga
poddsegment. Inlägget har dessutom en egenskap som är guld för komedi:

**Texten vägrar ta ställning.** Den säger "kanske", "en tanke", "jag vet inte hur
väl den håller". Det är intellektuellt hederligt — och fullständigt odramatiskt.

Så: ge nyansen till *ingen*. Ge ytterligheterna till två personer. Låt dem
kollidera, och låt textens faktiska slutsats falla ut ur kollisionen som en
biprodukt. Lyssnaren lär sig resonemanget genom att se det brytas isär.

---

## 2. De två personligheterna

Båda har läst samma inlägg. Båda är övertygade om att det bevisar deras sak.

> Skisserna nedan räcker för att generera ett gräl. För att generera ett *samtal*
> — talmönster, svagheter, hur de erkänner sig besegrade, hur de bär genom ett
> ämne som inte är teknik — se **[vardar/](vardar/)**, som är skrivet fristående
> från vilket inlägg som helst:
>
> | Fil | Innehåller |
> | --- | --- |
> | [vardar/bosse/](vardar/bosse/) · [vera/](vardar/vera/) | `PROFIL.md` vem hen är · `BAKGRUND.md` varför · `UNDERSTROMMAR.md` dagsform · `ROST.md` hur hen låter |
> | [vardar/KEMI.md](vardar/KEMI.md) | paret: grundaxeln, asymmetrierna, hur de bråkar, skyddsräckena |
>
> Profil och bakgrund går in i systemprompten vid varje anrop. Bakgrunden finns
> för att agenten ska veta mer än lyssnaren — den ska höras som tyngd, aldrig
> berättas som historia.

### 🧯 Bosse Boot — *ramverksmaximalisten*

- Titel på LinkedIn: "Lösningsarkitekt & Starter-entusiast".
- Reflex: varje problem besvaras inom 1,5 sekunder med *"det finns en starter för det"*.
- Talar i annotationer. Säger `@Transactional` som ett kraftuttryck.
- Djupaste rädsla: att skriva en for-loop utan att någon har godkänt den.
- **Har rätt om:** JSON, OAuth/OIDC, connection pools, avancerad telemetry.
  Svår semantik ska inte bli husmanskost.
- **Har fel om:** att räckvidden på hans reflex är oändlig. Han hämtar en
  hel familj av bibliotek för att formatera ett datum.

### 🔪 Vera Void — *JDK-puristen*

- Kompilerar ibland med `javac` för hand "för att känna doften".
- Raderade sitt eget `pom.xml` under ett anfall av klarhet i somras. Ångrar inget.
  Projektet byggde inte på nio dagar. Hon kallar det "en lärorik period".
- Citerar JDK-release notes som andra citerar poesi. "Det där har funnits sen 11.
  Du behövde bara läsa."
- **Har rätt om:** att HttpClient, records, virtuella trådar och schemaläggning
  redan ligger i lådan, och att mekanisk kod blivit billig.
- **Har fel om:** att hon mäter systemets storlek i antal JAR-filer. Hon skulle
  skriva sin egen connection pool på en fredag och menar allvar.

### 🔔 Den tredje mikrofonen: **Förbehållsklockan**

Nyansen får medvetet *ingen* personlighet. Den är en klocka. Den ringer varje
gång någon drar en slutsats utan sitt förbehåll — alltså varje gång någon
glömmer "men bara om…"-kolumnen ur inläggets tabell.

Det är seriens tesen i ett ljud: **det sanna svaret har ingen karisma.**
Därför blir det aldrig taget på allvar. Därför behövs klockan.

---

## 3. Humormotorn (fem regler, för att skämten ska gå att generera)

1. **Konflikt in, villkor ut.** Varje segment öppnar i gräl och stänger på
   inläggets faktiska förbehåll. Grälet är underhållningen, förbehållet är lärdomen.
2. **Ingen får ha rätt två segment i rad.** Om Vera vann `02`, vinner Bosse `03`.
   Detta är hårdkodat i generatorn och är det som gör podden pedagogisk i stället
   för partisk.
3. **Fakta får bara komma ur källtexten. Skämt får hittas på fritt.**
   Varje tekniskt påstående i manuset bär en `källa:`-rad tillbaka till en mening
   i inlägget. Ingen källa = repliken ska bort.
4. **Absurditeten sitter i personerna, aldrig i tekniken.** Java-fakta ska vara
   korrekt även när repliken är korkad. En podd som skämtar *fel* om Hibernate
   lär ut fel om Hibernate.
5. **Inläggets `.quote`-block sägs ordagrant, utan skämt.** Det är segmentets
   ankare. Två sekunders tystnad före och efter. Efter en minuts tramsande
   landar en rak mening ovanligt hårt.

## 4. Återkommande gags (bits)

| Bit | Trigger | Vad som händer |
| --- | --- | --- |
| **Isberget** | Någon säger "det är ju bara en liten dependency" | Titanic-stråkar. Vera läser upp det transitiva trädet som en dödsruna. |
| **Trappan** | Segment 03 (inläggets fyrastegsflöde) | Frågesport. Lyssnaren ska gissa vilket steg som gäller innan panelen gör det. Bosse svarar konsekvent "4". Vera svarar konsekvent "1". |
| **CVE-bingo** | Vera skriver egen kod som visar sig vara en säkerhetsyta | Bosse ropar BINGO. Ibland med rätta. |
| **Räknarna** | Löpande | Bosse räknar rader kod. Vera räknar JAR-filer. Ingen av dem mäter förvaltningskostnad — vilket avslöjas först i segment 08. Det är hela poängen och den ska inte förklaras förrän då. |
| **"Fungerar på min maskin"** | Slutvinjett | Sägs unisont. Är alltid osant för minst en av dem. |

---

## 5. Genereringspipelinen

```
src/sv/posts/*.md
      │
      │  0. EXTRAHERA    podd/tools/generera-podd.js
      ▼
podd/<slug>.plan.json           ← segment, källcitat, roller, konfliktform
      │
      │  1. FÖRARBETE    podd/tools/forarbete.py
      │                  två skilda anrop. Var och en läser texten på sitt sätt,
      │                  associerar, minns egna historier, skriver punktlista.
      │                  Den ena skickar sina hållpunkter till den andra.
      ▼
podd/<slug>.forarbete.json      ← + läsbar kopia i vardar/<vard>/forarbete/
      │
      │  2. INSPELNING   podd/tools/simulera-podd.py
      │                  två agenter turas om. Varje tur = en tanke + en replik.
      │                  Moderatorn ser allt, kastar turer, viskar lappar.
      ▼
podd/<slug>.ratape.md + .json   ← oklippt band
      │
      │  3. KLIPPNING    podd/tools/klippa-podd.py
      │                  klipparen väljer vilka turer som överlever. Bara bort,
      │                  aldrig om — annars tappar påståendena sin källa.
      ▼
podd/<slug>.klippt.md           ← produktionsmanus
      │
      │  4. RÖSTSÄTT     podd/tools/rosta-podd.js   (se ROSTNING.md)
      ▼
podd/audio/<slug>/*.mp3
```

Varje fas lämnar en artefakt som går att läsa, rätta för hand och köra vidare
från. Hela förloppet loggas till `podd/<slug>.simulering.jsonl` — en rad per tur,
med moderatorns beslut och kostnaden så långt.

Ett manus som ska sparas döps om till `podd/avsnitt-NN-<slug>.md`; allt annat
genererat är git-ignorerat.

### Steg 0 — Extrahera

Inlägget parsas till segment. Varje `<section>` med en `.eyebrow` blir ett segment.
Ur den plockas rubrik (tesen), brödtext (fakta), `.quote` (ankaret) och
strukturerade element (kort, flöden, tabeller, metrics).

### Konfliktformen kommer ur strukturen

Generatorn behöver inte gissa formen — HTML:en i inlägget säger vilken den är:

| Element i sektionen | Konfliktform | Varför |
| --- | --- | --- |
| `.cards` med `.tag remove/assess/keep` | **Snabbrunda** | Taggen delar redan ut segrarna: `remove` → Vera, `keep` → Bosse, `assess` → gräl som Förbehållsklockan avbryter |
| `.flow` / `.step` | **Trappan** | Ett numrerat flöde *är* en frågesport |
| `<table>` | **Villkorsklockan** | Sista kolumnen ("men bara om…") är bokstavligen förbehållet |
| `.metrics` | **Isberget** | En lista med dolda kostnader vill läsas som en dödsruna |
| inget av ovan | **Duell** | Fri dialog kring rubrikens tes |

### QA innan röstsättning

Läs igenom `podd/<slug>.klippt.md` innan du bränner ElevenLabs-kvot på den.

- **Spårbarhet:** varje faktapåstående ska gå att hitta i källtexten. Undantaget
  är värdarnas egna minnen, som hittas på i fas 1 och är deras.
- **Vinstbalans:** ingen vinner två segment i rad; totalen ska vara jämn.
- **Replikbalans:** ±15 % taltid mellan Bosse och Vera.
- **Ankare:** varje `.quote` finns ordagrant i manuset.
- **Längd:** ~150 ord/minut talad svenska. Åtta segment ≈ 22–26 min.

---

## 6. Så kör du det

Simuleringen kräver en Anthropic-nyckel i `podd/.env` (git-ignorerad) och
paketet `anthropic`:

```bash
echo 'ANTHROPIC_API_KEY=sk-ant-...' >> podd/.env
pip install -r podd/tools/requirements.txt
```

Sedan en fas i taget. **Kör alltid `--torrkor` först** — då byggs alla prompter
och skrivs ut, men inget anrop görs och ingenting kostar:

```bash
node podd/tools/generera-podd.js src/sv/posts/2026-09-01-mindre-ramverk-mer-java.md

python3 podd/tools/forarbete.py     podd/mindre-ramverk-mer-java.plan.json --torrkor
python3 podd/tools/forarbete.py     podd/mindre-ramverk-mer-java.plan.json
python3 podd/tools/simulera-podd.py podd/mindre-ramverk-mer-java.plan.json
python3 podd/tools/klippa-podd.py   podd/mindre-ramverk-mer-java.plan.json
```

Varje fas har ett eget budgettak i USD (`--budget`) som avbryter körningen i
stället för att låta en loop kosta pengar hela natten, och `--segment 01,03` för
att köra om en enda bit. Underströmmarna lottas i fas 1 — `--fro 42` ger samma
lottning igen.

Modell och tankedjup styrs per roll. Standard är `claude-opus-5` överallt, med
`effort` högt där bedömningen är svår och lågt där den ska vara snabb:

| Roll | Fas | `effort` | Varför |
| --- | --- | --- | --- |
| Värdarna | 1 · förarbete | `high` | avsnittets råmaterial — snåla inte här |
| Värdarna | 2 · inspelning | `medium` | en replik i taget, inte en utredning |
| Moderatorn | 2 · inspelning | `low` | fäller en snabb dom per tur |
| Klipparen | 3 · klippning | `high` | avsnittets enda helhetsbedömning |

`podd/avsnitt-01-mindre-ramverk-mer-java.md` är ett färdigskrivet exempel på hur
output ska se ut — använd det som referens för ton och täthet.

---

## 7. Vidare spår (osorterat spånande)

- **Engelsk version gratis.** `src/en/posts/` har samma `translationKey` och samma
  sektionsstruktur, så samma generator ger ett engelskt manus med samma beats.
  Bosse och Vera behöver dock nya namn — "Boot Bob" och "Vera Void" funkar.
- **Publicera manuset som inlägg.** Ett manus är läsbart innehåll i sig. Egen
  layout `podd.njk`, kapitelmarkeringar som `<h3>`, RSS-fältet återanvänds.
- **Lyssnarsegment: "Din dependency, vår domstol".** Skicka in en `pom.xml`.
  Bosse försvarar den. Vera åtalar den. Klockan dömer.
- **Anti-gag som skyddsräcke:** podden får aldrig skämta om att ett team
  *borde* skriva sin egen krypto- eller OAuth-kod utan att Bosse omedelbart
  vinner den ronden. Inlägget är tydligt där, och en podd som driver med det
  förlorar sin poäng.
- **Röstsyntes:** manusformatet (`**NAMN:** replik`) är trivialt att splitta per
  talare för TTS. Förbehållsklockan blir en ljudfil, inte en röst.
