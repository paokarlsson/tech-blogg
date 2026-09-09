# Beroendeframkallande · Avsnitt 1

## "Tänk om vi behövde färre ramverk?"

**Källa:** `src/sv/posts/2026-09-01-mindre-ramverk-mer-java.md`
**Längd:** ca 24 min · **Medverkande:** Bosse Boot, Vera Void, Förbehållsklockan 🔔
**Genererat underlag:** `podd/mindre-ramverk-mer-java.plan.json`

> Referensmanus. Visar ton, täthet och hur segmenten ska landa. Genererade utkast
> QA:as mot det här: spårbarhet, vinstbalans, replikbalans, ankarcitat.

---

### VINJETT

*Signaturmusik. Den låter som en ringsignal från 2011, för den är gjord av
ett bibliotek ingen längre underhåller.*

**BOSSE:** Välkomna till Beroendeframkallande, podden där vi läser ett blogginlägg
och båda två blir bekräftade i vår världsbild.

**VERA:** Det är statistiskt omöjligt.

**BOSSE:** Och ändå händer det varje vecka. Jag heter Bosse Boot.

**VERA:** Vera Void. Jag har inte kompilerat något med ett byggverktyg sedan i juli.

**BOSSE:** Hon har inte kompilerat något alls sedan i juli.

**VERA:** Det är två olika påståenden och bara ett av dem är sant.

**BOSSE:** Dagens inlägg heter "Tänk om vi behövde färre ramverk?" och undertiteln
är "En tanke om beroenden, Spring Boot och vad Java 25 redan ger oss".

**VERA:** Alltså ett manifest.

**BOSSE:** Alltså *inte* ett manifest, det står ordagrant "det här är ett resonemang,
inte en slutsats".

**VERA:** Det är precis vad ett manifest skulle säga för att smyga sig in.

---

### 01 · TANKEN — *duell · vinnare: Vera*
*Källa: inläggets sektion 01*

**BOSSE:** Så. Han börjar med att säga att Spring inte är problemet.

**VERA:** Han börjar med att säga att Spring inte är problemet, vilket är vad man
säger precis innan man förklarar att Spring är problemet.

**BOSSE:** Nej! Han menar det. Han skriver att för publika API:er, säkerhet,
avancerad routing, observability och stora integrationsytor är Spring antagligen
fortfarande det billigaste alternativet totalt sett. Läs det där högt för mig, Vera.

**VERA:** Nej.

**BOSSE:** Läs det.

**VERA:** …"antagligen fortfarande det billigaste alternativet totalt sett".

**BOSSE:** Tack. Det är min ringsignal nu.

**VERA:** Men sen kommer meningen som hela inlägget vilar på. Att Spring har blivit
*så självklart* att vi ibland når efter det även när problemet är mindre än lösningen.

**BOSSE:** Ge mig ett exempel på ett problem som är mindre än Spring Boot.

**VERA:** "Hämta JSON från en tjänst, räkna ihop två fält, skriv en rad till en databas."

**BOSSE:** Okej. Då vill jag ha en starter för HTTP-klienten, en starter för
serialiseringen, en för datalagret, en för hälsokontroller—

**VERA:** Tjänsten har alltså fem beroendefamiljer och en for-loop.

**BOSSE:** Den har *noll* for-loopar, det är hela vitsen.

**VERA:** Och i Java 25 finns redan HTTP-klient, JDBC, schemaläggning, records,
loggning, JFR, JMX och moderna samtidighetsverktyg. Plus virtuella trådar, som gör
vanlig, blockerande kod betydligt mer attraktiv för I/O än den var för några år sedan.

**BOSSE:** Du sa det där som om det var en dikt.

**VERA:** Det är en dikt. Den heter release notes och ingen läser den.

**BOSSE:** Jag läser den!

**VERA:** Du läser rubrikerna och sen söker du efter en starter för resten.

*Paus. Två sekunder.*

**BOSSE:** *(rakt, utan skämt)*
> Java har inte blivit ett nytt Spring. Men kanske har gränsen för vad som behöver
> ett ramverk flyttat sig lite?

*Två sekunder.*

**VERA:** …ja.

**BOSSE:** Bara "ja"?

**VERA:** Jag vann det här segmentet. Jag tänker inte förstöra det genom att prata.

---

### 02 · FÖRVALTNINGSYTAN — *isberget · vinnare: Bosse*
*Källa: inläggets sektion 02*

**VERA:** Sektion två. Isberget. Det här är mitt kapitel.

