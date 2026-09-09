# Beroendeframkallande · Avsnitt 1

## "Tänk om vi behövde färre ramverk?"

**Källa:** `src/sv/posts/2026-09-01-mindre-ramverk-mer-java.md`
**Längd:** ca 13 min · **Medverkande:** Bosse Boot, Vera Void

> Referensmanus, tredje versionen. Skrivet som samtal, inte som föredrag:
> de förstår saker i fel ordning, bygger liknelser som inte håller, lagar
> dem eller släpper dem, och är oense om minst en sak när avsnittet tar slut.
> Fakta kommer fortfarande bara ur inlägget. Författaren refereras könsneutralt
> ("det står", "texten säger") — vi vet inte vem som skrivit det.

---

### INTRO

*Signaturmusik, kort och odramatisk.*

**BOSSE:** Beroendeframkallande. Bosse här.

**VERA:** Och Vera.

**BOSSE:** Vi läser ett blogginlägg i veckan och pratar om det tills… ja, tills vi
inte har mer att säga.

**VERA:** Vilket inte är samma sak som tills vi förstått det.

**BOSSE:** *(skrattar)* Nej. Nej, det är det verkligen inte.

**BOSSE:** Den här veckan: "Tänk om vi behövde färre ramverk?" Spring Boot, Java 25,
och… du hade en sammanfattning innan vi började. Ta den.

**VERA:** Min sammanfattning var att det är ett inlägg som vägrar bestämma sig.

**BOSSE:** Det låter elakt.

**VERA:** Det var inte elakt menat. Det står nästan rakt ut — "det här är ett
resonemang, inte en slutsats". Det är ovanligt ärligt.

**BOSSE:** Okej. För jag läste det först som ett Spring-hatinlägg och blev irriterad
i ungefär två stycken, och sen visade det sig att det inte alls var det.

**VERA:** Nej, snarare tvärtom. Det står uttryckligen att för publika API:er,
säkerhet, stora integrationsytor — där är Spring antagligen fortfarande det
billigaste alternativet totalt sett.

**BOSSE:** Vilket i princip är hela mitt jobb, så det var ju skönt.

---

### VAD ETT BEROENDE KOSTAR

**VERA:** Den poäng jag fastnade på först är att räkna JAR-filer är ett trubbigt mått.

**BOSSE:** Mm.

**VERA:** En liten dependency kan vara jättebillig. Fyrahundra rader egen OAuth-kod
kan vara ohyggligt dyr. Samma rad i pom-filen. Helt olika kostnad.

**BOSSE:** Ja, det är ju… vänta. Det är som nycklar.

**VERA:** Nycklar.

**BOSSE:** Du har en nyckelknippa. Och du kan räkna nycklarna på den—

**VERA:** Mm.

**BOSSE:** —men antalet säger ingenting om vilka dörrar som är svåra att öppna.

**VERA:** *(tvekande)* Nej… men den säger inte riktigt det du vill heller. En nyckel
är en nyckel. De väger lika mycket allihop.

**BOSSE:** Ja men det är ju det som är—

**VERA:** Nej, jag menar: din bild säger att antalet är ointressant. Texten säger att
antalet är ointressant *och* att några av dem är fruktansvärt tunga att bära. Din
nyckelknippa har ingen tyngd i sig.

**BOSSE:** *(paus)* …okej. Så en av nycklarna går till ett rum där det står saker
ingen på företaget förstår.

**VERA:** *(skrattar)* Det är bättre.

**BOSSE:** Det är bättre! Den är fortfarande dålig, men den är bättre.

**VERA:** Och det är ungefär det texten säger, fast utan nycklar. Det handlar inte om
hur många beroenden du har utan hur mycket okänd semantik du bär på. Versions-
kopplingar. Autokonfiguration. Sånt som någon måste förstå den dagen det smäller.

**BOSSE:** Och det är därför minimalism här inte betyder noll bibliotek.

**VERA:** Nej, det står svart på vitt. Inte minst kod. Inte noll bibliotek. Mindre
onödig semantik.

**BOSSE:** Vilket är… hm. Säg det där en gång till.

**VERA:** Mindre teknik som teamet behöver bära över tid.

**BOSSE:** Så man kan alltså ha *mer* kod och samtidigt ett *mindre* system.

