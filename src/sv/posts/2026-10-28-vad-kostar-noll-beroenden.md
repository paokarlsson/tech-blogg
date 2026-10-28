---
layout: post.njk
translationKey: vad-kostar-noll-beroenden
title: "Vad kostar noll beroenden när koden blir billig?"
subtitle: "En fortsättning på tanken om färre ramverk – och ett experiment som tar den för långt"
eyebrow: "Java 25 · beroenden · AI · en idé under utveckling"
dek: "I ett tidigare inlägg skrev jag att JSON-parsning och säkerhet var saker jag skulle låta specialistbiblioteken ta hand om. Sedan dess har jag börjat bygga just det själv. Det här är ett försök att förstå varför, och om det är klokt eller bara envist."
description: "Om AI gör det billigt att skriva kod, flyttar då gränsen för vad vi bör äga själva? Ett resonemang kring noll beroenden, förvaltning och verifiering – med två hobbyprojekt som provbänk."
date: 2026-10-28
chips:
  - "Billig kod?"
  - "Dyr verifiering"
  - "Noll beroenden"
  - "Ägarskap över tid"
---
  <p class="lead">I inlägget om färre ramverk landade jag i en ganska försiktig slutsats: skriv vanlig Java där semantiken är din egen, men låt mogna bibliotek ta JSON, säkerhet och annat som bär på svåra gränsfall. Jag tror fortfarande att det är ett rimligt råd. Men jag har börjat undra om en av förutsättningarna bakom det håller på att ändras. Frågan jag vill resonera kring är: <strong>om det blir billigt att skriva kod, flyttar då gränsen för vad vi bör äga själva?</strong></p>

  <section class="section">
    <div class="copy">
      <p class="eyebrow">01 · Tanken</p>
      <h2>Kanske har kalkylen bakom beroenden ändrats</h2>
      <p>Under lång tid har det varit dyrt att skriva kod och billigt att lägga till ett beroende. Hela open source-ekonomin vilar på den kalkylen, och den har tjänat oss väl. Varför skriva en HTTP-parser när tusentals andra redan har gjort det bättre?</p>
      <p>Med AI blir det första ledet i kalkylen mycket billigare. Det betyder inte att koden blir bra av sig själv. Min känsla är snarare att kostnaden flyttar: från att <em>skriva</em> koden till att <em>veta att den stämmer</em>.</p>
      <p>Om det stämmer blir frågan inte längre ”orkar vi bygga det här?” utan ”klarar vi att verifiera det här, och att bära det över tid?”. Och det är en annan fråga, med andra svar.</p>
      <div class="quote">När det blir billigt att skriva kod blir det kanske dyrt att lita på den i stället.</div>
    </div>
  </section>

  <section class="section">
    <p class="eyebrow">02 · Experimentet</p>
    <h2>Två hobbyprojekt som tar idén för långt</h2>
    <p class="copy">För att pröva tanken har jag gjort det jag i förra inlägget avrådde från. <a href="https://github.com/paokarlsson/spola">Spola</a> är ett webbramverk för Java 25 som gör det ett webb-API behöver från Spring Boot och Lombok – HTTP-server, routing, JSON, validering, konfiguration och säkerhet – utan annoteringsmagi och utan ett enda beroende utanför JDK:n. <a href="https://github.com/paokarlsson/sola">Sola</a> är tänkt att bli motsvarigheten i webbläsaren: signals, mallar och routing ovanpå webbplattformens egna API:er, utan beroenden och utan byggsteg. Spola har vuxit en bra bit. Sola har precis börjat.</p>
    <p class="copy">Koden skrivs till största delen av AI under strikta regler, och båda ramverken växer bara när en riktig app behöver något. Man uppfinner inte ett ramverk, man bryter ut det när samma lösning skrivs för andra gången.</p>
    <div class="note"><strong>Det här är experiment, inte produkter.</strong> Spola är version 0.x, inte redo för produktion, och säkerhetsdelarna har inte granskats av en människa. Jag använder projekten som provbänk för frågan ovan, inte som ett förslag på vad någon annan borde köra.</div>
  </section>

  <section class="section">
    <p class="eyebrow">03 · Vad man kanske vinner</p>
    <h2>Kanske handlar noll beroenden mer om förvaltning än om säkerhet</h2>
    <div class="copy">
      <p>Den som har förvaltat ett Spring-system vet att den stora kostnaden sällan är de enskilda säkerhetshålen. Det är omsättningen: bytet från <code>javax</code> till <code>jakarta</code>, Log4Shell som tvingade fram nödpatchning en julvecka, och den jämna strömmen av uppdateringar som någon måste testa. En stack som bara består av JDK:n och webbläsarens standarder skulle kunna ha en väldigt lång livslängd. Java är extremt bakåtkompatibelt, och webben har principen att inte bryta befintliga sidor.</p>
      <p>Det finns också en tanke om attackyta. Många av de allvarligaste sårbarheterna i JSON-bibliotek har handlat om polymorf deserialisering, alltså reflektionsmagi. Explicit mappning till records tar bort hela den klassen av fel. Och en HTTP-parser kan göras ointressant som mål genom att vara strikt: allt tvetydigt får ett 400 i stället för en tolkning. Request smuggling uppstår när två parsrar tolkar samma tvetydighet olika. En parser som vägrar tolka stänger den dörren.</p>
      <p><strong>Med noll beroenden menar jag alltså inte att egen kod är säkrare.</strong> Snarare att den kan vara lättare att äga – om den hålls liten, strikt och läsbar.</p>
    </div>
    <div class="metrics">
      <div class="metric"><strong>Livslängd</strong><span>Ingen tvingad migrering när ett bibliotek byter riktning.</span></div>
      <div class="metric"><strong>Läsbarhet</strong><span>Allt som påverkar ett beteende går att följa i koden.</span></div>
      <div class="metric"><strong>Attackyta</strong><span>Strikt parsning och ingen reflektion i stället för tolkning.</span></div>
      <div class="metric"><strong>Ägarskap</strong><span>Inga leverantörer, inga licensfrågor, en rad i mjukvaruförteckningen.</span></div>
    </div>
  </section>

  <section class="section">
    <p class="eyebrow">04 · Det jag inte riktigt kan svara på</p>
    <h2>Allt håller nog inte lika bra</h2>
    <p class="copy">Jag har försökt vara så hård mot idén som jag skulle vara om någon annan visade upp den. En del invändningar tror jag går att hantera. Andra är jag inte alls säker på.</p>
    <div class="cards">
      <div class="card"><span class="tag remove">Min största tvekan</span><h3>Risken kanske bara flyttar</h3><p>Jackson, Tomcat och Spring Security har angripits av hela världen i femton år. Egen kod har inte det. Man byter kanske leverantörskedjerisk mot kodkvalitetsrisk, och den senare kan mycket väl vara större.</p></div>
      <div class="card"><span class="tag remove">Värt att ta på allvar</span><h3>Gröna tester bevisar inte så mycket</h3><p>När samma verktyg skriver både koden och testerna betyder ett grönt bygge att koden gör vad testerna säger. Inte nödvändigtvis att den är korrekt.</p></div>
      <div class="card"><span class="tag assess">Beror på vad man vill</span><h3>Ingen magi kräver inte noll beroenden</h3><p>Javalin och Helidon SE ger redan explicit wiring utan annoteringar, med få och väletablerade beroenden. Vill man bara bli av med magin finns det billigare vägar.</p></div>
      <div class="card"><span class="tag keep">Kanske lösbart</span><h3>PostgreSQL</h3><p>JDBC finns i JDK:n men drivrutinen gör det inte. Ett datalager kan dock bygga på <code>java.sql</code> och låta appen välja drivrutin vid sin egen kant. Då förblir ramverket fritt från beroenden.</p></div>
      <div class="card"><span class="tag remove">Här skulle jag vara försiktig</span><h3>Kryptografi</h3><p>Lösenordshashning går att bygga på JDK:ns primitiver och testa mot officiella testvektorer. Men JWT och liknande betyder mer egen hantering av krypto, och där är jag mindre bekväm.</p></div>
      <div class="card"><span class="tag assess">Beror på organisationen</span><h3>Offentlig sektor</h3><p>Där vill man ofta ha tråkig teknik som många kan och som går att upphandla. Samtidigt är problemet där ofta system som inte har råd att följa med i ramverkens uppgraderingstakt. Jag vet inte vilket som väger tyngst.</p></div>
    </div>
  </section>

  <section class="section callout big">
    <p class="eyebrow">05 · Ett förslag på ordning</p>
    <h2>Tänk om vi verifierade i den här ordningen?</h2>
    <p class="copy">Om kostnaden verkligen flyttar till verifieringen borde det vara där arbetet läggs. Jag har börjat tänka i fyra steg. Ju längre åt höger, desto mer oberoende blir kontrollen. Ordningen är ingen sanning – mest ett sätt att göra valet medvetet.</p>
    <div class="flow">
      <div class="step"><b>1. Var strikt</b><span>Vägra tolka det som är tvetydigt. Ett tydligt fel är lättare att lita på än en generös gissning.</span><span class="arrow">→</span></div>
      <div class="step"><b>2. Testa mot andras facit</b><span>Officiella testvektorer, JSONTestSuite och kända fall av HTTP smuggling. Tester som ingen i projektet har hittat på.</span><span class="arrow">→</span></div>
      <div class="step"><b>3. Jämför mot referensen</b><span>Slumpad indata genom både den egna parsern och Jackson eller Tomcat. Varje avvikelse blir ett fynd att förstå.</span><span class="arrow">→</span></div>
      <div class="step"><b>4. Låt en människa läsa</b><span>Innan något med riktiga användaruppgifter rör säkerhetskoden behöver någon ha läst den på riktigt.</span></div>
    </div>
  </section>

  <section class="section">
    <p class="eyebrow">06 · Vad skulle vi vinna?</p>
    <h2>Om det stämmer handlar det om ägarskap över tid</h2>
    <p class="copy">Det som skulle göra idén värd något är inte ett tomt beroendeträd i sig. Det är om ett system kan leva i många år utan tvingade migreringar, och om den som förvaltar det faktiskt kan förstå vad det gör. Och det är förstås ett antagande som behöver prövas.</p>
    <div class="table-wrap"><table>
      <thead><tr><th>Om vi äger mer själva…</th><th>Skulle vi kanske få…</th><th>Men bara om…</th></tr></thead>
      <tbody>
        <tr><td>HTTP-parsern</td><td>Färre säkerhetsflöden att följa och ingen tvingad uppgradering</td><td>Den är strikt och prövad mot andras testfall</td></tr>
        <tr><td>JSON-hanteringen</td><td>Ingen polymorf deserialisering och synlig mappning</td><td>Parsern jämförs mot en referens i stor skala</td></tr>
        <tr><td>Säkerheten</td><td>Full insyn i hur inloggning och sessioner fungerar</td><td>En människa har läst och förstått koden</td></tr>
        <tr><td>Frontend utan byggsteg</td><td>Inga beroenden att uppdatera och inga ramverksmigreringar</td><td>Ramverket bryts ut ur en riktig app och inte gissas fram</td></tr>
      </tbody>
    </table></div>
  </section>

  <section class="section callout big">
    <p class="eyebrow">07 · En sak som kan ha ändrats</p>
    <h2>Regeln kanske bara ska gälla det som levereras</h2>
    <p>Länge tänkte jag på noll beroenden som allt eller inget. Men det är kanske inte så. Det som körs i produktion kan vara fritt från beroenden, medan det som testar koden gärna får använda Jackson, Tomcat och vad som helst annat som referens.</p>
    <p>Då blir de mogna biblioteken inte något man bygger på, utan något man mäter sig mot. Det känns som ett rimligare sätt att ta tillvara femton års erfarenhet än att antingen ärva den rakt av eller ignorera den.</p>
    <div class="rule">Det som <em>levereras</em> kan vara fritt från beroenden. Det som <em>testar</em> behöver inte vara det.</div>
  </section>

  <section class="section">
    <p class="eyebrow">08 · Så här långt har jag kommit</p>
    <h2>Kanske är experimentet viktigare än ramverken</h2>
    <p class="copy">Jag ser ingen poäng i att göra noll beroenden till en trosbekännelse. Rådet från förra inlägget står sig för de flesta system: låt specialistbiblioteken ta det som är svårt. Det jag är nyfiken på är om gränsen för vad som räknas som svårt flyttar sig när koden blir billig – och vad verifieringen då måste kosta för att det ska vara värt det.</p>
    <p class="copy">Om det fungerar visar det kanske något större än två ramverk: att man kan äga hela sin stack, från HTTP-parsning till signals i webbläsaren, utan att bära på ett beroendeträd. Om det inte fungerar har jag åtminstone lärt mig var gränsen går, och varför de mogna biblioteken finns.</p>
    <div class="quote">Bygg verifieringen innan koden används till något som spelar roll. Med den på plats kan egen kod bli ett seriöst alternativ. Utan den är det fortfarande ett experiment.</div>
    <div class="note"><strong>Det här är ett experiment jag gärna vill tänka vidare på tillsammans med andra – inget recept.</strong> Jag är fullt beredd på att idén håller sämre i verkligheten än på pappret, och att invändningarna ovan väger tyngre än jag vill tro. Frågan jag tycker är intressant är inte ”kan vi klara oss utan beroenden?”, utan ”vad behöver vi kunna verifiera för att våga äga mer själva?”. Har du erfarenheter som pekar åt ett annat håll vill jag gärna höra dem.</div>
  </section>
