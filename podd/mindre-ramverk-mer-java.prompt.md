# Skriv poddmanus: "Beroendeframkallande" — Tänk om vi behövde färre ramverk?

Ingress ur inlägget: *Vi har blivit riktigt bra på att lägga till bibliotek. Jag har börjat undra om nästa förbättring kan vara att ta bort några – utan att göra systemet dummare, farligare eller svårare att drifta. Det här är ett resonemang, inte en slutsats.*

## Värdar
- **Bosse Boot** (ramverksmaximalist). Svarar allt med 'det finns en starter för det'. Har rätt om JSON, OAuth/OIDC, connection pools och telemetry. Har fel om räckvidden på sin egen reflex.
- **Vera Void** (JDK-purist). Citerar release notes som poesi. Har rätt om vad JDK:n redan ger. Har fel om att systemets storlek mäts i JAR-filer.
- **Förbehållsklockan** 🔔 — inte en person, en klocka. Ringer när någon drar en slutsats utan sitt villkor.

## Hårda regler
- Fakta får bara komma ur källtexten. Skämt får hittas på fritt.
- Varje faktapåstående får en 'källa:'-rad tillbaka till en mening i inlägget.
- Absurditeten sitter i personerna, aldrig i tekniken — Java-fakta ska vara korrekt även i en dum replik.
- Ankarcitaten sägs ordagrant, utan skämt, med två sekunders tystnad före och efter.
- Ingen vinner två segment i rad.

## Format
`**NAMN:** replik` per rad. Regianvisningar i *kursiv* på egen rad. Ankarcitat i blockquote.

## Segment

### 01 · Tanken — ca 450 ord
**Tes:** Det här handlar inte om att Spring är problemet
**Konfliktform:** Duell. Fri dialog kring tesen. Öppna i oenighet, stäng på inläggets eget förbehåll.
**Segmentet vinns av:** vera
**Ankare (sägs ordagrant):**
> Java har inte blivit ett nytt Spring. Men kanske har gränsen för vad som behöver ett ramverk flyttat sig lite?
**Faktaunderlag (enda tillåtna källan för tekniska påståenden):**
- Spring Boot löser många svåra problem, och gör det bra. För publika API:er, säkerhet, avancerad routing, observability och stora integrationsytor är Spring antagligen fortfarande det billigaste alternativet totalt sett.
- Men Spring har blivit så självklart att jag misstänker att vi ibland når efter det även när problemet är mindre än lösningen. Det är den misstanken jag vill undersöka här.
- En liten intern tjänst behöver kanske bara några HTTP-anrop, en databas, ett utgående anrop och lite affärslogik. I Java 25 finns redan HTTP-klient, JDBC, schemaläggning, records, loggning, JFR/JMX och moderna samtidighetsverktyg. Virtuella trådar gör dessutom vanlig, blockerande kod betydligt mer attraktiv för I/O än den var för några år sedan.

### 02 · Förvaltningsytan — ca 450 ord
**Tes:** Kanske är beroenden lite av ett isberg
**Konfliktform:** Isberget. Vera läser posterna som en dödsruna, Bosse avfärdar dem som 'bara transitivt'. Titanic-stråkarna spelas exakt en gång, inte två.
**Segmentet vinns av:** bosse
**Poster:**
- **Versioner** — Uppgraderingar, kompatibilitet och koordinering.
- **Säkerhet** — CVE:er, parser- och nätverksyta, patcharbete.
- **Semantik** — Dolda regler, proxybeteenden och lifecycle.
- **Förändring** — Hur mycket behöver förstås nästa gång kraven flyttar sig?
**Faktaunderlag (enda tillåtna källan för tekniska påståenden):**
- När vi tittar på en pom.xml eller build.gradle ser vi bara en del av systemets tekniska yta. Under den finns transitiva bibliotek, versionskopplingar, autokonfiguration, proxyer, annotation processing och konventioner som någon behöver förstå den dagen något går fel.
- Att räkna JAR-filer känns därför som ett trubbigt mått. En liten extern dependency kan vara mycket billig. Fyrahundra rader egen OAuth-kod kan vara mycket dyr.
- Med minimalism menar jag alltså inte minst kod eller noll bibliotek. Snarare mindre onödig semantik – mindre teknik som teamet behöver bära över tid.