**VERA:** Ja.

**BOSSE:** Det tar emot att säga.

**VERA:** Jag vet.

**BOSSE:** Nej men det tar fysiskt emot.

**VERA:** Fast du säger det som om det vore gratis. Det gäller bara om den explicita
koden förblir liten och begriplig — det står längre ner i inlägget, i en egen kolumn
till och med.

**BOSSE:** *(surt)* Jag hade kommit dit.

**VERA:** Det hade du inte.

**BOSSE:** Nej.

---

### ORDNINGEN

**VERA:** Sen kommer ett förslag på hur man skulle kunna fråga sig fram. Fyra steg.

**BOSSE:** Den här gillade jag faktiskt. Behövs det? Finns det i JDK:n? Räcker lite
egen kod? Och annars: låt specialisten ta det.

**VERA:** Precis.

**BOSSE:** Och det är alltså en regel man kan följa.

**VERA:** Nej.

**BOSSE:** Nej?

**VERA:** Det står uttryckligen att ordningen inte är någon sanning. Det är ett sätt
att göra valet medvetet. Inte ett flödesschema.

**BOSSE:** Men om jag går igenom stegen får jag ju ett svar.

**VERA:** Får du?

**BOSSE:** Ja? Ta ett utgående HTTP-anrop. Steg ett, behövs det: ja. Steg två, finns
det i JDK:n: ja, HttpClient. Klart. Svaret är två.

**VERA:** Vill du ha retry?

**BOSSE:** …ja.

**VERA:** Steg tre. Liten egen loop.

**BOSSE:** Okej. Två och tre.

**VERA:** Vill du ha tracing som hänger ihop över alla era tjänster?

**BOSSE:** Ja, självklart.

**VERA:** Steg fyra.

**BOSSE:** *(paus)* Så det är två, tre och fyra.

**VERA:** Samma behov. Tre olika svar, beroende på var du drar gränsen för vad
behovet faktiskt är.

**BOSSE:** Men då gör ju ordningen ingenting.

**VERA:** Jo. Den gör en enda sak. Den tvingar dig att börja på ett.

**BOSSE:** …

**VERA:** Exemplet i texten är en cache för något som körs en gång per dygn.

**BOSSE:** Åh. Nej. Den ska ju inte finnas alls.

**VERA:** Och en cache som aldrig byggs har ingen implementation att förvalta.

**BOSSE:** Nej, men det där är billigt sagt. Det är alltid lätt att säga "bygg
mindre".

**VERA:** Är det? Hur ofta gör vi det?

**BOSSE:** *(kort paus)* Aldrig.

**VERA:** Nej.

**BOSSE:** Vi börjar på fyra.

**VERA:** Du börjar på fyra.

**BOSSE:** *(skrattar)* Jag börjar på fyra.

---

### VAR SPRING SKA BO

**VERA:** Den idé jag tycker är intressantast handlar inte om att ta bort Spring alls.
Den handlar om var i systemet det får bo.

**BOSSE:** Kanten.

**VERA:** Kanten. HTTP, säkerhet, bootstrap, adapters — där gör Spring nytta. Och
innanför det: kärnan. Vanlig Java. Domän, use cases, records. Inte en enda Spring-typ.

**BOSSE:** Mm.

**VERA:** Jag tänkte att det är lite som en restaurang. Hovmästaren tar emot i
entrén, håller ordning på bokningar, allt det formella. Men i köket lagar man mat.
Där gäller inga dukningsregler.

**BOSSE:** Nä.

**VERA:** Nä?

**BOSSE:** Nej, jag köper den inte.

**VERA:** Varför inte?

**BOSSE:** För i din bild är hovmästaren dekoration. Hen gör inget svårt. Och det är
precis vad Spring vid kanten *inte* är. Det är där det svåraste i hela systemet
sitter — OIDC, routing, säkerhetsfilter. Sånt du absolut inte vill ha i köket.

**VERA:** *(paus)* Det är… ja. Okej, det är sant.

**BOSSE:** Om något är kärnan hovmästaren. Det är den som ska göra en enda tråkig sak
väldigt bra.

**VERA:** Nu blev det sämre.

**BOSSE:** *(skrattar)* Ja, nu vet jag inte vad jag har gjort.

