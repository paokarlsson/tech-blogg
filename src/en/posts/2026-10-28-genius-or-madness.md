---
layout: post.njk
translationKey: genialiskt-eller-vansinnigt
title: "Genius or madness?"
subtitle: "Spola, Sola and the question of what zero-dependency, AI-built code actually costs"
eyebrow: "Java 25 · AI agents · zero dependencies · a review from both sides"
dek: "I have two projects built on the same stubborn idea: a full stack without a single dependency, where the code is written by AI agents under strict rules. This time I try to review them from both sides – first as harshly as I can, then as charitably as I can – and see where it lands."
description: "A critique and a defence of Spola and Sola – two zero-dependency frameworks whose code is written by AI agents – and the conclusion that verification is what decides it."
date: 2026-10-28
chips:
  - "Zero dependencies?"
  - "AI writing the code"
  - "Critics who disagree"
  - "Verify before use"
---
  <p class="lead">In my earlier post about frameworks I reasoned about how much of Spring we actually need. Since then I have taken the idea considerably further than is probably sensible. <a href="https://github.com/paokarlsson/spola">Spola</a> is a Java 25 web framework that replaces what a web API needs from Spring Boot and Lombok, without annotation magic and without a single dependency outside the JDK. <a href="https://github.com/paokarlsson/sola">Sola</a> is meant to become its counterpart in the browser. And almost all of the code is written by AI agents. The question I want to test is easy to ask: <strong>is this genius or madness?</strong></p>

  <section class="section">
    <p class="eyebrow">01 · What it is</p>
    <h2>Two frameworks, one idea</h2>
    <div class="cards">
      <div class="card"><span class="tag assess">Spola · version 0.x</span><h3>Spring + Ola</h3><p>HTTP/1.1 on virtual threads with TLS, routing as code, a strict JSON parser with explicit mapping to records, validation, configuration, a REST client and security with password hashing, sessions and CSRF protection. Only JDK 25, no reflection at startup and no annotations beyond a handful from the JDK.</p></div>
      <div class="card"><span class="tag assess">Sola · early stage</span><h3>Solid + Ola</h3><p>A frontend framework with no dependencies and no build step: signals, tagged template literals and routing on top of the Navigation API, URLPattern and import maps. The whole runtime in one file that is checked into the app. The design is done, and the first lines – a dev server that serves the app under a strict CSP – have just landed.</p></div>
    </div>
    <p class="copy" style="margin-top:24px">Both follow the same principle: you don't invent a framework, you extract it from a real app when the same solution gets written a second time. Spola only grows when a project submits a <em>need</em> that has a counterpart in Spring or Lombok.</p>
    <div class="note"><strong>This is a hobby and lab project.</strong> The README says so plainly: not ready for production, no support, and the security modules have not been reviewed by a human. Read everything below with that in mind.</div>
  </section>

  <section class="section callout big">
    <p class="eyebrow">02 · How the code gets made</p>
    <h2>A loop that tries to sink its own work</h2>
    <p class="copy">Spola isn't written by me but by a loop of Claude Code agents that I call the gauntlet loop. Each iteration looks roughly like this:</p>
    <div class="flow">
      <div class="step"><b>1. The planner</b><span>Picks the next mission or tests a need against the rule: does it exist in Spring or Lombok, does it fit the rules, and is it missing? Otherwise it is rejected.</span><span class="arrow">→</span></div>
      <div class="step"><b>2. The builder</b><span>Writes the code and the tests. The only agent allowed to change the framework.</span><span class="arrow">→</span></div>
      <div class="step"><b>3. Three critics</b><span>With fresh context: one tries to break the code, one checks off the requirements, one judges clarity and “magic”.</span><span class="arrow">→</span></div>
      <div class="step"><b>4. The judge</b><span>Verifies the findings, discards false ones and duplicates, and gives the verdict. Only rounds with a green build are committed.</span></div>
    </div>
    <p class="copy">The build also checks by itself that the ground rules in <code>REGLER.md</code> are followed – no third-party dependencies, no custom annotations, no reflection steering logic – and those rules may never be changed or circumvented by a mission.</p>
    <div class="metrics">
      <div class="metric"><strong>4 weeks</strong><span>Since the first iteration in early October.</span></div>
      <div class="metric"><strong>29</strong><span>Completed missions, from the build to a four-part security review.</span></div>
      <div class="metric"><strong>~77,000</strong><span>Lines of Java, just over half of them tests.</span></div>
      <div class="metric"><strong>1</strong><span>Line in the software bill of materials: JDK 25.</span></div>
    </div>
  </section>

  <section class="section">
    <p class="eyebrow">03 · The critique</p>
    <h2>The case for madness</h2>
    <p class="copy">I have tried to write the critique I would give if someone else showed me this. It starts with what is genuinely good: the process is more thought-through than in most projects where AI writes the code, need-driven growth is classically sound, the timing with Java 25 and today's web platform is reasonable, and the honesty of the README is exemplary. Then comes the rest.</p>
    <div class="cards">
      <div class="card"><span class="tag remove">The risk moves</span><h3>Zero dependencies isn't zero risk</h3><p>Jackson, Tomcat and Spring Security have been attacked by the whole world for fifteen years. Spola replaces them with code no human has read. You trade supply-chain risk for code-quality risk, and the latter is probably larger. A homegrown HTTP parser is exactly where request smuggling lives.</p></div>
      <div class="card"><span class="tag remove">Shared blind spots</span><h3>The critics aren't that independent</h3><p>Fresh context helps against sloppy mistakes. But if the critics are the same model as the builder they share its blind spots, and the builder writes the tests. A green build means the code does what the tests say, not that it is correct.</p></div>
      <div class="card"><span class="tag assess">Two goals</span><h3>“No magic” doesn't require zero dependencies</h3><p>Javalin and Helidon SE already give you explicit wiring without annotation magic, with few, well-established dependencies. The first goal is cheap. The second costs enormously.</p></div>
      <div class="card"><span class="tag assess">Collision ahead</span><h3>PostgreSQL and JWT</h3><p>JDBC is in the JDK, the Postgres driver isn't. Either you write the wire protocol yourself or you break the rule that must not be broken. JWT means more homegrown crypto.</p></div>
      <div class="card"><span class="tag remove">Wrong audience</span><h3>The public sector wants boring tech</h3><p>The example app is a booking system for care recipients and providers. There you want technology hundreds of consultants know, that can be procured and can pass an audit – not a framework with one person behind it, zero stars and documentation in Swedish.</p></div>
      <div class="card"><span class="tag assess">Still an idea</span><h3>Sola is mostly design</h3><p>Only the idea can be judged, and it closely resembles Lit, htm and Preact Signals. Good company, but not new.</p></div>
    </div>
    <div class="quote">As an experiment it is closer to genius than madness. As something you build systems on, it is close to madness.</div>
  </section>

  <section class="section">
    <p class="eyebrow">04 · The defence</p>
    <h2>The arithmetic behind the critique is changing</h2>
    <p class="copy">The critique rests on an assumption that held for twenty years: writing code is expensive and adding a dependency is cheap. The whole open-source economy is built on that arithmetic. When AI makes writing code cheap, the cost moves to <em>verifying</em> the code. Spola is an attempt to take that shift seriously, and should probably be judged on that basis.</p>
    <div class="grid-2">
      <div class="copy">
        <h3>Maintenance, not supply chain</h3>
        <p>Anyone who has maintained a Spring system knows the big cost is rarely the security holes, but the churn: the move from <code>javax</code> to <code>jakarta</code>, Log4Shell forcing emergency patching over Christmas, and a steady stream of upgrades someone has to test. A stack made only of the JDK and browser standards has the longest lifespan you can get.</p>
        <h3>Smaller attack surface by design</h3>
        <p>Many of Jackson's most serious vulnerabilities have involved polymorphic deserialization – exactly the kind of reflection magic the rules forbid. And the HTTP parser can be made uninteresting by being strict: anything ambiguous gets a 400 instead of an interpretation. Request smuggling happens when two parsers interpret the same ambiguity differently. A parser that refuses to interpret closes that door.</p>
      </div>
      <div class="copy">
        <h3>Zero dependencies is what makes the loop work</h3>
        <p>To me this is the strongest argument. All of Spola fits in an agent's context. The agents can read all the code that affects a behaviour instead of guessing what a library does internally, and every decision is in git and the run logs. Seen from the agent's side, “no magic” and “zero dependencies” are the same goal: everything must be traceable.</p>
        <h3>PostgreSQL is a solved problem</h3>
        <p>A data layer can be built solely on <code>java.sql</code> and let the app pick a driver at its own edge. To go further, the Postgres wire protocol version 3 has been stable since 2003, and SCRAM-SHA-256 can be built on the JDK's crypto primitives. A bounded task, not an abyss.</p>
      </div>
    </div>
    <p class="copy" style="margin-top:24px">The defence has more points. That the public sector's real problem is not a lack of Spring consultants but systems that can't afford to keep up with frameworks' upgrade pace – and that a software bill of materials with a single line becomes a real advantage under the EU Cyber Resilience Act. That the knowledge doesn't sit in one head but in rules, architecture decisions, run logs and a runnable loop under Apache 2.0. And that a framework extracted from a real app by definition cannot exist before the app does – which is exactly the point of Sola.</p>
  </section>

  <section class="section">
    <p class="eyebrow">05 · A quick check</p>
    <h2>What does the code itself say?</h2>
    <p class="copy">It is easy to argue in the abstract, so I looked at what is actually in the repository. Some of the defence is already reality, some is only a proposal.</p>
    <div class="table-wrap"><table>
      <thead><tr><th>Claim</th><th>State of the code</th><th>Verdict</th></tr></thead>
      <tbody>
        <tr><td>The parser refuses ambiguity</td><td>A request with both <code>Transfer-Encoding</code> and <code>Content-Length</code> gets a 400 citing RFC 9112, and there are tests for requests smuggled inside a body</td><td>In place</td></tr>
        <tr><td>The build enforces the rules</td><td>A dedicated guardrails module runs in every build, before the tests</td><td>In place</td></tr>
        <tr><td>Security code against official test vectors</td><td>Required by the ground rules. BCrypt is tested against published vectors from jBCrypt and Openwall, PBKDF2 against RFC 7914</td><td>In place</td></tr>
        <tr><td>External test suites and fuzzing</td><td>No JSONTestSuite, no differential testing against Jackson or Tomcat</td><td>Missing</td></tr>
        <tr><td>Critics from different model families</td><td>All agents are the same model family</td><td>Missing</td></tr>
        <tr><td>Human review of the security modules</td><td>Explicitly not done</td><td>Missing</td></tr>
      </tbody>
    </table></div>
  </section>

  <section class="section callout big">
    <p class="eyebrow">06 · Where it lands</p>
    <h2>The critique and the defence agree more than it seems</h2>
    <p>Both sides think the process is the most interesting part, that “no magic” is the right direction and that verification is the decisive question. The defence holds up best on maintenance, on why zero dependencies make the AI loop possible, and on PostgreSQL via <code>java.sql</code>. It holds up worst where it assumes things that don't exist yet: the differential testing and the critics from other model families are proposals, not reality. And the sovereignty is only real if someone at the maintaining organisation can actually read and understand the code.</p>
    <div class="rule">The zero-dependency rule applies to what is <em>shipped</em>, not to what <em>tests</em> it.</div>
    <p>That insight is why I think the critique's three proposals can be carried out without breaking anything:</p>
    <div class="flow">
      <div class="step"><b>1. External test suites</b><span>JSONTestSuite and known HTTP smuggling cases – just as BCrypt and PBKDF2 are already tested against published vectors. Tests the agent didn't make up itself.</span><span class="arrow">→</span></div>
      <div class="step"><b>2. Differential fuzzing</b><span>Millions of random inputs through both Spola and Jackson, Spola and Tomcat, in a separate test repository. Every divergence becomes a finding.</span><span class="arrow">→</span></div>
      <div class="step"><b>3. Another model</b><span>At least one critic from a different model family, so the blind spots don't overlap.</span><span class="arrow">→</span></div>
      <div class="step"><b>4. A human</b><span>Someone who reads the security modules before anything with real user credentials touches them.</span></div>
    </div>
  </section>

  <section class="section">
    <p class="eyebrow">07 · Where I've got to so far</p>
    <h2>Maybe the test bench is the product</h2>
    <p class="copy">I think the critique's most important sentence is this one: the most valuable thing to come out of all this is probably not Spola or Sola, but the experience of how far you can push AI-built code under strict rules. The frameworks are the test bench for that question.</p>
    <p class="copy">If it works, it shows something bigger than two frameworks – that one person with a disciplined AI process can own their entire stack, from HTTP parsing to signals in the browser, without a dependency tree. As a side effect there is a teaching resource: every module shows the Spring code and the Spola code side by side, making visible what Spring's magic actually does. But that is an “if”.</p>
    <div class="quote">Build the verification before the framework is used for anything that matters. With it in place, the project moves from interesting experiment to serious alternative. Without it, the critique's warning still stands.</div>
    <div class="note"><strong>This is a review I'd like to continue together with others – not a speech for the defence.</strong> I'm fully prepared for the critique to be more right than I'd like to believe. If you have maintained Spring systems in the public sector, written HTTP parsers or run AI agents against real code, I'd love to hear where you think the reasoning breaks down. The code is open on <a href="https://github.com/paokarlsson/spola">GitHub</a> – and if you find a request that slips past the parser, please open an issue.</div>
  </section>