### 03 · Ett förslag på ordning — ca 450 ord
**Tes:** Tänk om vi frågade i den här ordningen?
**Konfliktform:** Trappan. Kör stegen som frågesport — lyssnaren ska hinna gissa före panelen. Bosse svarar alltid 4. Vera svarar alltid 1. Rätt svar ligger nästan alltid däremellan.
**Segmentet vinns av:** vera
**Steg:**
- 1. 1. Behövs det? Behövs beteendet över huvud taget? En cache eller intern event-bus som aldrig byggs har ingen implementation att förvalta.
- 2. 2. Finns det i JDK? Finns en direkt och tillräcklig lösning i Java 25? Till exempel HTTP-klient, filer, Base64, scheduling.
- 3. 3. Räcker lite egen kod? Är semantiken enkel och lokal? Mappning, konfiguration, en liten retry-loop eller en composition root kan bli ganska tydlig vanlig Java.
- 4. 4. Låt specialisten ta det Handlar det om JSON, OAuth/OIDC, anslutningspool, brokerprotokoll eller avancerad telemetry? Då tror jag ett moget bibliotek nästan alltid är billigare.
**Faktaunderlag (enda tillåtna källan för tekniska påståenden):**
- I stället för att börja med frågan “vilket bibliotek ska ersätta detta?” skulle man kunna gå igenom fyra steg. Ju längre åt höger vi kommer, desto mer specialiserad semantik väljer vi att låta någon annan äga. Ordningen är ingen sanning – mest ett sätt att göra valet medvetet.

### 04 · Var Spring kanske passar bäst — ca 450 ord
**Tes:** Tänk om Spring fick bo vid kanten?
**Konfliktform:** Ritningen. Beskriv arkitekturen i ljud — lagren måste gå att höra utan bild. Båda tror att diagrammet bevisar deras sak. Ingen av dem har fel om sitt eget lager.
**Segmentet vinns av:** bosse
**Lager:**
- Omvärld: HTTP · identitet · drift
- Kanten: Spring när det hjälper
- Kärnan: Vanlig Java
- Gränser: Små adapters
**Faktaunderlag (enda tillåtna källan för tekniska påståenden):**
- Den idé jag själv tycker är mest intressant handlar inte om att ta bort Spring Boot. Den handlar om att kanske sluta låta Spring vara applikationens huvudsakliga programmeringsmodell.
- Min tanke är att om kärnan är fri från Spring blir nästa beslut mindre dramatiskt. En komplex tjänst kan lugnt stanna på avskalat Boot. En liten intern tjänst skulle senare kunna gå längre mot ren JDK. En batch eller worker behövde kanske aldrig Spring från början. Men det är just en tanke – jag vet inte hur väl den håller i era system.

### 05 · Några saker jag är nyfiken på — ca 450 ord
**Tes:** Allt behöver nog inte behandlas lika
**Konfliktform:** Snabbrunda. Ett kort i taget, max fyra repliker per kort. Taggen delar ut segern: `remove` → Vera, `keep` → Bosse, `assess` → gräl som Förbehållsklockan avbryter.
**Segmentet vinns av:** delad
**Kort:**
- `remove` **Lombok och mappare** — Records och explicit kod gör att en del av den mekaniska hjälpen känns mindre värdefull än den gjorde tidigare.
- `remove` **Utgående HTTP** — JDK HttpClient verkar räcka långt för vanlig service-to-service-kommunikation.
- `assess` **Spring DI** — Konstruktorinjektion behöver ingen container. Samtidigt kan en stor och dynamisk objektgraf mycket väl motivera Spring.
- `assess` **JPA / Hibernate** — För tydlig SQL och en begränsad modell kan JDBC vara enklare. För rika objektgrafer är ORM antagligen fortfarande billigare.
- `keep` **JSON och säkerhet** — Generell JSON-parsning och OAuth/OIDC bär på svår semantik som sällan bör bli egen infrastruktur.
- `keep` **Connection pool** — JDBC finns i JDK, men en produktionsmässig pool gör det inte. HikariCP känns som ett självklart kvarvarande beroende.
**Faktaunderlag (enda tillåtna källan för tekniska påståenden):**
- Records och explicit kod gör att en del av den mekaniska hjälpen känns mindre värdefull än den gjorde tidigare.
- JDK HttpClient verkar räcka långt för vanlig service-to-service-kommunikation.
- Konstruktorinjektion behöver ingen container. Samtidigt kan en stor och dynamisk objektgraf mycket väl motivera Spring.
- För tydlig SQL och en begränsad modell kan JDBC vara enklare. För rika objektgrafer är ORM antagligen fortfarande billigare.
- Generell JSON-parsning och OAuth/OIDC bär på svår semantik som sällan bör bli egen infrastruktur.
- JDBC finns i JDK, men en produktionsmässig pool gör det inte. HikariCP känns som ett självklart kvarvarande beroende.