**VERA:** Vi släpper restaurangen.

**BOSSE:** Vi släpper restaurangen. Men själva poängen står ju kvar, och den är bra:
om kärnan är fri från Spring blir *nästa* beslut billigare.

**VERA:** Utveckla.

**BOSSE:** En stor publik tjänst kan ligga kvar på Boot i evighet, ingen bryr sig. Men
en liten intern tjänst kan glida mot ren JDK längre fram utan att man river upp
affärslogiken. Man behöver inte välja idag.

**VERA:** Det är att skjuta upp beslutet.

**BOSSE:** Det är att skjuta upp beslutet tills man vet mer. Det är inte samma sak som
att smita från det.

**VERA:** *(motvilligt)* Nej. Nej, det är det inte.

**BOSSE:** *(nöjt)* Skriv upp det.

---

### NÅGRA EXEMPEL

**VERA:** Det finns en lista med konkreta saker längre ner. Vi tar inte alla.

**BOSSE:** Nej, för då sitter vi här till i morgon.

**VERA:** Lombok, till exempel. Det står att med records och lite explicit kod känns
den mekaniska hjälpen mindre värdefull än den gjorde förr.

**BOSSE:** Den håller jag med om. Fast av fel skäl.

**VERA:** Vilket är?

**BOSSE:** Jag har aldrig gillat att en annotation skriver kod jag inte kan läsa i
filen framför mig.

**VERA:** Det är faktiskt rätt skäl.

**BOSSE:** Är det?

**VERA:** Det är exakt textens skäl. Dold semantik.

**BOSSE:** Åh. Kul.

**VERA:** Sen connection pooling. JDBC finns i JDK:n. En produktionsmässig pool gör
det inte.

**BOSSE:** Nej, och den raden tycker jag är den lättaste i hela inlägget.

**VERA:** *(torrt)* Det är ungefär som elektriker och säkringsskåp. De flesta av oss
kan dra en kabel. Man tar ändå in någon för skåpet — inte för att man inte klarar en
skruvmejsel, utan för att ett fel där kostar på ett sätt som inte syns förrän det
redan brunnit.

**BOSSE:** Där höll bilden hela vägen.

**VERA:** Den höll.

**BOSSE:** Bättre än nycklarna.

**VERA:** Avsevärt bättre än nycklarna.

**BOSSE:** Okej, men då tar jag en där jag tycker texten är för mjuk. Spring DI.

**VERA:** Det står att konstruktorinjektion inte behöver någon container.

**BOSSE:** Ja. Och det är sant. Och det är också helt irrelevant i ett system med
hundrafemtio bönor och en objektgraf som ändrar sig varje sprint. Det står ju det
också — att en stor och dynamisk objektgraf mycket väl kan motivera Spring — men det
står som ett förbehåll. Jag tycker det borde vara huvudspåret.

**VERA:** Jag tycker det är rätt viktat.

**BOSSE:** Det tycker inte jag.

**VERA:** Nej, det märks.

**BOSSE:** *(surt)* Vi behöver inte lösa det här.

**VERA:** Nej.

---

### DEN NYA BITEN

**BOSSE:** En sista sak. Det finns ett stycke om AI som känns nyast i hela inlägget.

**VERA:** Mm. Jag är inte såld på det.

**BOSSE:** Vänta, hör tesen först. AI gör det billigare att skriva mekanisk kod.
Mappare, row-mappers, config-klasser, tråkiga adaptrar. Och om det stämmer sjunker
värdet på bibliotek vars enda bidrag är att man slipper skriva de raderna.

**VERA:** Jo, jag hör vad det säger.

**BOSSE:** Och?

**VERA:** Och jag tror "billigare att skriva" är fel mätsticka. Det var aldrig
skrivandet som kostade. Det var att läsa det där om ett år.

**BOSSE:** Jo, men det står ju faktiskt det också—

**VERA:** Var?

**BOSSE:** Direkt efter. Att AI knappast gör protokoll, kryptografi, gränsfall i
parsers, concurrency eller transaktionssemantik mindre farliga. Det går fort att
generera en connection pool—

**VERA:** —det betyder inte att teamet borde äga en.

**BOSSE:** Precis den meningen.

