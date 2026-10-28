---
layout: post.njk
translationKey: vad-kostar-noll-beroenden
title: "Hugg ner beroendeträdet"
subtitle: "Noll beroenden lät som en dålig idé så länge kod var dyr. Nu är den inte det längre."
eyebrow: "Java 25 · noll beroenden · AI · en hyllning till en dålig idé"
dek: "Så länge jag har hållit på med kod har jag hört samma råd: skriv aldrig din egen parser, ditt eget ramverk eller din egen säkerhet. Det är ett klokt råd, och jag har följt det. Men jag har börjat undra om det håller på att gå ut. Så jag har provat att göra precis det man inte ska – och det har varit väldigt roligt."
description: "En hyllning till idén om mjukvara helt utan beroenden: varför de gamla sanningarna om att aldrig bygga själv kanske inte gäller längre när kod blir billig att skriva."
date: 2026-10-28
image: "/assets/images/noll-beroenden-hero.sv.svg"
imageAlt: "Ett virrvarr av sammankopplade beroenden till vänster, en streckad snittlinje, och till höger en enda app som står direkt på JDK 25."
chips:
  - "Hugg ner trädet"
  - "Bygg det själv"
  - "Mjukvara som åldras väl"
  - "Heliga kor"
---
  <p class="lead">Vi har lärt oss att det är dyrt att skriva kod och billigt att lägga till ett beroende. Hela vår bransch vilar på den kalkylen, och den har varit sann så länge att vi slutat se den som en kalkyl. Den har blivit en sanning. Men tänk om den inte är det längre? <strong>Tänk om det nu är billigare att äga sin kod än att låna den?</strong></p>

  <section class="section">
    <div class="copy">
      <p class="eyebrow">01 · Tanken</p>
      <h2>Branschens heligaste regel har gått ut</h2>
      <p>”Uppfinn inte hjulet igen.” ”Skriv aldrig din egen kryptografi.” ”Använd ett beprövat ramverk.” Det är råd jag har lärt mig av andra, och jag har tagit dem till mig.</p>
      <p>Men titta på varför de var sanna. Det var aldrig för att egen kod är fel i sig. Det var för att den var dyr. Det tog veckor att skriva en HTTP-parser, månader att få den stabil och år att hinna lära sig alla dess gränsfall. Ett beroende fick man på en rad.</p>
      <p>Nu skriver AI den där parsern på en eftermiddag. Inte perfekt, men tillräckligt bra för att börja pröva den, vässa den och lära sig av den. När ena sidan av kalkylen rasar så kraftigt kan inte svaret bli detsamma som förut.</p>
      <div class="quote">”Uppfinn inte hjulet igen” var ett råd om kostnad. Inte en naturlag.</div>
    </div>
  </section>

  <section class="section">
    <p class="eyebrow">02 · Experimentet</p>
    <h2>Så jag bröt mot varenda regel</h2>
    <p class="copy">I mitt förra inlägg om ramverk skrev jag att JSON och säkerhet var saker jag skulle låta specialistbiblioteken ta hand om. Sedan dess har jag byggt båda själv.</p>
    <p class="copy"><a href="https://github.com/paokarlsson/spola">Spola</a> är ett webbramverk för Java 25 som gör det ett webb-API behöver från Spring Boot och Lombok – HTTP-server, routing, JSON, validering, konfiguration, sessioner och inloggning – utan annoteringsmagi och utan ett enda beroende utanför JDK:n. <a href="https://github.com/paokarlsson/sola">Sola</a> ska bli samma sak för webbläsaren: signals, mallar och routing direkt på webbplattformen, utan beroenden och utan byggsteg. Det som körs i webbläsaren är exakt det man skrev.</p>
    <p class="copy">Koden skrivs mest av AI. Och båda ramverken växer bara när en riktig app behöver något, så de blir aldrig större än vad någon faktiskt använder.</p>
    <div class="grid-2" style="margin-top:28px">
      <figure class="figure"><img src="/assets/images/noll-beroenden-spring.sv.svg" alt="Beroendeträdet för spring-boot-starter-web: ett trettiotal artefakter från Spring, Jackson, Tomcat, loggning och annat, i fyra nivåer."><figcaption>Det här får du med <code>spring-boot-starter-web</code>, ungefär så som Maven visar det för Spring Boot 3. Varje rad är en version att följa.</figcaption></figure>
      <figure class="figure"><img src="/assets/images/noll-beroenden-spola.sv.svg" alt="Beroendeträdet för spola.web: fyra moduler som alla står direkt på JDK 25, och sedan ingenting mer."><figcaption>Det här får du med <code>spola.web</code>. Fyra moduler, och under dem bara JDK:n.</figcaption></figure>
    </div>
    <div class="rule">Hela stacken, från TCP-socketen till knappen i webbläsaren. <em>Inget</em> beroendeträd.</div>
  </section>

  <section class="section">
    <p class="eyebrow">03 · Vad man vinner</p>
    <h2>Mjukvara som vägrar ruttna</h2>
    <div class="copy">
      <p>Den som har förvaltat ett Spring-system vet var tiden faktiskt går. Inte till affärslogiken, utan till allt runt omkring: bytet från <code>javax</code> till <code>jakarta</code>, Log4Shell en julvecka, beroendeuppdateringar varje sprint och den där gången då en minor-version av ett bibliotek tre nivåer ner ändrade beteende utan att någon märkte det.</p>
      <p>Ett system som bara står på JDK:n och webbläsarens standarder har inget av det. Java är löjligt bakåtkompatibelt. Webben har som princip att aldrig bryta en befintlig sida. Bygger man bara på dem kan koden man skriver i dag fungera om tjugo år.</p>
      <p>Och det bästa: man kan läsa allt. Ingen kan läsa hela Spring. Men hela HTTP-servern i Spola går att läsa på några kvällar. När något går fel finns det ingen svart låda att skylla på, och inget som händer bakom ryggen.</p>
    </div>
    <div class="metrics">
      <div class="metric"><strong>Livslängd</strong><span>Inga tvingade migreringar, någonsin.</span></div>
      <div class="metric"><strong>Läsbarhet</strong><span>Varje rad som påverkar ett beteende finns i ditt eget repo.</span></div>
      <div class="metric"><strong>Ägarskap</strong><span>Inga leverantörer, inga licensfrågor, inga överraskningar.</span></div>
      <div class="metric"><strong>Lugn</strong><span>Inga CVE-larm för bibliotek du aldrig visste att du hade.</span></div>
    </div>
  </section>

  <section class="section">
    <p class="eyebrow">04 · Gamla sanningar</p>
    <h2>Sex heliga kor att slakta</h2>
    <p class="copy">Här är några av de saker jag har förstått att man aldrig ska röra. Jag tror att alla är värda att ifrågasätta nu.</p>
    <div class="cards">
      <div class="card"><span class="tag remove">Gammal sanning</span><h3>”Skriv aldrig din egen HTTP-parser”</h3><p>Request smuggling uppstår när två parsrar tolkar samma tvetydighet olika. En parser som vägrar tolka – som svarar 400 på allt tvetydigt – stänger hela den dörren. Strikt slår smart.</p></div>
      <div class="card"><span class="tag remove">Gammal sanning</span><h3>”Skriv aldrig din egen JSON-parser”</h3><p>Många av de värsta sårbarheterna i JSON-bibliotek kommer från polymorf deserialisering, alltså reflektionsmagi. Explicit mappning till records har inte den sortens fel. Det enklaste är det säkraste.</p></div>
      <div class="card"><span class="tag remove">Gammal sanning</span><h3>”Du behöver ett byggsteg”</h3><p>ES-moduler, import maps och dynamisk <code>import()</code> finns i alla webbläsare. Ingen bundler, ingen transpilering, inget <code>node_modules</code> med tusen mappar.</p></div>
      <div class="card"><span class="tag remove">Gammal sanning</span><h3>”Du behöver en DI-container”</h3><p>Konstruktorer finns. Vanlig Java-kod som kopplar ihop objekten går att följa med ”Go to definition”, och ett saknat beroende blir ett fel vid start i stället för en överraskning i produktion.</p></div>
      <div class="card"><span class="tag remove">Gammal sanning</span><h3>”Databasen kräver ett ORM”</h3><p><code>java.sql</code> har funnits i JDK:n i över tjugo år. Tydlig SQL och en record per rad räcker längre än vi brukar tro.</p></div>
      <div class="card"><span class="tag remove">Gammal sanning</span><h3>”Rör aldrig säkerheten”</h3><p>JDK:n har redan de kryptografiska primitiverna. Lösenordshashning som byggs ovanpå dem och testas mot officiella testvektorer är inte magi – det är noggrannhet.</p></div>
    </div>
  </section>

  <section class="section callout big">
    <p class="eyebrow">05 · Ett förslag på ordning</p>
    <h2>Vänd på hela frågan</h2>
    <p class="copy">I det första inlägget föreslog jag en ordning som slutade med ”låt specialisten ta det”. Nu vill jag pröva att vända på den. I stället för att fråga när vi får bygga själva frågar vi när vi verkligen måste låna.</p>
    <div class="flow">
      <div class="step"><b>1. Finns det i plattformen?</b><span>JDK:n och webbläsaren kan mycket mer än vi brukar tro. Börja alltid där.</span><span class="arrow">→</span></div>
      <div class="step"><b>2. Kan vi skriva det strikt?</b><span>Om beteendet går att beskriva tydligt och allt annat kan avvisas, så går det att skriva – och AI skriver det snabbt.</span><span class="arrow">→</span></div>
      <div class="step"><b>3. Kan vi pröva det mot de bästa?</b><span>Kör samma indata genom den egna koden och genom Jackson eller Tomcat. De mogna biblioteken blir facit i stället för fundament.</span><span class="arrow">→</span></div>
      <div class="step"><b>4. Först då: låna</b><span>Om inget av det går, ta in ett beroende. Men gör det som ett undantag, inte som en reflex.</span></div>
    </div>
  </section>

  <section class="section">
    <p class="eyebrow">06 · Vad vi skulle vinna</p>
    <h2>Ta tillbaka makten över ditt system</h2>
    <p class="copy">Det här är inte en fråga om ett snyggare beroendeträd. Det är en fråga om vem som bestämmer över ens system: man själv, eller den som underhåller bibliotek nummer 47 i lockfilen.</p>
    <div class="table-wrap"><table>
      <thead><tr><th>Om vi äger det själva…</th><th>Så får vi…</th><th>Och slipper…</th></tr></thead>
      <tbody>
        <tr><td>HTTP-servern</td><td>En strikt parser vi kan läsa från början till slut</td><td>Nödpatchar för kod vi aldrig sett</td></tr>
        <tr><td>JSON-hanteringen</td><td>Synlig mappning till våra egna typer</td><td>Hela klassen av deserialiseringsbuggar</td></tr>
        <tr><td>Säkerheten</td><td>Full insyn i hur inloggning och sessioner fungerar</td><td>Konfigurationsmagi som ingen i teamet förstår</td></tr>
        <tr><td>Frontenden</td><td>Kod som körs exakt som den skrevs</td><td>Byggkedjor, bundlers och ramverksmigreringar</td></tr>
        <tr><td>Hela stacken</td><td>En mjukvaruförteckning med en rad: JDK 25</td><td>Leverantörsberoende och licensfrågor</td></tr>
      </tbody>
    </table></div>
  </section>

  <section class="section callout big">
    <p class="eyebrow">07 · Drömmen</p>
    <h2>Ett system som överlever sina utvecklare</h2>
    <p>Tänk dig ett bokningssystem för en kommun. Det byggs en gång, ordentligt, och sedan får det bara leva. Ingen tvingad uppgradering vart tredje år. Ingen konsult som måste in för att lyfta ramverket. Koden ligger i kommunens eget repo, och den som vill förstå den kan läsa den, hela vägen ner.</p>
    <p>Det är inte så offentliga system brukar fungera i dag. Men det är inte för att det är omöjligt. Det är för att det har varit för dyrt att skriva allt själv. Och det är precis den kostnaden som håller på att försvinna.</p>
    <div class="rule">Det bästa beroendet är det som <em>aldrig</em> behöver uppdateras.</div>
  </section>

  <section class="section">
    <p class="eyebrow">08 · Så här långt har jag kommit</p>
    <h2>Sluta be om ursäkt för att du bygger själv</h2>
    <p class="copy">Länge har ”jag byggde det själv” låtit som ett erkännande. Något man säger lite tyst, med en förklaring efteråt. Jag tror inte att det behöver vara så längre.</p>
    <p class="copy">När koden blir billig blir det plötsligt möjligt för en enda person att äga hela sin stack, från HTTP-parsningen till signals i webbläsaren. Det är inte ett steg tillbaka till hur vi gjorde innan open source. Det är något nytt: lika fritt som att skriva allt själv, nästan lika billigt som att låna.</p>
    <div class="quote">Vi slutade bygga själva för att det var dyrt. Nu är det inte dyrt längre. Så varför slutade vi?</div>
  </section>

  <section class="section">
    <p class="eyebrow">09 · En liten brasklapp</p>
    <h2>Okej, okej. Det finns problem.</h2>
    <p class="copy">Jackson, Tomcat och Spring Security har angripits av hela världen i femton år, och det har inte min kod. När samma verktyg skriver både koden och testerna betyder ett grönt bygge bara att koden gör vad testerna säger. Kryptografi som JWT är fortfarande ett område där jag går varsamt fram. Och Spola är version 0.x, där säkerhetsdelarna ännu inte har granskats av en människa – använd det inte för att skydda något på riktigt. Allt det här går att lösa med extern testning, jämförelser mot referensbiblioteken och en mänsklig granskning. Men det behöver göras.</p>
    <div class="note"><strong>Det här är en hyllning, inte ett recept.</strong> Jag vet att den är lite naiv, och det är meningen. Om du tycker att jag har fel vill jag gärna höra varför – men berätta gärna också vilken gammal sanning du själv skulle vilja pröva.</div>
  </section>