### 06 · Vad skulle vi vinna? — ca 450 ord
**Tes:** Om det stämmer handlar det om förvaltningskostnad
**Konfliktform:** Villkorsklockan. Läs raderna som löften, och låt klockan ringa på sista kolumnen. Ingen får komma undan ett 'om vi minskar X får vi Y' utan sitt 'men bara om'.
**Segmentet vinns av:** bosse
**Löfte → villkor (klockan ringer på sista ledet):**
- Minska *Externa dependency families* → *Färre separata versions- och uppgraderingsspår* — men bara om *Vi inte ersätter dem med stora interna ramverk*
- Minska *Spring-typer i domänen* → *Mindre påverkan av ramverksuppgraderingar och enklare tester* — men bara om *Gränserna mellan kärna och adapters är tydliga*
- Minska *Runtime-magi* → *Synligare kontrollflöde och enklare felsökning* — men bara om *Den explicita koden förblir liten och begriplig*
- Minska *Överdriven standardisering i kod* → *Mindre lokal infrastruktur* — men bara om *Organisationen fortfarande standardiserar viktiga kontrakt och driftbeteenden*
**Faktaunderlag (enda tillåtna källan för tekniska påståenden):**
- Det som skulle göra idén värd något är inte ett snyggare dependency tree. Det är om teamet över flera år får mindre teknik att koordinera, färre lager att förstå och mindre påverkan när plattformen uppgraderas. Och det är förstås ett antagande som behöver prövas.

### 07 · En sak som kan ha ändrats — ca 450 ord
**Tes:** Mer kod kan ibland betyda mindre system
**Konfliktform:** Duell. Fri dialog kring tesen. Öppna i oenighet, stäng på inläggets eget förbehåll.
**Segmentet vinns av:** vera
**Ankare (sägs ordagrant):**
> Lite mer synlig kod skulle kunna ge ett betydligt mindre system.
**Faktaunderlag (enda tillåtna källan för tekniska påståenden):**
- AI gör det billigare att skapa mekaniska mappare, JDBC row-mappers, config records, adapters, tester och repetitiva decorators. Om det stämmer minskar värdet av abstraktioner vars viktigaste bidrag är att vi slipper skriva några rader.
- Samtidigt gör AI knappast protokoll, kryptografi, parsergränsfall, concurrency eller transaktionssemantik mindre farliga. Det går snabbt att generera en anslutningspool. Det betyder inte att teamet borde äga en.

### 08 · Så här långt har jag kommit — ca 450 ord
**Tes:** Kanske handlar minimalism mest om att välja ansvar
**Konfliktform:** Duell. Fri dialog kring tesen. Öppna i oenighet, stäng på inläggets eget förbehåll.
**Segmentet vinns av:** bosse
**Ankare (sägs ordagrant):**
> Fråga först om det behövs. Titta sedan i JDK. Skriv liten, konkret kod när semantiken är er egen. Och låt specialistbiblioteken ta det som tillhör ett svårt protokoll, en säkerhetsstandard eller en resursmanager.
**Faktaunderlag (enda tillåtna källan för tekniska påståenden):**
- Jag ser ingen poäng i att göra “noll Spring” till en trosbekännelse. Däremot tror jag att det finns något i att göra varje dependency medveten.
- En liten tjänst skulle kanske klara sig på JDK:s HTTP-server. En komplex publik tjänst kan gott stanna på WebMVC och Spring Security. En worker kan kanske vara nästan ren Java. Det gemensamma vore att affärslogiken får vara vanlig Java och att specialistbibliotek hålls vid tydliga gränser.
**Obs:** Det här är en idé jag gärna vill tänka vidare på tillsammans med andra – inget migrationsrecept. Jag är fullt beredd på att den håller sämre i verkligheten än på pappret. Frågan jag tycker är intressant är inte “kan vi ta bort Spring?”, utan “vilken teknik ger faktiskt lägst total ägarbörda för just den här tjänsten?” Har du erfarenheter som pekar åt ett annat håll vill jag gärna höra dem.

## Slutvinjett
Bosse och Vera säger unisont "det fungerar på min maskin". Det är osant för minst en av dem.
