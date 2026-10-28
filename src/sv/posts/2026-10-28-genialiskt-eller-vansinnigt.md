---
layout: post.njk
translationKey: genialiskt-eller-vansinnigt
title: "Genialiskt eller vansinnigt?"
subtitle: "Spola, Sola och frågan om vad AI-byggd kod utan beroenden faktiskt kostar"
eyebrow: "Java 25 · AI-agenter · noll beroenden · en granskning från båda håll"
dek: "Jag har två projekt som bygger på samma envisa idé: en fullstack utan ett enda beroende, där koden skrivs av AI-agenter under hårda regler. Den här gången försöker jag granska dem från båda håll – först så hårt jag kan, sedan så välvilligt jag kan – och se var det landar."
description: "En kritik och ett försvar av Spola och Sola – två ramverk utan beroenden där koden skrivs av AI-agenter – och slutsatsen att verifieringen är det som avgör."
date: 2026-10-28
chips:
  - "Noll beroenden?"
  - "AI som skriver koden"
  - "Kritiker som inte håller med"
  - "Verifiering före användning"
---
  <p class="lead">I förra inlägget om ramverk resonerade jag kring hur mycket av Spring vi egentligen behöver. Sedan dess har jag tagit idén betydligt längre än vad som nog är förnuftigt. <a href="https://github.com/paokarlsson/spola">Spola</a> är ett webbramverk för Java 25 som ersätter det ett webb-API behöver från Spring Boot och Lombok, utan annoteringsmagi och utan ett enda beroende utanför JDK:n. <a href="https://github.com/paokarlsson/sola">Sola</a> är tänkt att bli dess motsvarighet i webbläsaren. Och nästan all kod skrivs av AI-agenter. Frågan jag vill pröva är enkel att ställa: <strong>är det här genialiskt eller vansinnigt?</strong></p>

  <section class="section">
    <p class="eyebrow">01 · Vad det är</p>
    <h2>Två ramverk, en idé</h2>
    <div class="cards">
      <div class="card"><span class="tag assess">Spola · version 0.x</span><h3>Spring + Ola</h3><p>HTTP/1.1 på virtuella trådar med TLS, routing som kod, en strikt JSON-parser med explicit mappning till records, validering, konfiguration, en REST-klient och säkerhet med lösenordshashning, sessioner och CSRF-skydd. Bara JDK 25, ingen reflektion vid start och inga andra annoteringar än en handfull från JDK:n.</p></div>
      <div class="card"><span class="tag assess">Sola · tidig fas</span><h3>Solid + Ola</h3><p>Ett frontendramverk utan beroenden och utan byggsteg: signals, tagged template literals och routing ovanpå Navigation API, URLPattern och import maps. Hela runtime i en fil som checkas in i appen. Designen är klar, och de första raderna – en devserver som serverar appen under strikt CSP – har precis kommit på plats.</p></div>
    </div>
    <p class="copy" style="margin-top:24px">Båda följer samma princip: man uppfinner inte ett ramverk, man bryter ut det ur en riktig app när samma lösning skrivs för andra gången. Spola växer bara när ett projekt skickar in ett <em>behov</em> som har en motsvarighet i Spring eller Lombok.</p>
    <div class="note"><strong>Det här är ett hobby- och labbprojekt.</strong> README:n säger det rakt ut: inte redo för produktion, ingen support, och säkerhetsmodulerna är inte granskade av en människa. Allt nedan ska läsas med det i bakhuvudet.</div>
  </section>

  <section class="section callout big">
    <p class="eyebrow">02 · Hur koden blir till</p>
    <h2>En loop som försöker sänka sitt eget arbete</h2>
    <p class="copy">Spola skrivs inte av mig utan av en loop med Claude Code-agenter som jag kallar gauntlet-loopen. Varje iteration ser ut ungefär så här:</p>
    <div class="flow">
      <div class="step"><b>1. Planeraren</b><span>Väljer nästa uppdrag eller prövar ett behov mot regeln: finns det i Spring eller Lombok, går det inom reglerna och saknas det? Annars avvisas det.</span><span class="arrow">→</span></div>
      <div class="step"><b>2. Byggaren</b><span>Skriver koden och testerna. Den enda agenten som får ändra i ramverket.</span><span class="arrow">→</span></div>
      <div class="step"><b>3. Tre kritiker</b><span>Med färsk kontext: en försöker bryta koden, en bockar av kraven, en bedömer tydlighet och ”magi”.</span><span class="arrow">→</span></div>
      <div class="step"><b>4. Domaren</b><span>Verifierar fynden, slänger falska och dubbletter och ger utslaget. Bara rundor med grönt bygge committas.</span></div>
    </div>
    <p class="copy">Bygget kontrollerar dessutom själv att grundreglerna i <code>REGLER.md</code> följs – inga tredjepartsberoenden, inga egna annoteringar, ingen reflektion som styr logik – och de reglerna får aldrig ändras eller kringgås av ett uppdrag.</p>
    <div class="metrics">
      <div class="metric"><strong>4 veckor</strong><span>Sedan första iterationen i början av oktober.</span></div>
      <div class="metric"><strong>29</strong><span>Klara uppdrag, från bygget till en säkerhetsöversyn i fyra delar.</span></div>
      <div class="metric"><strong>~77 000</strong><span>Rader Java, varav drygt hälften är tester.</span></div>
      <div class="metric"><strong>1</strong><span>Rad i mjukvaruförteckningen: JDK 25.</span></div>
    </div>
  </section>

  <section class="section">
    <p class="eyebrow">03 · Kritiken</p>
    <h2>Det som talar för vansinne</h2>
    <p class="copy">Jag har försökt skriva den kritik jag själv skulle ge om någon annan visade upp det här. Den börjar med det som faktiskt är bra: processen är mer genomtänkt än i de flesta projekt där AI skriver koden, behovsstyrd tillväxt är klassiskt sunt, tajmingen med Java 25 och dagens webbplattform är rimlig och ärligheten i README:n är föredömlig. Sedan kommer resten.</p>
    <div class="cards">
      <div class="card"><span class="tag remove">Risken flyttar</span><h3>Noll beroenden är inte noll risk</h3><p>Jackson, Tomcat och Spring Security har angripits av hela världen i femton år. Spola ersätter dem med kod som ingen människa har läst. Man byter leverantörskedjerisk mot kodkvalitetsrisk, och den senare är troligen större. En egen HTTP-parser är precis där request smuggling bor.</p></div>
      <div class="card"><span class="tag remove">Samma blinda fläckar</span><h3>Kritikerna är inte så oberoende</h3><p>Färsk kontext hjälper mot slarvfel. Men om kritikerna är samma modell som byggaren delar de blinda fläckar, och byggaren skriver testerna. Grönt bygge betyder att koden gör vad testerna säger, inte att den är korrekt.</p></div>
      <div class="card"><span class="tag assess">Två mål</span><h3>”Ingen magi” kräver inte noll beroenden</h3><p>Javalin och Helidon SE ger explicit wiring utan annoteringsmagi, med få och väletablerade beroenden. Det första målet är billigt. Det andra kostar enormt.</p></div>
      <div class="card"><span class="tag assess">Krock framåt</span><h3>PostgreSQL och JWT</h3><p>JDBC finns i JDK:n, men Postgres-drivrutinen gör det inte. Antingen skriver man wire-protokollet själv eller bryter man regeln som inte får brytas. JWT betyder mer egenhändig krypto.</p></div>
      <div class="card"><span class="tag remove">Fel publik</span><h3>Offentlig sektor vill ha tråkig teknik</h3><p>Exempelappen är ett bokningssystem för brukare och utförare. Där vill man ha teknik som hundratals konsulter kan, som går att upphandla och som klarar en granskning – inte ett ramverk med en person, noll stjärnor och dokumentation på svenska.</p></div>
      <div class="card"><span class="tag assess">Ännu en idé</span><h3>Sola är mest design</h3><p>Det går bara att bedöma idén, och den liknar Lit, htm och Preact Signals. Bra sällskap, men inte nytt.</p></div>
    </div>
    <div class="quote">Som experiment är det närmare genialiskt än vansinnigt. Som något man bygger system på är det nära vansinnigt.</div>
  </section>

  <section class="section">
    <p class="eyebrow">04 · Försvaret</p>
    <h2>Kalkylen bakom kritiken håller på att ändras</h2>
    <p class="copy">Kritiken vilar på ett antagande som var sant i tjugo år: att det är dyrt att skriva kod och billigt att lägga till ett beroende. Hela open source-ekonomin bygger på den kalkylen. När AI gör det billigt att skriva kod flyttas kostnaden till att <em>verifiera</em> koden. Spola är ett försök att ta den förskjutningen på allvar, och borde nog bedömas efter det.</p>
    <div class="grid-2">
      <div class="copy">
        <h3>Förvaltning, inte leverantörskedja</h3>
        <p>Den som har förvaltat ett Spring-system vet att den stora kostnaden sällan är säkerhetshålen, utan omsättningen: bytet från <code>javax</code> till <code>jakarta</code>, Log4Shell som tvingade fram nödpatchning en julvecka, och en jämn ström av uppdateringar som någon måste testa. En stack som bara består av JDK:n och webbläsarens standarder har den längsta livslängd som går att få.</p>
        <h3>Mindre attackyta genom design</h3>
        <p>Många av Jacksons allvarligaste sårbarheter har handlat om polymorf deserialisering – just den sortens reflektionsmagi som reglerna förbjuder. Och HTTP-parsern kan göras ointressant genom att vara strikt: allt tvetydigt ger 400 i stället för en tolkning. Request smuggling uppstår när två parsrar tolkar samma tvetydighet olika. En parser som vägrar tolka stänger den dörren.</p>
      </div>
      <div class="copy">
        <h3>Noll beroenden är det som får loopen att fungera</h3>
        <p>Det här tycker jag är det starkaste argumentet. Hela Spola ryms i en agents kontext. Agenterna kan läsa all kod som påverkar ett beteende i stället för att gissa vad ett bibliotek gör internt, och varje beslut finns i git och körningsloggarna. ”Ingen magi” och ”noll beroenden” är, sett från agentens håll, samma mål: allt ska gå att följa.</p>
        <h3>PostgreSQL är ett löst problem</h3>
        <p>Ett datalager kan bygga enbart på <code>java.sql</code> och låta appen välja drivrutin vid sin egen kant. Vill man gå längre är Postgres wire-protokoll version 3 stabilt sedan 2003 och SCRAM-SHA-256 går att bygga på JDK:ns kryptoprimitiver. En avgränsad uppgift, inte en avgrund.</p>
      </div>
    </div>
    <p class="copy" style="margin-top:24px">Försvaret har fler punkter. Att offentlig sektors verkliga problem inte är brist på Spring-konsulter utan system som inte har råd att följa med i ramverkens uppgraderingstakt – och att en mjukvaruförteckning med en enda rad blir en reell fördel med EU:s Cyber Resilience Act. Att kunskapen inte sitter i ett huvud utan i regler, arkitekturbeslut, körningsloggar och en körbar loop under Apache 2.0. Och att ett ramverk som extraheras ur en riktig app per definition inte kan finnas innan appen finns – vilket är precis poängen med Sola.</p>
  </section>

  <section class="section">
    <p class="eyebrow">05 · En liten kontroll</p>
    <h2>Vad säger koden själv?</h2>
    <p class="copy">Det är lätt att argumentera i det abstrakta, så jag tittade på vad som faktiskt finns i repot. En del av försvaret är redan verklighet, en del är bara förslag.</p>
    <div class="table-wrap"><table>
      <thead><tr><th>Påstående</th><th>Läget i koden</th><th>Bedömning</th></tr></thead>
      <tbody>
        <tr><td>Parsern vägrar tvetydigheter</td><td>En request med både <code>Transfer-Encoding</code> och <code>Content-Length</code> ger 400 med hänvisning till RFC 9112, och det finns tester för smugglade requests i kroppen</td><td>Finns</td></tr>
        <tr><td>Reglerna upprätthålls av bygget</td><td>En egen guardrails-modul körs i varje bygge, före testerna</td><td>Finns</td></tr>
        <tr><td>Säkerhetskod mot officiella testvektorer</td><td>Står i grundreglerna. BCrypt testas mot publicerade vektorer från jBCrypt och Openwall, PBKDF2 mot RFC 7914</td><td>Finns</td></tr>
        <tr><td>Externa testsviter och fuzzing</td><td>Inget JSONTestSuite, ingen differentiell testning mot Jackson eller Tomcat</td><td>Saknas</td></tr>
        <tr><td>Kritiker från olika modellfamiljer</td><td>Alla agenter är samma modellfamilj</td><td>Saknas</td></tr>
        <tr><td>Mänsklig granskning av säkerhetsmodulerna</td><td>Uttryckligen inte gjord</td><td>Saknas</td></tr>
      </tbody>
    </table></div>
  </section>

  <section class="section callout big">
    <p class="eyebrow">06 · Var det landar</p>
    <h2>Kritiken och försvaret är mer överens än det ser ut</h2>
    <p>Båda sidor tycker att processen är det mest intressanta, att ”ingen magi” är rätt riktning och att verifieringen är den avgörande frågan. Försvaret håller bäst om förvaltningen, om varför noll beroenden gör AI-loopen möjlig och om PostgreSQL via <code>java.sql</code>. Det håller sämst där det förutsätter saker som ännu inte finns: den differentiella testningen och kritikerna från andra modellfamiljer är förslag, inte verklighet. Och suveräniteten är bara verklig om någon hos förvaltaren faktiskt kan läsa och förstå koden.</p>
    <div class="rule">Regeln om noll beroenden gäller det som <em>levereras</em>, inte det som <em>testar</em>.</div>
    <p>Det är den insikten som gör att jag tror att kritikens tre förslag går att genomföra utan att bryta något:</p>
    <div class="flow">
      <div class="step"><b>1. Externa testsviter</b><span>JSONTestSuite och kända testfall för HTTP smuggling – på samma sätt som BCrypt och PBKDF2 redan testas mot publicerade vektorer. Tester som agenten inte själv har hittat på.</span><span class="arrow">→</span></div>
      <div class="step"><b>2. Differentiell fuzzing</b><span>Miljontals slumpade indata genom både Spola och Jackson, Spola och Tomcat, i ett separat testrepo. Varje avvikelse blir ett fynd.</span><span class="arrow">→</span></div>
      <div class="step"><b>3. En annan modell</b><span>Minst en kritiker från en annan modellfamilj, så att de blinda fläckarna inte sammanfaller.</span><span class="arrow">→</span></div>
      <div class="step"><b>4. En människa</b><span>Någon som läser säkerhetsmodulerna innan något med riktiga användaruppgifter rör dem.</span></div>
    </div>
  </section>

  <section class="section">
    <p class="eyebrow">07 · Så här långt har jag kommit</p>
    <h2>Kanske är provbänken produkten</h2>
    <p class="copy">Jag tror att kritikens viktigaste mening är den här: det mest värdefulla som kommer ut av det här är förmodligen inte Spola eller Sola, utan erfarenheten av hur långt man kan driva AI-byggd kod under hårda regler. Ramverken är provbänken för den frågan.</p>
    <p class="copy">Om det fungerar visar det något större än två ramverk – att en person med en disciplinerad AI-process kan äga hela sin stack, från HTTP-parsning till signals i webbläsaren, utan ett beroendeträd. Som bieffekt finns en pedagogisk resurs: varje modul visar Spring-koden och Spola-koden sida vid sida, så att det blir synligt vad magin i Spring faktiskt gör. Men det är ett ”om”.</p>
    <div class="quote">Bygg verifieringen innan ramverket används till något som spelar roll. Med den på plats flyttar sig projektet från intressant experiment till seriöst alternativ. Utan den förblir kritikens varning giltig.</div>
    <div class="note"><strong>Det här är en granskning jag gärna fortsätter tillsammans med andra – inget försvarstal.</strong> Jag är fullt beredd på att kritiken har mer rätt än jag vill tro. Om du har förvaltat Spring-system i offentlig sektor, skrivit HTTP-parsrar eller kört AI-agenter mot riktig kod vill jag gärna höra var du tycker att resonemanget brister. Koden ligger öppet på <a href="https://github.com/paokarlsson/spola">GitHub</a> – och den som hittar en request som tar sig förbi parsern får gärna öppna ett issue.</div>
  </section>
