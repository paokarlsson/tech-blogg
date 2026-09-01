---
layout: post.njk
title: "Tänk om vi behövde färre ramverk?"
subtitle: "En tanke om beroenden, Spring Boot och vad Java 25 redan ger oss"
eyebrow: "Java 25 · Spring Boot 4 · en idé under utveckling"
dek: "Vi har blivit riktigt bra på att lägga till bibliotek. Jag har börjat undra om nästa förbättring kan vara att ta bort några – utan att göra systemet dummare, farligare eller svårare att drifta. Det här är ett resonemang, inte en slutsats."
description: "Ett försök att resonera kring när Spring Boot verkligen behövs och när vanlig Java 25 kan räcka — med ett förslag på beslutsordning."
date: 2026-09-01
image: "/assets/images/hero.webp"
imageAlt: "Abstrakt visualisering av många tekniska lager som skalas av mot en enkel kärna."
chips:
  - "Färre beroenden?"
  - "Mer vanlig Java"
  - "Spring där det ger värde"
  - "Mindre att förvalta"
---
  <p class="lead">Under många år har Java-utveckling ofta betytt att vi lägger till ett ramverk eller bibliotek så fort ett nytt behov uppstår. Det har varit rationellt, och jag har gjort likadant. Men Java-plattformen har vuxit, språket har blivit bättre och priset för mekanisk kod har sjunkit. Därför har jag börjat fundera på en fråga jag inte har ett färdigt svar på: <strong>hur mycket av det vi brukar lägga till behöver vi fortfarande?</strong></p>

  <section class="section grid-2">
    <div class="copy">
      <p class="eyebrow">01 · Tanken</p>
      <h2>Det här handlar inte om att Spring är problemet</h2>
      <p>Spring Boot löser många svåra problem, och gör det bra. För publika API:er, säkerhet, avancerad routing, observability och stora integrationsytor är Spring antagligen fortfarande det billigaste alternativet totalt sett.</p>
      <p>Men Spring har blivit så självklart att jag misstänker att vi ibland når efter det även när problemet är mindre än lösningen. Det är den misstanken jag vill undersöka här.</p>
      <p>En liten intern tjänst behöver kanske bara några HTTP-anrop, en databas, ett utgående anrop och lite affärslogik. I Java 25 finns redan HTTP-klient, JDBC, schemaläggning, records, loggning, JFR/JMX och moderna samtidighetsverktyg. Virtuella trådar gör dessutom vanlig, blockerande kod betydligt mer attraktiv för I/O än den var för några år sedan.</p>
      <div class="quote">Java har inte blivit ett nytt Spring. Men kanske har gränsen för vad som behöver ett ramverk flyttat sig lite?</div>
    </div>
    <figure class="figure">
      <img src="{{ metadata.url }}/assets/images/figure-01.webp" alt="Abstrakt nätverksdiagram där en tydlig kärna kopplas till ett begränsat antal yttre system.">
      <figcaption>En målbild jag tycker är tilltalande: en tydlig kärna och ett litet antal medvetna gränser mot omvärlden.</figcaption>
    </figure>
  </section>

  <section class="section">
    <p class="eyebrow">02 · Förvaltningsytan</p>
    <h2>Kanske är beroenden lite av ett isberg</h2>
    <div class="grid-2">
      <div class="copy">
        <p>När vi tittar på en <code>pom.xml</code> eller <code>build.gradle</code> ser vi bara en del av systemets tekniska yta. Under den finns transitiva bibliotek, versionskopplingar, autokonfiguration, proxyer, annotation processing och konventioner som någon behöver förstå den dagen något går fel.</p>
        <p>Att räkna JAR-filer känns därför som ett trubbigt mått. En liten extern dependency kan vara mycket billig. Fyrahundra rader egen OAuth-kod kan vara mycket dyr.</p>
        <p><strong>Med minimalism menar jag alltså inte minst kod eller noll bibliotek.</strong> Snarare mindre onödig semantik – mindre teknik som teamet behöver bära över tid.</p>
      </div>
      <figure class="figure"><img src="{{ metadata.url }}/assets/images/figure-02.webp" alt="Isberg där en liten synlig topp representerar direkta beroenden och en mycket större struktur under ytan representerar den dolda förvaltningsytan."><figcaption>Direkta dependencies är den synliga delen. Min känsla är att förvaltningskostnaden ofta sitter i allt som följer med.</figcaption></figure>
    </div>
    <div class="metrics">
      <div class="metric"><strong>Versioner</strong><span>Uppgraderingar, kompatibilitet och koordinering.</span></div>
      <div class="metric"><strong>Säkerhet</strong><span>CVE:er, parser- och nätverksyta, patcharbete.</span></div>
      <div class="metric"><strong>Semantik</strong><span>Dolda regler, proxybeteenden och lifecycle.</span></div>
      <div class="metric"><strong>Förändring</strong><span>Hur mycket behöver förstås nästa gång kraven flyttar sig?</span></div>
    </div>
  </section>

  <section class="section callout big">
    <p class="eyebrow">03 · Ett förslag på ordning</p>
    <h2>Tänk om vi frågade i den här ordningen?</h2>
    <p class="copy">I stället för att börja med frågan “vilket bibliotek ska ersätta detta?” skulle man kunna gå igenom fyra steg. Ju längre åt höger vi kommer, desto mer specialiserad semantik väljer vi att låta någon annan äga. Ordningen är ingen sanning – mest ett sätt att göra valet medvetet.</p>
    <div class="flow">
      <div class="step"><b>1. Behövs det?</b><span>Behövs beteendet över huvud taget? En cache eller intern event-bus som aldrig byggs har ingen implementation att förvalta.</span><span class="arrow">→</span></div>
      <div class="step"><b>2. Finns det i JDK?</b><span>Finns en direkt och tillräcklig lösning i Java 25? Till exempel HTTP-klient, filer, Base64, scheduling.</span><span class="arrow">→</span></div>
      <div class="step"><b>3. Räcker lite egen kod?</b><span>Är semantiken enkel och lokal? Mappning, konfiguration, en liten retry-loop eller en composition root kan bli ganska tydlig vanlig Java.</span><span class="arrow">→</span></div>
      <div class="step"><b>4. Låt specialisten ta det</b><span>Handlar det om JSON, OAuth/OIDC, anslutningspool, brokerprotokoll eller avancerad telemetry? Då tror jag ett moget bibliotek nästan alltid är billigare.</span></div>
    </div>
  </section>

  <section class="section">
    <p class="eyebrow">04 · Var Spring kanske passar bäst</p>
    <h2>Tänk om Spring fick bo vid kanten?</h2>
    <p class="copy">Den idé jag själv tycker är mest intressant handlar inte om att ta bort Spring Boot. Den handlar om att kanske sluta låta Spring vara applikationens huvudsakliga programmeringsmodell.</p>
    <div class="arch" role="img" aria-label="Arkitekturdiagram: omvärld går via Spring vid kanten till en kärna i vanlig Java och sedan via adapters till externa system.">
      <div class="arch-grid">
        <div class="arch-node"><div class="arch-label">Omvärld</div><div class="arch-title">HTTP · identitet · drift</div><div class="arch-copy">Protokoll, routing, säkerhet och standardiserad observability är komplext och förändras över tid.</div></div>
        <div class="arch-node edge"><div class="arch-label">Kanten</div><div class="arch-title">Spring när det hjälper</div><div class="arch-copy">WebMVC, Security, adapters och bootstrap. Ramverket översätter till applikationens egna typer.</div></div>
        <div class="arch-node core"><div class="arch-label">Kärnan</div><div class="arch-title">Vanlig Java</div><div class="arch-copy">Domän, use cases, records, konstruktorer, invariants och små portar utan Spring-typer.</div></div>
        <div class="arch-node ext"><div class="arch-label">Gränser</div><div class="arch-title">Små adapters</div><div class="arch-copy">JDBC, JSON, externa API:er och köer kapslas bakom tydliga interfaces.</div></div>
      </div>
    </div>
    <p class="copy" style="margin-top:24px">Min tanke är att om kärnan är fri från Spring blir nästa beslut mindre dramatiskt. En komplex tjänst kan lugnt stanna på avskalat Boot. En liten intern tjänst skulle senare kunna gå längre mot ren JDK. En batch eller worker behövde kanske aldrig Spring från början. Men det är just en tanke – jag vet inte hur väl den håller i era system.</p>
  </section>

  <section class="section">
    <p class="eyebrow">05 · Några saker jag är nyfiken på</p>
    <h2>Allt behöver nog inte behandlas lika</h2>
    <div class="cards">
      <div class="card"><span class="tag remove">Kanske enklare idag</span><h3>Lombok och mappare</h3><p>Records och explicit kod gör att en del av den mekaniska hjälpen känns mindre värdefull än den gjorde tidigare.</p></div>
      <div class="card"><span class="tag remove">JDK räcker ofta</span><h3>Utgående HTTP</h3><p>JDK HttpClient verkar räcka långt för vanlig service-to-service-kommunikation.</p></div>
      <div class="card"><span class="tag assess">Beror på tjänsten</span><h3>Spring DI</h3><p>Konstruktorinjektion behöver ingen container. Samtidigt kan en stor och dynamisk objektgraf mycket väl motivera Spring.</p></div>
      <div class="card"><span class="tag assess">Värt att titta på</span><h3>JPA / Hibernate</h3><p>För tydlig SQL och en begränsad modell kan JDBC vara enklare. För rika objektgrafer är ORM antagligen fortfarande billigare.</p></div>
      <div class="card"><span class="tag keep">Här skulle jag behålla</span><h3>JSON och säkerhet</h3><p>Generell JSON-parsning och OAuth/OIDC bär på svår semantik som sällan bör bli egen infrastruktur.</p></div>
      <div class="card"><span class="tag keep">Här skulle jag behålla</span><h3>Connection pool</h3><p>JDBC finns i JDK, men en produktionsmässig pool gör det inte. HikariCP känns som ett självklart kvarvarande beroende.</p></div>
    </div>
  </section>

  <section class="section">
    <p class="eyebrow">06 · Vad skulle vi vinna?</p>
    <h2>Om det stämmer handlar det om förvaltningskostnad</h2>
    <p class="copy">Det som skulle göra idén värd något är inte ett snyggare dependency tree. Det är om teamet över flera år får mindre teknik att koordinera, färre lager att förstå och mindre påverkan när plattformen uppgraderas. Och det är förstås ett antagande som behöver prövas.</p>
    <div class="table-wrap"><table>
      <thead><tr><th>Om vi minskar…</th><th>Skulle vi kanske få…</th><th>Men bara om…</th></tr></thead>
      <tbody>
        <tr><td>Externa dependency families</td><td>Färre separata versions- och uppgraderingsspår</td><td>Vi inte ersätter dem med stora interna ramverk</td></tr>
        <tr><td>Spring-typer i domänen</td><td>Mindre påverkan av ramverksuppgraderingar och enklare tester</td><td>Gränserna mellan kärna och adapters är tydliga</td></tr>
        <tr><td>Runtime-magi</td><td>Synligare kontrollflöde och enklare felsökning</td><td>Den explicita koden förblir liten och begriplig</td></tr>
        <tr><td>Överdriven standardisering i kod</td><td>Mindre lokal infrastruktur</td><td>Organisationen fortfarande standardiserar viktiga kontrakt och driftbeteenden</td></tr>
      </tbody>
    </table></div>
  </section>

  <section class="section callout big">
    <p class="eyebrow">07 · En sak som kan ha ändrats</p>
    <h2>Mer kod kan ibland betyda mindre system</h2>
    <p>AI gör det billigare att skapa mekaniska mappare, JDBC row-mappers, config records, adapters, tester och repetitiva decorators. Om det stämmer minskar värdet av abstraktioner vars viktigaste bidrag är att vi slipper skriva några rader.</p>
    <p>Samtidigt gör AI knappast protokoll, kryptografi, parsergränsfall, concurrency eller transaktionssemantik mindre farliga. Det går snabbt att generera en anslutningspool. Det betyder inte att teamet borde äga en.</p>
    <div class="rule">Lite mer <em>synlig kod</em> skulle kunna ge ett betydligt mindre system.</div>
  </section>

  <section class="section">
    <p class="eyebrow">08 · Så här långt har jag kommit</p>
    <h2>Kanske handlar minimalism mest om att välja ansvar</h2>
    <p class="copy">Jag ser ingen poäng i att göra “noll Spring” till en trosbekännelse. Däremot tror jag att det finns något i att göra varje dependency medveten.</p>
    <p class="copy">En liten tjänst skulle kanske klara sig på JDK:s HTTP-server. En komplex publik tjänst kan gott stanna på WebMVC och Spring Security. En worker kan kanske vara nästan ren Java. Det gemensamma vore att affärslogiken får vara vanlig Java och att specialistbibliotek hålls vid tydliga gränser.</p>
    <div class="quote">Fråga först om det behövs. Titta sedan i JDK. Skriv liten, konkret kod när semantiken är er egen. Och låt specialistbiblioteken ta det som tillhör ett svårt protokoll, en säkerhetsstandard eller en resursmanager.</div>
    <div class="note"><strong>Det här är en idé jag gärna vill tänka vidare på tillsammans med andra – inget migrationsrecept.</strong> Jag är fullt beredd på att den håller sämre i verkligheten än på pappret. Frågan jag tycker är intressant är inte “kan vi ta bort Spring?”, utan “vilken teknik ger faktiskt lägst total ägarbörda för just den här tjänsten?” Har du erfarenheter som pekar åt ett annat håll vill jag gärna höra dem.</div>
  </section>