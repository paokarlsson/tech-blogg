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
> ämne som inte är teknik — se **[PERSONLIGHETER.md](PERSONLIGHETER.md)**, som är
> skriven fristående från vilket inlägg som helst.

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
      │  1. EXTRAHERA   tools/generera-podd.js
      ▼
podd/<slug>.plan.json      ← segment, källcitat, roller, konfliktform
      │
      │  2. PROMPTA     podd/<slug>.prompt.md  (klar att klistra in i en LLM)
      ▼
  utkast till manus
      │
      │  3. QA-PASS     spårbarhet · vinstbalans · replikbalans · längd
      ▼
podd/avsnitt-NN-<slug>.md  ← produktionsmanus
```

### Steg 1 — Extrahera

Inlägget parsas till segment. Varje `<section>` med en `.eyebrow` blir ett segment.
Ur den plockas rubrik (tesen), brödtext (fakta), `.quote` (ankaret) och
strukturerade element (kort, flöden, tabeller, metrics).

### Steg 2 — Välj konfliktform ur strukturen

Generatorn behöver inte gissa formen — HTML:en i inlägget säger vilken den är:

| Element i sektionen | Konfliktform | Varför |
| --- | --- | --- |
| `.cards` med `.tag remove/assess/keep` | **Snabbrunda** | Taggen delar redan ut segrarna: `remove` → Vera, `keep` → Bosse, `assess` → gräl som Förbehållsklockan avbryter |
| `.flow` / `.step` | **Trappan** | Ett numrerat flöde *är* en frågesport |
| `<table>` | **Villkorsklockan** | Sista kolumnen ("men bara om…") är bokstavligen förbehållet |
| `.metrics` | **Isberget** | En lista med dolda kostnader vill läsas som en dödsruna |
| inget av ovan | **Duell** | Fri dialog kring rubrikens tes |

### Steg 3 — QA innan inspelning

- **Spårbarhet:** varje faktapåstående har en `källa:`-rad.
- **Vinstbalans:** ingen vinner två segment i rad; totalen ska vara jämn.
- **Replikbalans:** ±15 % taltid mellan Bosse och Vera.
- **Ankare:** varje `.quote` finns ordagrant i manuset.
- **Längd:** ~150 ord/minut talad svenska. Åtta segment ≈ 22–26 min.

---

## 6. Så kör du det

```bash
node tools/generera-podd.js src/sv/posts/2026-09-01-mindre-ramverk-mer-java.md
```

Ger `podd/<slug>.plan.json` och `podd/<slug>.prompt.md`.
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
