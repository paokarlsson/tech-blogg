---
layout: post.njk
translationKey: vad-kostar-noll-beroenden
title: "Chop down the dependency tree"
subtitle: "Zero dependencies sounded like a bad idea for as long as code was expensive. It isn't any more."
eyebrow: "Java 25 · zero dependencies · AI · a tribute to a bad idea"
dek: "For my whole career I've heard the same thing: never write your own parser, your own framework or your own security. It was wise advice. I think it's about to expire. So I've started doing exactly everything you're not supposed to – and I've rarely had more fun."
description: "A tribute to the idea of software with no dependencies at all: why the old truths about never building it yourself may no longer hold when code gets cheap to write."
date: 2026-10-28
image: "/assets/images/noll-beroenden-hero.en.svg"
imageAlt: "A tangle of interconnected dependencies on the left, a dashed cut line, and on the right a single app standing directly on JDK 25."
chips:
  - "Chop down the tree"
  - "Build it yourself"
  - "Software that ages well"
  - "Sacred cows"
---
  <p class="lead">We've learned that writing code is expensive and adding a dependency is cheap. Our whole industry rests on that arithmetic, and it has been true for so long that we've stopped seeing it as arithmetic. It has become a truth. But what if it isn't any more? <strong>What if it's now cheaper to own your code than to borrow it?</strong></p>

  <section class="section">
    <div class="copy">
      <p class="eyebrow">01 · The thought</p>
      <h2>The industry's holiest rule has expired</h2>
      <p>“Don't reinvent the wheel.” “Never roll your own crypto.” “Use a proven framework.” I've said every one of those sentences myself, and I meant them.</p>
      <p>But look at why they were true. It was never because your own code is wrong in itself. It was because it was expensive. It took weeks to write an HTTP parser, months to make it stable and years to learn all its edge cases. A dependency was one line away.</p>
      <p>Now AI writes that parser in an afternoon. Not perfectly, but well enough to start testing it, sharpening it and learning from it. When one side of the equation collapses that hard, the answer can't stay the same.</p>
      <div class="quote">“Don't reinvent the wheel” was advice about cost. Not a law of nature.</div>
    </div>
  </section>

  <section class="section">
    <p class="eyebrow">02 · The experiment</p>
    <h2>So I broke every single rule</h2>
    <p class="copy">In my earlier post about frameworks I wrote that JSON and security were things I'd leave to the specialist libraries. Since then I've built both myself.</p>
    <p class="copy"><a href="https://github.com/paokarlsson/spola">Spola</a> is a Java 25 web framework that does what a web API needs from Spring Boot and Lombok – HTTP server, routing, JSON, validation, configuration, sessions and login – without annotation magic and without a single dependency outside the JDK. <a href="https://github.com/paokarlsson/sola">Sola</a> is going to be the same thing for the browser: signals, templates and routing straight on the web platform, with no dependencies and no build step. What runs in the browser is exactly what you wrote.</p>
    <p class="copy">The code is mostly written by AI. And both frameworks only grow when a real app needs something, so they never get bigger than what someone actually uses.</p>
    <div class="grid-2" style="margin-top:28px">
      <figure class="figure"><img src="/assets/images/noll-beroenden-spring.en.svg" alt="The dependency tree for spring-boot-starter-web: thirty-odd artifacts from Spring, Jackson, Tomcat, logging and more, four levels deep."><figcaption>This is what you get with <code>spring-boot-starter-web</code>, roughly as Maven shows it for Spring Boot 3. Every line is a version to keep track of.</figcaption></figure>
      <figure class="figure"><img src="/assets/images/noll-beroenden-spola.en.svg" alt="The dependency tree for spola.web: four modules that all stand directly on JDK 25, and then nothing more."><figcaption>This is what you get with <code>spola.web</code>. Four modules, and beneath them only the JDK.</figcaption></figure>
    </div>
    <div class="rule">The whole stack, from the TCP socket to the button in the browser. <em>No</em> dependency tree.</div>
  </section>

  <section class="section">
    <p class="eyebrow">03 · What you gain</p>
    <h2>Software that refuses to rot</h2>
    <div class="copy">
      <p>Anyone who has maintained a Spring system knows where the time actually goes. Not to the business logic, but to everything around it: the move from <code>javax</code> to <code>jakarta</code>, Log4Shell over Christmas, dependency upgrades every sprint, and that time a minor version of a library three levels down changed behaviour without anyone noticing.</p>
      <p>A system that stands only on the JDK and browser standards has none of that. Java is ridiculously backwards compatible. The web has a principle of never breaking an existing page. Build only on them and the code you write today can still work in twenty years.</p>
      <p>And the best part: you can read all of it. Nobody can read all of Spring. But the whole HTTP server in Spola can be read in a few evenings. When something goes wrong there's no black box to blame, and nothing happening behind your back.</p>
    </div>
    <div class="metrics">
      <div class="metric"><strong>Lifespan</strong><span>No forced migrations, ever.</span></div>
      <div class="metric"><strong>Readability</strong><span>Every line that affects a behaviour is in your own repo.</span></div>
      <div class="metric"><strong>Ownership</strong><span>No vendors, no licensing questions, no surprises.</span></div>
      <div class="metric"><strong>Calm</strong><span>No CVE alerts for libraries you never knew you had.</span></div>
    </div>
  </section>

  <section class="section">
    <p class="eyebrow">04 · Old truths</p>
    <h2>Six sacred cows to slaughter</h2>
    <p class="copy">Here are some of the things I was taught never to touch. I think every one of them is worth questioning now.</p>
    <div class="cards">
      <div class="card"><span class="tag remove">Old truth</span><h3>“Never write your own HTTP parser”</h3><p>Request smuggling happens when two parsers interpret the same ambiguity differently. A parser that refuses to interpret – that answers 400 to anything ambiguous – closes that whole door. Strict beats clever.</p></div>
      <div class="card"><span class="tag remove">Old truth</span><h3>“Never write your own JSON parser”</h3><p>Many of the worst vulnerabilities in JSON libraries come from polymorphic deserialization, which is reflection magic. Explicit mapping to records doesn't have that kind of bug. The simplest thing is the safest.</p></div>
      <div class="card"><span class="tag remove">Old truth</span><h3>“You need a build step”</h3><p>ES modules, import maps and dynamic <code>import()</code> are in every browser. No bundler, no transpiling, no <code>node_modules</code> with a thousand folders.</p></div>
      <div class="card"><span class="tag remove">Old truth</span><h3>“You need a DI container”</h3><p>Constructors exist. Plain Java code that wires the objects together can be followed with “Go to definition”, and a missing dependency becomes a startup error instead of a surprise in production.</p></div>
      <div class="card"><span class="tag remove">Old truth</span><h3>“The database needs an ORM”</h3><p><code>java.sql</code> has been in the JDK for over twenty years. Clear SQL and one record per row go further than we usually think.</p></div>
      <div class="card"><span class="tag remove">Old truth</span><h3>“Never touch security”</h3><p>The JDK already has the cryptographic primitives. Password hashing built on top of them and tested against official test vectors isn't magic – it's diligence.</p></div>
    </div>
  </section>

  <section class="section callout big">
    <p class="eyebrow">05 · A suggested order</p>
    <h2>Turn the whole question around</h2>
    <p class="copy">In the first post I suggested an order that ended with “let the specialist take it”. Now I want to try turning it around. Instead of asking when we're allowed to build it ourselves, we ask when we really have to borrow.</p>
    <div class="flow">
      <div class="step"><b>1. Is it in the platform?</b><span>The JDK and the browser can do far more than we usually think. Always start there.</span><span class="arrow">→</span></div>
      <div class="step"><b>2. Can we write it strictly?</b><span>If the behaviour can be described clearly and everything else can be rejected, it can be written – and AI writes it fast.</span><span class="arrow">→</span></div>
      <div class="step"><b>3. Can we test it against the best?</b><span>Run the same input through your own code and through Jackson or Tomcat. The mature libraries become the answer key instead of the foundation.</span><span class="arrow">→</span></div>
      <div class="step"><b>4. Only then: borrow</b><span>If none of that works, take on a dependency. But do it as an exception, not a reflex.</span></div>
    </div>
  </section>

  <section class="section">
    <p class="eyebrow">06 · What we'd gain</p>
    <h2>Take back control of your system</h2>
    <p class="copy">This isn't about a prettier dependency tree. It's about who gets to decide over your system: you, or whoever maintains library number 47 in the lockfile.</p>
    <div class="table-wrap"><table>
      <thead><tr><th>If we own it ourselves…</th><th>We get…</th><th>And we're spared…</th></tr></thead>
      <tbody>
        <tr><td>The HTTP server</td><td>A strict parser we can read from start to finish</td><td>Emergency patches for code we've never seen</td></tr>
        <tr><td>JSON handling</td><td>Visible mapping to our own types</td><td>The whole class of deserialization bugs</td></tr>
        <tr><td>Security</td><td>Full insight into how login and sessions work</td><td>Configuration magic nobody on the team understands</td></tr>
        <tr><td>The frontend</td><td>Code that runs exactly as it was written</td><td>Build chains, bundlers and framework migrations</td></tr>
        <tr><td>The whole stack</td><td>A bill of materials with one line: JDK 25</td><td>Vendor lock-in and licensing questions</td></tr>
      </tbody>
    </table></div>
  </section>

  <section class="section callout big">
    <p class="eyebrow">07 · The dream</p>
    <h2>A system that outlives its developers</h2>
    <p>Imagine a booking system for a municipality. It's built once, properly, and then it's just allowed to live. No forced upgrade every three years. No consultant who has to come in to lift the framework. The code lives in the municipality's own repository, and anyone who wants to understand it can read it, all the way down.</p>
    <p>That isn't how public systems usually work today. But not because it's impossible. It's because writing everything yourself has been too expensive. And that's exactly the cost that is disappearing.</p>
    <div class="rule">The best dependency is the one that <em>never</em> needs updating.</div>
  </section>

  <section class="section">
    <p class="eyebrow">08 · Where I've got to so far</p>
    <h2>Stop apologising for building it yourself</h2>
    <p class="copy">For years, “I built it myself” has sounded like a confession. Something you say a little quietly, with an explanation afterwards. I think it's time to say it out loud again.</p>
    <p class="copy">When code gets cheap, it suddenly becomes possible for a single person to own their whole stack, from HTTP parsing to signals in the browser. That isn't a step back to how we did things before open source. It's something new: as free as writing everything yourself, almost as cheap as borrowing.</p>
    <div class="quote">We stopped building it ourselves because it was expensive. It isn't expensive any more. So why did we stop?</div>
  </section>

  <section class="section">
    <p class="eyebrow">09 · A small disclaimer</p>
    <h2>Okay, okay. There are problems.</h2>
    <p class="copy">Jackson, Tomcat and Spring Security have been attacked by the whole world for fifteen years, and my code hasn't. When the same tool writes both the code and the tests, a green build only means the code does what the tests say. Cryptography like JWT is still an area where I tread carefully. And Spola is version 0.x, with security parts that haven't yet been reviewed by a human – don't use it to protect anything real. All of this can be solved with external testing, comparisons against the reference libraries and a human review. But it needs doing.</p>
    <div class="note"><strong>This is a tribute, not a recipe.</strong> I know it's a bit naive, and that's the point. If you think I'm wrong I'd love to hear why – but do also tell me which old truth you'd like to put to the test yourself.</div>
  </section>