**BOSSE:** Det är ett *diagram*, Vera, du kan inte äga ett diagram.

**VERA:** När vi tittar på en `pom.xml` ser vi bara toppen. Under ytan ligger
transitiva bibliotek. Versionskopplingar. Autokonfiguration. Proxyer. Annotation
processing. Konventioner som *någon* behöver förstå den dagen något går fel.

**BOSSE:** Ja men det är ju bara en liten dependency—

*🎻 Stråkar. Långsamma. Havet är väldigt stilla i kväll.*

**VERA:** *(dödsruna, långsamt)* Versioner. Uppgraderingar, kompatibilitet och
koordinering. Säkerhet. CVE:er, parser- och nätverksyta, patcharbete. Semantik.
Dolda regler, proxybeteenden och lifecycle. Förändring. Hur mycket behöver förstås
nästa gång kraven flyttar sig?

**BOSSE:** Var det allt?

**VERA:** Det var toppen av det.

**BOSSE:** Bra. För nu ska jag vinna det här kapitlet med *hans egna ord*.

**VERA:** Det tror jag inte.

**BOSSE:** "Att räkna JAR-filer känns som ett trubbigt mått."

**VERA:** …

**BOSSE:** "En liten extern dependency kan vara mycket billig. Fyrahundra rader egen
OAuth-kod kan vara mycket dyr."

**VERA:** Fyrahundra rader är i överkant.

**BOSSE:** BINGO.

**VERA:** Det var inte bingo, jag sa ingenting—

**BOSSE:** Du sa "fyrahundra rader OAuth är i överkant", vilket betyder att du har
en siffra i huvudet, vilket betyder att du har *tänkt på det*.

**VERA:** Alla har tänkt på det.

**BOSSE:** Ingen frisk människa har tänkt på det. Och han skriver rakt ut: med
minimalism menar han inte minst kod eller noll bibliotek. Utan mindre onödig
semantik. Mindre teknik som teamet behöver bära över tid.

**VERA:** Det är faktiskt inte samma sak som det jag har sagt i fyra år.

**BOSSE:** Nej. Det är det inte.

🔔

**VERA:** Vad ringde den för?

**BOSSE:** Den ringde för dig.

**VERA:** Jag drog inte ens en slutsats!

**BOSSE:** Du drog fyra. Du bara sa dem inte högt.

---

### 03 · TRAPPAN — *frågesport · vinnare: Vera*
*Källa: inläggets sektion 03*

*Jingel. Fyra toner. Den fjärde är lite off, vilket är avsiktligt och kommer
irritera exakt rätt lyssnare.*

**BOSSE:** Trappan! Fyra steg. Vi läser ett behov, ni gissar hemma, vi gissar här,
och sen får vi veta hur fel vi hade.

**VERA:** Stegen är: ett — behövs det över huvud taget. Två — finns det i JDK:n.
Tre — räcker lite egen kod. Fyra — låt specialisten ta det.

**BOSSE:** Och ju längre åt höger vi går, desto mer specialiserad semantik låter vi
någon annan äga. Första behovet: **vi vill cacha resultatet av ett anrop som görs
en gång per dygn.**

**VERA:** Ett.

**BOSSE:** Fyra.

**VERA:** Du hörde inte ens klart frågan.

**BOSSE:** Jag hörde "cache". Det finns en abstraktion för det.

**VERA:** Det görs *en gång per dygn*. Det är steg ett. Behövs beteendet över huvud
taget? Nej. Och en cache som aldrig byggs har ingen implementation att förvalta.

**BOSSE:** …det är faktiskt hans exempel, ordagrant.

**VERA:** Jag vet. Nästa.

**BOSSE:** **Vi ska anropa ett internt API över HTTP och läsa svaret.**

**VERA:** Ett.

**BOSSE:** Nu är det inte ett, nu *behövs* det ju.

**VERA:** Förlåt. Två. JDK:s HttpClient.

**BOSSE:** Fyra.

**VERA:** På vilken grund?

**BOSSE:** Retry, timeouts, metrics, tracing, felhantering—

**VERA:** Timeouts finns i HttpClient. Retry är steg tre — en liten retry-loop är
ganska tydlig vanlig Java. Och tracing är steg fyra, men bara tracing.

**BOSSE:** Så svaret är två *och* tre *och* lite fyra.

**VERA:** Ja. Det är därför det är en ordning och inte ett quiz.

**BOSSE:** Det är ett quiz. Vi gjorde en jingel.

**VERA:** Sista. **Vi ska verifiera en OAuth-token.**