**VERA:** *(paus)* Okej. Den var bra.

**BOSSE:** Det är som en väldigt snabb skräddare. Hen syr om plagget på halva tiden.
Men tyget blir inte starkare av att sömmen gick fort.

**VERA:** *(skrattar)* Nu var det din tur att ha en som funkar.

**BOSSE:** Jag har haft en hel karriär av dåliga liknelser och nu kommer den. Live.
Inspelat.

**VERA:** Men jag är fortfarande inte hela vägen med. Det förutsätter att man vet
vilken kod som är mekanisk. Och gränsen mellan mekanisk och farlig är sällan
uppenbar när man sitter mitt i den.

**BOSSE:** Nej. Nej, det är den inte.

**VERA:** Så jag skulle säga: intressant tes, ovanligt osäker.

**BOSSE:** Vilket texten säger om sig själv också.

**VERA:** *(motvilligt)* Ja.

*Två sekunder.*

**BOSSE:** *(rakt, utan skämt)*
> Lite mer synlig kod skulle kunna ge ett betydligt mindre system.

*Två sekunder.*

**VERA:** Och det är alltså inte "mindre kod är bättre".

**BOSSE:** Nej. Fler rader, färre begrepp.

**VERA:** Rader kostar minuter. Begrepp kostar år.

**BOSSE:** Var det ditt eller textens?

**VERA:** Mitt.

**BOSSE:** Det var bra.

**VERA:** Jag vet.

---

### AVSLUTNING

**BOSSE:** Var landar du?

**VERA:** Jag landar i att det är ett resonemang jag känner igen men aldrig sett
skrivet så försiktigt. Det finns inget "noll Spring" här. Det står till och med rakt
ut att det inte är någon trosbekännelse värd att ha.

**BOSSE:** Utan?

**VERA:** Att göra varje beroende medvetet i stället för automatiskt.

**BOSSE:** Och jag landar väl i att jag är mindre hotad av det än jag var efter första
stycket. En liten tjänst klarar sig kanske på JDK:s egen HTTP-server. En stor publik
tjänst har alla skäl i världen att ligga kvar på WebMVC och Security. En worker kan
vara nästan ren Java rakt igenom.

**VERA:** Och det gemensamma är att affärslogiken får vara vanlig Java, och att
specialistbiblioteken hålls vid tydliga gränser.

*Två sekunder.*

**VERA:** *(rakt, utan skämt)*
> Fråga först om det behövs. Titta sedan i JDK. Skriv liten, konkret kod när
> semantiken är er egen. Och låt specialistbiblioteken ta det som tillhör ett svårt
> protokoll, en säkerhetsstandard eller en resursmanager.

*Två sekunder.*

**BOSSE:** Det är fyra meningar.

**VERA:** Det är fyra meningar.

**BOSSE:** Vi har hållit på i en halvtimme.

**VERA:** *(skrattar)* Ja.

**BOSSE:** Är jag övertygad?

**VERA:** Är du?

**BOSSE:** Om Spring DI? Nej. Fortfarande nej.

**VERA:** Jag vet.

**BOSSE:** Om resten… jag ska titta på en av våra småtjänster i morgon och se vad som
faktiskt används av det vi drog in. Det är väl något.

**VERA:** Det är mer än de flesta gör efter ett blogginlägg.

**BOSSE:** Tack för att ni lyssnade på Beroendeframkallande.

**VERA:** Hej.

*Slutvinjett, kort.*

---

## QA-anteckningar

| Kontroll | Utfall |
| --- | --- |
| Spårbarhet | Sakpåståenden går tillbaka till inläggets sektioner 01, 02, 03, 04, 05, 07, 08 |
| Ankarcitat | Sägs ordagrant, oförändrade från inlägget |
| Författarreferens | Könsneutralt genomgående — "det står", "texten säger". Aldrig "han/hon skriver" |
| Liknelser | Nyckelknippan misslyckas och lagas halvvägs · restaurangen förkastas helt · elektrikern håller · skräddaren håller |
| Oenighet | Spring DI lämnas olöst. Vera köper aldrig AI-tesen fullt ut |
| Skratt | 5 st, samtliga ur situationen — inga punchlines |
| Längd | ca 13 min vid 150 ord/min |
