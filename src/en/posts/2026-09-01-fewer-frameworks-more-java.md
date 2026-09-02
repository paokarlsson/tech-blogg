---
layout: post.njk
translationKey: mindre-ramverk-mer-java
title: "What if we needed fewer frameworks?"
subtitle: "A thought on dependencies, Spring Boot, and what Java 25 already gives us"
eyebrow: "Java 25 · Spring Boot 4 · an idea still taking shape"
dek: "We've gotten really good at adding libraries. I've started to wonder whether the next improvement might be removing a few – without making the system dumber, riskier, or harder to operate. This is a line of reasoning, not a conclusion."
description: "An attempt to reason about when Spring Boot is genuinely needed and when plain Java 25 might be enough — with a suggested order of decisions."
date: 2026-09-01
image: "/assets/images/hero.webp"
imageAlt: "Abstract visualization of many technical layers being pared back toward a simple core."
chips:
  - "Fewer dependencies?"
  - "More plain Java"
  - "Spring where it earns its keep"
  - "Less to maintain"
---
  <p class="lead">For years, Java development has often meant reaching for a framework or library the moment a new need appears. That's been rational, and I've done the same. But the Java platform has grown, the language has gotten better, and the cost of writing mechanical code by hand has dropped. So I've started turning over a question I don't have a finished answer to: <strong>how much of what we usually add do we still actually need?</strong></p>

  <section class="section grid-2">
    <div class="copy">
      <p class="eyebrow">01 · The idea</p>
      <h2>This isn't about Spring being the problem</h2>
      <p>Spring Boot solves a lot of hard problems, and it solves them well. For public APIs, security, advanced routing, observability, and large integration surfaces, Spring is probably still the cheapest option overall.</p>
      <p>But Spring has become such a default reach that I suspect we sometimes grab it even when the problem is smaller than the solution. That's the suspicion I want to examine here.</p>
      <p>A small internal service might need only a handful of HTTP calls, a database, one outgoing call, and some business logic. Java 25 already has an HTTP client, JDBC, scheduling, records, logging, JFR/JMX, and modern concurrency tools. Virtual threads also make plain, blocking code considerably more attractive for I/O than it was a few years ago.</p>
      <div class="quote">Java hasn't become a new Spring. But maybe the line for what actually needs a framework has shifted a little?</div>
    </div>
    <figure class="figure">
      <img src="/assets/images/figure-01.webp" alt="Abstract network diagram where a clear core connects to a limited number of outer systems.">
      <figcaption>A goal I find appealing: a clear core and a small number of deliberate boundaries toward the outside world.</figcaption>
    </figure>
  </section>

  <section class="section">
    <p class="eyebrow">02 · The maintenance surface</p>
    <h2>Maybe dependencies are a bit of an iceberg</h2>
    <div class="grid-2">
      <div class="copy">
        <p>When we look at a <code>pom.xml</code> or <code>build.gradle</code>, we only see part of the system's technical surface. Underneath it sit transitive libraries, version couplings, autoconfiguration, proxies, annotation processing, and conventions that someone has to understand the day something breaks.</p>
        <p>Counting JAR files therefore feels like a blunt measure. A small external dependency can be very cheap. Four hundred lines of hand-rolled OAuth code can be very expensive.</p>
        <p><strong>So by minimalism I don't mean the least code, or zero libraries.</strong> Rather, less unnecessary semantics – less technology the team has to carry over time.</p>
      </div>
      <figure class="figure"><img src="/assets/images/figure-02.webp" alt="Iceberg where a small visible tip represents direct dependencies and a much larger structure below the surface represents the hidden maintenance surface."><figcaption>Direct dependencies are the visible part. My sense is that maintenance cost usually sits in everything that comes along with them.</figcaption></figure>
    </div>
    <div class="metrics">
      <div class="metric"><strong>Versions</strong><span>Upgrades, compatibility, and coordination.</span></div>
      <div class="metric"><strong>Security</strong><span>CVEs, parser and network surface, patch work.</span></div>
      <div class="metric"><strong>Semantics</strong><span>Hidden rules, proxy behavior, and lifecycle.</span></div>
      <div class="metric"><strong>Change</strong><span>How much needs to be understood next time requirements shift?</span></div>
    </div>
  </section>

  <section class="section callout big">
    <p class="eyebrow">03 · A proposed order</p>
    <h2>What if we asked in this order?</h2>
    <p class="copy">Instead of starting with "which library should replace this?", you could work through four steps. The further right we get, the more specialized semantics we choose to let someone else own. The order isn't a truth – mostly a way to make the choice deliberate.</p>
    <div class="flow">
      <div class="step"><b>1. Is it needed at all?</b><span>Is the behavior needed in the first place? A cache or internal event bus that never gets built has no implementation to maintain.</span><span class="arrow">→</span></div>
      <div class="step"><b>2. Is it in the JDK?</b><span>Is there a direct, sufficient solution in Java 25? For example an HTTP client, files, Base64, scheduling.</span><span class="arrow">→</span></div>
      <div class="step"><b>3. Does a bit of our own code suffice?</b><span>Is the semantics simple and local? Mapping, configuration, a small retry loop, or a composition root can turn out to be fairly clear, ordinary Java.</span><span class="arrow">→</span></div>
      <div class="step"><b>4. Let the specialist handle it</b><span>Is it about JSON, OAuth/OIDC, connection pooling, broker protocols, or advanced telemetry? Then I think a mature library is almost always cheaper.</span></div>
    </div>
  </section>

  <section class="section">
    <p class="eyebrow">04 · Where Spring might fit best</p>
    <h2>What if Spring lived at the edge?</h2>
    <p class="copy">The idea I personally find most interesting isn't about removing Spring Boot. It's about maybe no longer letting Spring be the application's primary programming model.</p>
    <div class="arch" role="img" aria-label="Architecture diagram: the outside world reaches Spring at the edge, then a core in plain Java, then adapters to external systems.">
      <div class="arch-grid">
        <div class="arch-node"><div class="arch-label">Outside world</div><div class="arch-title">HTTP · identity · operations</div><div class="arch-copy">Protocols, routing, security, and standardized observability are complex and change over time.</div></div>
        <div class="arch-node edge"><div class="arch-label">The edge</div><div class="arch-title">Spring where it helps</div><div class="arch-copy">WebMVC, Security, adapters, and bootstrap. The framework translates into the application's own types.</div></div>
        <div class="arch-node core"><div class="arch-label">The core</div><div class="arch-title">Plain Java</div><div class="arch-copy">Domain, use cases, records, constructors, invariants, and small ports without Spring types.</div></div>
        <div class="arch-node ext"><div class="arch-label">Boundaries</div><div class="arch-title">Small adapters</div><div class="arch-copy">JDBC, JSON, external APIs, and queues are wrapped behind clear interfaces.</div></div>
      </div>
    </div>
    <p class="copy" style="margin-top:24px">My thinking is that if the core is free of Spring, the next decision becomes less dramatic. A complex service can happily stay on trimmed-down Boot. A small internal service could later move further toward plain JDK. A batch job or worker might never have needed Spring in the first place. But that's just a thought – I don't know how well it holds up in your systems.</p>
  </section>

  <section class="section">
    <p class="eyebrow">05 · A few things I'm curious about</p>
    <h2>Not everything probably needs the same treatment</h2>
    <div class="cards">
      <div class="card"><span class="tag remove">Maybe simpler today</span><h3>Lombok and mappers</h3><p>Records and explicit code mean some of the mechanical help feels less valuable than it used to.</p></div>
      <div class="card"><span class="tag remove">JDK is often enough</span><h3>Outbound HTTP</h3><p>The JDK HttpClient seems to go a long way for ordinary service-to-service communication.</p></div>
      <div class="card"><span class="tag assess">Depends on the service</span><h3>Spring DI</h3><p>Constructor injection needs no container. At the same time, a large and dynamic object graph can very well justify Spring.</p></div>
      <div class="card"><span class="tag assess">Worth a look</span><h3>JPA / Hibernate</h3><p>For clear SQL and a limited model, JDBC can be simpler. For rich object graphs, an ORM is probably still cheaper.</p></div>
      <div class="card"><span class="tag keep">I'd keep this here</span><h3>JSON and security</h3><p>General-purpose JSON parsing and OAuth/OIDC carry difficult semantics that should rarely become in-house infrastructure.</p></div>
      <div class="card"><span class="tag keep">I'd keep this here</span><h3>Connection pool</h3><p>JDBC comes with the JDK, but a production-grade pool doesn't. HikariCP feels like an obvious dependency to keep.</p></div>
    </div>
  </section>

  <section class="section">
    <p class="eyebrow">06 · What would we gain?</p>
    <h2>If it holds, it's about maintenance cost</h2>
    <p class="copy">What would make this idea worth anything isn't a tidier dependency tree. It's whether, over several years, the team ends up with less technology to coordinate, fewer layers to understand, and less impact when the platform is upgraded. And that's of course an assumption that needs to be tested.</p>
    <div class="table-wrap"><table>
      <thead><tr><th>If we reduce…</th><th>We might gain…</th><th>But only if…</th></tr></thead>
      <tbody>
        <tr><td>External dependency families</td><td>Fewer separate version and upgrade tracks</td><td>We don't replace them with large in-house frameworks</td></tr>
        <tr><td>Spring types in the domain</td><td>Less impact from framework upgrades and simpler tests</td><td>The boundaries between core and adapters stay clear</td></tr>
        <tr><td>Runtime magic</td><td>More visible control flow and easier debugging</td><td>The explicit code stays small and understandable</td></tr>
        <tr><td>Excessive standardization in code</td><td>Less local infrastructure</td><td>The organization still standardizes important contracts and operational behavior</td></tr>
      </tbody>
    </table></div>
  </section>

  <section class="section callout big">
    <p class="eyebrow">07 · One thing that may have changed</p>
    <h2>More code can sometimes mean a smaller system</h2>
    <p>AI makes it cheaper to produce mechanical mappers, JDBC row mappers, config records, adapters, tests, and repetitive decorators. If that's true, it lowers the value of abstractions whose main contribution is that we get to skip writing a few lines.</p>
    <p>At the same time, AI hardly makes protocols, cryptography, parser edge cases, concurrency, or transaction semantics any less dangerous. It's quick to generate a connection pool. That doesn't mean the team should own one.</p>
    <div class="rule">A bit more <em>visible code</em> could add up to a considerably smaller system.</div>
  </section>

  <section class="section">
    <p class="eyebrow">08 · Where I've landed so far</p>
    <h2>Maybe minimalism is mostly about choosing responsibility</h2>
    <p class="copy">I don't see the point in making "zero Spring" a creed. But I do think there's something to making every dependency a deliberate choice.</p>
    <p class="copy">A small service might get by on the JDK's HTTP server. A complex public-facing service can happily stay on WebMVC and Spring Security. A worker might end up being nearly plain Java. What they'd have in common is that the business logic gets to be ordinary Java, and specialist libraries are kept at clear boundaries.</p>
    <div class="quote">Ask first whether it's needed. Then check the JDK. Write small, concrete code when the semantics are your own. And let specialist libraries take on what belongs to a hard protocol, a security standard, or a resource manager.</div>
    <div class="note"><strong>This is an idea I'd like to keep thinking through together with others – not a migration recipe.</strong> I'm fully prepared for it to hold up worse in reality than on paper. The question I find interesting isn't "can we remove Spring?", but "which technology actually gives the lowest total cost of ownership for this particular service?" If you've seen evidence pointing the other way, I'd genuinely like to hear it.</div>
  </section>