**BOSSE:** FYRA. FYRA. Fyra, fyra, fyra.

**VERA:** …fyra.

**BOSSE:** Säg det igen.

**VERA:** Fyra. Handlar det om JSON, OAuth, OIDC, anslutningspooler, brokerprotokoll
eller avancerad telemetry, så är ett moget bibliotek nästan alltid billigare.

**BOSSE:** Och hur känns det?

**VERA:** Som steg två, fast för mitt känsloliv.

---

### 04 · RITNINGEN — *arkitektur i ljud · vinnare: Bosse*
*Källa: inläggets sektion 04*

**VERA:** Nu kommer den intressanta idén. Den handlar inte om att ta bort Spring Boot.

**BOSSE:** Den handlar om att sluta låta Spring vara applikationens huvudsakliga
programmeringsmodell. Jag läste den meningen tre gånger.

**VERA:** Och?

**BOSSE:** Andra gången blev jag arg. Tredje gången ritade jag den.

**VERA:** Beskriv den för lyssnaren. Utan att peka. Du pekar just nu.

**BOSSE:** Fyra lager. Ytterst: omvärlden. HTTP, identitet, drift. Protokoll,
routing, säkerhet, standardiserad observability — komplext, och det förändras över tid.
Sen: **kanten**. Där bor Spring. WebMVC, Security, adapters, bootstrap. Ramverket
översätter omvärlden till applikationens egna typer.

**VERA:** Och innanför kanten: **kärnan**. Vanlig Java. Domän, use cases, records,
konstruktorer, invariants, små portar — utan en enda Spring-typ.

**BOSSE:** Och på andra sidan kärnan: **gränserna**. Små adapters. JDBC, JSON,
externa API:er, köer — inkapslade bakom tydliga interfaces.

**VERA:** Det här är ju bara hexagonal arkitektur med bättre PR.

**BOSSE:** Ja! Och vet du vad det betyder? Det betyder att jag får ha kvar Spring.

**VERA:** Det betyder att du får ha kvar Spring *i ett lager*.

**BOSSE:** I ett lager där det gör nytta, vilket är exakt vad jag har sagt hela tiden.

**VERA:** Du har aldrig sagt det. Du har sagt "lägg till en starter".

**BOSSE:** Jag har sagt "lägg till en starter" *vid kanten*.

**VERA:** Du har sagt det i en `@Entity`.

**BOSSE:** Det var en svår vecka och den ligger bakom mig.

**VERA:** Men poängen han gör är att om kärnan är fri från Spring blir nästa beslut
mindre dramatiskt. En komplex tjänst kan lugnt stanna på avskalat Boot. En liten
intern tjänst kan senare gå längre mot ren JDK. En batch eller worker behövde
kanske aldrig Spring från början.

**BOSSE:** Det är faktiskt smart. Det är inte ett val. Det är att skjuta upp valet
tills man vet något.

**VERA:** Han skriver också "men det är just en tanke — jag vet inte hur väl den
håller i era system".

**BOSSE:** Ska vi ringa i klockan på honom?

**VERA:** Nej. Han hade med sitt förbehåll. Han är den enda i det här rummet som har det.

---

### 05 · SNABBRUNDAN — *sex kort · delad seger*
*Källa: inläggets sektion 05*

*Snabb jingel. Klocka som tickar. Alldeles för stressig för innehållet.*

**BOSSE:** Sex saker, en i taget. Behåll, ta bort, eller utred. Kör.
**Lombok och mappare.**

**VERA:** Ta bort. Records och explicit kod gör att en del av den mekaniska hjälpen
känns mindre värdefull än den gjorde tidigare.

**BOSSE:** …jag har inget. Jag har faktiskt inget.

**VERA:** Skriv upp det.

**BOSSE:** **Utgående HTTP.**

**VERA:** JDK:s HttpClient räcker långt för vanlig service-to-service-kommunikation.

**BOSSE:** "Långt."

**VERA:** Långt.

**BOSSE:** Det är ett förbehåll utan klocka. **Spring DI.**

**VERA:** Utred. Konstruktorinjektion behöver ingen container.

**BOSSE:** Utred! Samtidigt kan en stor och dynamisk objektgraf mycket väl motivera Spring.

**VERA:** Vi är överens.

**BOSSE:** Det känns fruktansvärt.

**VERA:** **JPA och Hibernate.**

**BOSSE:** Utred. För rika objektgrafer är ORM antagligen fortfarande billigare.

**VERA:** För tydlig SQL och en begränsad modell kan JDBC vara enklare.

