---
layout: post.njk
translationKey: vad-kostar-noll-beroenden
title: "What do zero dependencies cost when code gets cheap?"
subtitle: "A follow-up to the idea of fewer frameworks – and an experiment that takes it too far"
eyebrow: "Java 25 · dependencies · AI · an idea in progress"
dek: "In an earlier post I wrote that JSON parsing and security were things I'd leave to the specialist libraries. Since then I've started building exactly that myself. This is an attempt to understand why, and whether it is wise or just stubborn."
description: "If AI makes writing code cheap, does the line for what we should own ourselves move? Some reasoning about zero dependencies, maintenance and verification – with two hobby projects as a test bench."
date: 2026-10-28
chips:
  - "Cheap code?"
  - "Expensive verification"
  - "Zero dependencies"
  - "Ownership over time"
---
  <p class="lead">In the post about fewer frameworks I landed on a fairly cautious conclusion: write plain Java where the semantics are your own, but let mature libraries handle JSON, security and anything else that carries hard edge cases. I still think that is reasonable advice. But I've started to wonder whether one of the premises behind it is changing. The question I want to reason about is: <strong>if writing code gets cheap, does the line for what we should own ourselves move?</strong></p>

  <section class="section">
    <div class="copy">
      <p class="eyebrow">01 · The thought</p>
      <h2>Maybe the arithmetic behind dependencies has changed</h2>
      <p>For a long time, writing code has been expensive and adding a dependency has been cheap. The whole open-source economy rests on that arithmetic, and it has served us well. Why write an HTTP parser when thousands of others have already done it better?</p>
      <p>With AI, the first part of that equation gets much cheaper. That doesn't mean the code becomes good on its own. My sense is rather that the cost moves: from <em>writing</em> the code to <em>knowing that it is right</em>.</p>
      <p>If that's true, the question is no longer “can we be bothered to build this?” but “can we verify this, and carry it over time?”. That is a different question, with different answers.</p>
      <div class="quote">When code gets cheap to write, perhaps it gets expensive to trust instead.</div>
    </div>
  </section>

  <section class="section">
    <p class="eyebrow">02 · The experiment</p>
    <h2>Two hobby projects that take the idea too far</h2>
    <p class="copy">To test the thought, I've done what I advised against in the previous post. <a href="https://github.com/paokarlsson/spola">Spola</a> is a Java 25 web framework that does what a web API needs from Spring Boot and Lombok – HTTP server, routing, JSON, validation, configuration and security – without annotation magic and without a single dependency outside the JDK. <a href="https://github.com/paokarlsson/sola">Sola</a> is meant to become its counterpart in the browser: signals, templates and routing on top of the web platform's own APIs, with no dependencies and no build step. Spola has come a fair way. Sola has only just started.</p>
    <p class="copy">The code is mostly written by AI under strict rules, and both frameworks only grow when a real app needs something. You don't invent a framework, you extract it when the same solution gets written a second time.</p>
    <div class="note"><strong>These are experiments, not products.</strong> Spola is version 0.x, not ready for production, and the security parts have not been reviewed by a human. I use the projects as a test bench for the question above, not as a suggestion for what anyone else should run.</div>
  </section>

  <section class="section">
    <p class="eyebrow">03 · What you might gain</p>
    <h2>Maybe zero dependencies is more about maintenance than security</h2>
    <div class="copy">
      <p>Anyone who has maintained a Spring system knows the big cost is rarely the individual security holes. It is the churn: the move from <code>javax</code> to <code>jakarta</code>, Log4Shell forcing emergency patching over Christmas, and the steady stream of upgrades someone has to test. A stack made only of the JDK and browser standards could have a very long lifespan. Java is extremely backwards compatible, and the web has a principle of not breaking existing pages.</p>
      <p>There is also a thought about attack surface. Many of the most serious vulnerabilities in JSON libraries have involved polymorphic deserialization, which is reflection magic. Explicit mapping to records removes that whole class of bugs. And an HTTP parser can be made an uninteresting target by being strict: anything ambiguous gets a 400 instead of an interpretation. Request smuggling happens when two parsers interpret the same ambiguity differently. A parser that refuses to interpret closes that door.</p>
      <p><strong>So by zero dependencies I don't mean that your own code is safer.</strong> Rather that it can be easier to own – if it is kept small, strict and readable.</p>
    </div>
    <div class="metrics">
      <div class="metric"><strong>Lifespan</strong><span>No forced migration when a library changes direction.</span></div>
      <div class="metric"><strong>Readability</strong><span>Everything that affects a behaviour can be followed in the code.</span></div>
      <div class="metric"><strong>Attack surface</strong><span>Strict parsing and no reflection instead of interpretation.</span></div>
      <div class="metric"><strong>Ownership</strong><span>No vendors, no licensing questions, one line in the bill of materials.</span></div>
    </div>
  </section>

  <section class="section">
    <p class="eyebrow">04 · What I can't quite answer</p>
    <h2>Not everything holds up equally well</h2>
    <p class="copy">I've tried to be as hard on the idea as I would be if someone else showed it to me. Some objections I think can be handled. Others I'm not at all sure about.</p>
    <div class="cards">
      <div class="card"><span class="tag remove">My biggest doubt</span><h3>The risk may just move</h3><p>Jackson, Tomcat and Spring Security have been attacked by the whole world for fifteen years. Your own code hasn't. You may be trading supply-chain risk for code-quality risk, and the latter could well be larger.</p></div>
      <div class="card"><span class="tag remove">Worth taking seriously</span><h3>Green tests don't prove much</h3><p>When the same tool writes both the code and the tests, a green build means the code does what the tests say. Not necessarily that it is correct.</p></div>
      <div class="card"><span class="tag assess">Depends on what you want</span><h3>No magic doesn't require zero dependencies</h3><p>Javalin and Helidon SE already give you explicit wiring without annotations, with few and well-established dependencies. If all you want is to get rid of the magic, there are cheaper routes.</p></div>
      <div class="card"><span class="tag keep">Maybe solvable</span><h3>PostgreSQL</h3><p>JDBC is in the JDK but the driver isn't. A data layer can, however, be built on <code>java.sql</code> and let the app pick a driver at its own edge. The framework then stays free of dependencies.</p></div>
      <div class="card"><span class="tag remove">Here I'd be careful</span><h3>Cryptography</h3><p>Password hashing can be built on the JDK's primitives and tested against official test vectors. But JWT and the like mean more homegrown crypto handling, and there I'm less comfortable.</p></div>
      <div class="card"><span class="tag assess">Depends on the organisation</span><h3>The public sector</h3><p>There you often want boring technology that many people know and that can be procured. At the same time, the problem there is often systems that can't afford to keep up with frameworks' upgrade pace. I don't know which weighs more.</p></div>
    </div>
  </section>

  <section class="section callout big">
    <p class="eyebrow">05 · A suggested order</p>
    <h2>What if we verified in this order?</h2>
    <p class="copy">If the cost really moves to verification, that's where the work should go. I've started thinking in four steps. The further right, the more independent the check. The order isn't a truth – mostly a way to make the choice deliberate.</p>
    <div class="flow">
      <div class="step"><b>1. Be strict</b><span>Refuse to interpret what is ambiguous. A clear error is easier to trust than a generous guess.</span><span class="arrow">→</span></div>
      <div class="step"><b>2. Test against someone else's answers</b><span>Official test vectors, JSONTestSuite and known HTTP smuggling cases. Tests nobody in the project made up.</span><span class="arrow">→</span></div>
      <div class="step"><b>3. Compare against the reference</b><span>Random input through both your own parser and Jackson or Tomcat. Every divergence becomes a finding to understand.</span><span class="arrow">→</span></div>
      <div class="step"><b>4. Have a human read it</b><span>Before anything with real user credentials touches the security code, someone needs to have actually read it.</span></div>
    </div>
  </section>

  <section class="section">
    <p class="eyebrow">06 · What would we gain?</p>
    <h2>If it holds, it's about ownership over time</h2>
    <p class="copy">What would make the idea worth something isn't an empty dependency tree in itself. It's whether a system can live for many years without forced migrations, and whether whoever maintains it can actually understand what it does. And that is of course an assumption that needs testing.</p>
    <div class="table-wrap"><table>
      <thead><tr><th>If we own more ourselves…</th><th>We might get…</th><th>But only if…</th></tr></thead>
      <tbody>
        <tr><td>The HTTP parser</td><td>Fewer security feeds to follow and no forced upgrades</td><td>It is strict and tested against other people's test cases</td></tr>
        <tr><td>JSON handling</td><td>No polymorphic deserialization and visible mapping</td><td>The parser is compared against a reference at scale</td></tr>
        <tr><td>Security</td><td>Full insight into how login and sessions work</td><td>A human has read and understood the code</td></tr>
        <tr><td>A frontend without a build step</td><td>No dependencies to update and no framework migrations</td><td>The framework is extracted from a real app, not guessed at</td></tr>
      </tbody>
    </table></div>
  </section>

  <section class="section callout big">
    <p class="eyebrow">07 · Something that may have changed</p>
    <h2>Maybe the rule should only apply to what ships</h2>
    <p>For a long time I thought of zero dependencies as all or nothing. But maybe it isn't. What runs in production can be free of dependencies, while what tests the code is welcome to use Jackson, Tomcat and anything else as a reference.</p>
    <p>Then the mature libraries aren't something you build on, but something you measure yourself against. That feels like a more reasonable way to make use of fifteen years of experience than either inheriting it wholesale or ignoring it.</p>
    <div class="rule">What <em>ships</em> can be free of dependencies. What <em>tests</em> it doesn't have to be.</div>
  </section>

  <section class="section">
    <p class="eyebrow">08 · Where I've got to so far</p>
    <h2>Maybe the experiment matters more than the frameworks</h2>
    <p class="copy">I see no point in making zero dependencies a creed. The advice from the previous post stands for most systems: let the specialist libraries handle what is hard. What I'm curious about is whether the line for what counts as hard moves when code gets cheap – and what verification then has to cost for it to be worth it.</p>
    <p class="copy">If it works, it might show something bigger than two frameworks: that you can own your whole stack, from HTTP parsing to signals in the browser, without carrying a dependency tree. If it doesn't, I'll at least have learned where the line is, and why the mature libraries exist.</p>
    <div class="quote">Build the verification before the code is used for anything that matters. With it in place, your own code can become a serious alternative. Without it, it's still an experiment.</div>
    <div class="note"><strong>This is an experiment I'd like to keep thinking about together with others – not a recipe.</strong> I'm fully prepared for the idea to hold up worse in reality than on paper, and for the objections above to weigh more than I'd like to believe. The question I find interesting isn't “can we do without dependencies?”, but “what do we need to be able to verify in order to dare own more ourselves?”. If you have experiences that point in another direction, I'd love to hear them.</div>
  </section>