**BOSSE:** Och nu ska vi bråka i fyrtio minuter om vad "rik objektgraf" betyder—

🔔

**VERA:** Tack.

**BOSSE:** **JSON och säkerhet.**

**VERA:** Behåll. Generell JSON-parsning och OAuth/OIDC bär på svår semantik som
sällan bör bli egen infrastruktur.

**BOSSE:** Säg det en gång till, långsamt, jag spelar in det separat.

**VERA:** Nej.

**BOSSE:** **Connection pool.**

**VERA:** Behåll. JDBC finns i JDK, men en produktionsmässig pool gör det inte.

**BOSSE:** Och du skulle ju skriva en. I somras. På en fredag.

**VERA:** Jag skrev en.

**BOSSE:** Vad hände?

**VERA:** Den fungerade.

**BOSSE:** Vad hände på *måndagen*?

**VERA:** …den fungerade inte längre.

**BOSSE:** BINGO.

**VERA:** Han skriver att HikariCP känns som ett självklart kvarvarande beroende,
och jag tänker inte bråka om det.

**BOSSE:** Två till dig, två till mig, två oavgjorda. Det är den mest oroande siffra
vi någonsin har producerat.

---

### 06 · VILLKORSKLOCKAN — *fyra löften · vinnare: Bosse*
*Källa: inläggets sektion 06*

**VERA:** Sektion sex. Vad vi skulle vinna. Det finns en tabell.

**BOSSE:** Och tabellen har tre kolumner: "om vi minskar", "skulle vi kanske få",
och — det här är min favoritkolumn i hela svensk teknikjournalistik — **"men bara om"**.

**VERA:** Kör. Minskar vi externa dependency families får vi färre separata
versions- och uppgraderingsspår.

🔔

**VERA:** …men bara om vi inte ersätter dem med stora interna ramverk.

**BOSSE:** Vilket är exakt vad som händer. Varje gång. Ett team tar bort fyra
bibliotek och bygger `vår-plattform-core`, som ingen utanför teamet begriper, och
som har en enda underhållare, som slutar i mars.

**VERA:** Nästa. Minskar vi Spring-typer i domänen får vi mindre påverkan av
ramverksuppgraderingar och enklare tester — men bara om gränserna mellan kärna och
adapters är tydliga.

**BOSSE:** Du hann före klockan.

**VERA:** Jag lär mig.

**BOSSE:** Minskar vi runtime-magi får vi synligare kontrollflöde och enklare
felsökning—

🔔

**BOSSE:** —men bara om den explicita koden förblir liten och begriplig. Ja, ja.

**VERA:** Och det är det verkliga hålet, va. "Explicit" och "liten" är två olika
saker, och de flesta som byter bort magi mot explicit kod får explicit *och stor*.

**BOSSE:** Sista: minskar vi överdriven standardisering i kod får vi mindre lokal
infrastruktur — men bara om organisationen fortfarande standardiserar viktiga
kontrakt och driftbeteenden.

**VERA:** Så: mindre standardisering i koden, men inte mindre standardisering.

**BOSSE:** Precis. Och det, Vera, är varför jag vinner det här kapitlet, för alla
fyra raderna säger samma sak: **vinsten är villkorad, och villkoret är svårare än
själva bortplockandet.**

**VERA:** …det där var faktiskt bra.

**BOSSE:** Jag vet. Jag ska aldrig säga något bra igen. Det var för dyrt.

---

### 07 · DEN NYA GREJEN — *duell · vinnare: Vera*
*Källa: inläggets sektion 07*

**VERA:** Sektion sju är den som är ny. Den handlar om AI.

**BOSSE:** Här blir jag nervös.

**VERA:** Tesen: AI gör det billigare att skapa mekaniska mappare, JDBC row-mappers,
config records, adapters, tester och repetitiva decorators. Och om det stämmer,
minskar värdet av abstraktioner vars viktigaste bidrag är att vi slipper skriva några rader.

**BOSSE:** Så halva argumentet för mitt halva verktygsbälte var alltid "det är jobbigt att skriva".

**VERA:** Och det argumentet blev billigare i år.

**BOSSE:** Men.

**VERA:** Men. Och det här är den viktigaste meningen i hela inlägget, tycker jag:
AI gör knappast protokoll, kryptografi, parsergränsfall, concurrency eller
transaktionssemantik mindre *farliga*.

**BOSSE:** Det går snabbt att generera en anslutningspool.

**VERA:** Det betyder inte att teamet borde äga en.

**BOSSE:** *(paus)* Jag ska sätta upp den meningen på väggen.

**VERA:** Du ska generera en affisch med den meningen och sen ska någon annan
underhålla affischen.

**BOSSE:** Ja.

*Två sekunder.*

**VERA:** *(rakt, utan skämt)*
> Lite mer synlig kod skulle kunna ge ett betydligt mindre system.

*Två sekunder.*

**BOSSE:** Det är alltså inte "mindre kod = bättre".

**VERA:** Nej. Det är "mer kod, färre begrepp". Man byter bort dold semantik mot
synliga rader. Raderna kostar minutrar. Semantiken kostar år.

---

### 08 · RÄKNARNA — *duell · vinnare: Bosse*
*Källa: inläggets sektion 08*

**BOSSE:** Sista sektionen. Och innan vi läser den vill jag redovisa avsnittets
statistik. Jag har räknat rader kod som Vera har föreslagit att vi skriver själva.

**VERA:** Och jag har räknat JAR-filer som Bosse har föreslagit att vi hämtar.

**BOSSE:** Trehundraåttio rader.

**VERA:** Nitton JAR-filer.

**BOSSE:** Och vem vann?

**VERA:** …

**BOSSE:** Vera. Vem vann?

**VERA:** Ingen av oss mäter rätt sak.

**BOSSE:** Nej.

**VERA:** Vi har räknat i två olika enheter i tjugo minuter och ingen av dem är
förvaltningskostnad.

**BOSSE:** Nej. Och det är därför han skriver att det inte finns någon poäng i att
göra "noll Spring" till en trosbekännelse. Men att det finns något i att göra varje
dependency **medveten**.

**VERA:** En liten tjänst skulle kanske klara sig på JDK:s HTTP-server. En komplex
publik tjänst kan gott stanna på WebMVC och Spring Security. En worker kan kanske
vara nästan ren Java.

**BOSSE:** Och det gemensamma vore att affärslogiken får vara vanlig Java, och att
specialistbiblioteken hålls vid tydliga gränser.

*Två sekunder.*

**VERA:** *(rakt, utan skämt)*
> Fråga först om det behövs. Titta sedan i JDK. Skriv liten, konkret kod när
> semantiken är er egen. Och låt specialistbiblioteken ta det som tillhör ett svårt
> protokoll, en säkerhetsstandard eller en resursmanager.

*Två sekunder.*

**BOSSE:** Det är fyra meningar. Vi gjorde tjugofyra minuter av dem.

**VERA:** Vi gjorde tjugofyra minuter *mot* dem. Det är skillnad.

**BOSSE:** Och han avslutar med att det inte är ett migrationsrecept. Att han är
fullt beredd på att idén håller sämre i verkligheten än på pappret. Och att frågan
inte är "kan vi ta bort Spring" utan "vilken teknik ger faktiskt lägst total
ägarbörda för just den här tjänsten".

**VERA:** Det finns inget att bråka om där.

**BOSSE:** Nej.

**VERA:** Vilket är obehagligt.

**BOSSE:** Djupt obehagligt. Har du något du vill ta tillbaka?

**VERA:** Jag skulle inte skriva en connection pool på en fredag.

**BOSSE:** Tack.

**VERA:** Jag skulle skriva den på en tisdag, med hela veckan framför mig.

🔔

**BOSSE:** Tack för att ni lyssnade på Beroendeframkallande.

**BÅDA:** *(unisont)* Det fungerar på min maskin!

**VERA:** Det gör det inte.

**BOSSE:** Nej.

*Slutvinjett. Bryts av mitt i en ton — biblioteket som spelar upp den har en
breaking change i patchversionen.*

---

## QA-protokoll för det här avsnittet

| Kontroll | Krav | Utfall |
| --- | --- | --- |
| Spårbarhet | Varje tekniskt påstående härlett ur inlägget | ✅ segmentrubrikerna anger källsektion |
| Vinstbalans | Ingen vinner två i rad | ✅ V–B–V–B–delad–B–V–B |
| Totalbalans | Jämnt | ✅ 3 Vera, 4 Bosse, 1 delad |
| Ankarcitat | Sägs ordagrant, utan skämt | ✅ 01, 07, 08 |
| Förbehållsklockan | Ringer på varje oförsedd slutsats | ✅ 5 gånger |
| Java-fakta | Korrekt även i dumma repliker | ✅ HttpClient, virtuella trådar, records, HikariCP |
| Längd | 22–26 min vid 150 ord/min | ✅ ca 24 min |
