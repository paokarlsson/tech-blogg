#!/usr/bin/env node
/**
 * Genererar ett poddmanus-underlag ur ett blogginlägg.
 *
 *   node podd/tools/generera-podd.js src/sv/posts/2026-09-01-mindre-ramverk-mer-java.md
 *
 * Skriver två filer till podd/:
 *   <slug>.plan.json    strukturerad segmentplan med källcitat och rollanvisningar
 *   <slug>.prompt.md    färdig prompt att mata en LLM med
 *
 * Formatet beskrivs i podd/KONCEPT.md. Inga externa beroenden — poängen med
 * inlägget vore lite förlorad annars.
 */

const fs = require("fs");
const path = require("path");

const VARDAR = {
  bosse: { namn: "Bosse Boot", roll: "ramverksmaximalist" },
  vera: { namn: "Vera Void", roll: "JDK-purist" }
};

// --- Parsning ---------------------------------------------------------------

function delaFrontMatter(rå) {
  const träff = rå.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/);
  if (!träff) throw new Error("Inlägget saknar front matter.");
  return { frontMatter: parseFrontMatter(träff[1]), kropp: träff[2] };
}

/** Minimal YAML — räcker för front mattern som README.md dokumenterar. */
function parseFrontMatter(text) {
  const ut = {};
  let listnyckel = null;
  for (const rad of text.split(/\r?\n/)) {
    const list = rad.match(/^\s+-\s+(.*)$/);
    if (list && listnyckel) {
      ut[listnyckel].push(avcitera(list[1]));
      continue;
    }
    const par = rad.match(/^([A-Za-z0-9_]+):\s*(.*)$/);
    if (!par) continue;
    const [, nyckel, värde] = par;
    if (värde === "") {
      listnyckel = nyckel;
      ut[nyckel] = [];
    } else {
      listnyckel = null;
      ut[nyckel] = avcitera(värde);
    }
  }
  return ut;
}

const avcitera = (s) => s.trim().replace(/^["'](.*)["']$/, "$1");

const textAv = (html) =>
  html
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/\s+/g, " ")
    .trim();

function alla(regex, html) {
  return [...html.matchAll(regex)];
}

/** Plockar ut varje <section> som ett segment med sina beståndsdelar. */
function extraheraSegment(kropp) {
  const sektioner = alla(/<section\b[^>]*>([\s\S]*?)<\/section>/g, kropp).map((m) => m[1]);

  return sektioner.map((html, i) => {
    const eyebrow = textAv((html.match(/<p class="eyebrow">([\s\S]*?)<\/p>/) || [, ""])[1]);
    const rubrik = textAv((html.match(/<h2>([\s\S]*?)<\/h2>/) || [, ""])[1]);

    const [, nummer = String(i + 1).padStart(2, "0"), tema = eyebrow] =
      eyebrow.match(/^(\d+)\s*·\s*(.*)$/) || [];

    const stycken = alla(/<p(?![^>]*class="eyebrow")[^>]*>([\s\S]*?)<\/p>/g, html)
      .map((m) => textAv(m[1]))
      .filter((t) => t.length > 40);

    const citat = alla(/<div class="quote">([\s\S]*?)<\/div>/g, html).map((m) => textAv(m[1]));
    const regel = alla(/<div class="rule">([\s\S]*?)<\/div>/g, html).map((m) => textAv(m[1]));
    const noteringar = alla(/<div class="note">([\s\S]*?)<\/div>/g, html).map((m) => textAv(m[1]));

    const kort = alla(/<div class="card">([\s\S]*?)<\/div>\s*(?=<div class="card">|$)/g, html).map((m) => {
      const bit = m[1];
      return {
        hållning: (bit.match(/<span class="tag (\w+)">/) || [, "assess"])[1],
        etikett: textAv((bit.match(/<span class="tag \w+">([\s\S]*?)<\/span>/) || [, ""])[1]),
        ämne: textAv((bit.match(/<h3>([\s\S]*?)<\/h3>/) || [, ""])[1]),
        motivering: textAv((bit.match(/<p>([\s\S]*?)<\/p>/) || [, ""])[1])
      };
    });

    const steg = alla(/<div class="step">([\s\S]*?)<\/div>/g, html).map((m) => ({
      fråga: textAv((m[1].match(/<b>([\s\S]*?)<\/b>/) || [, ""])[1]),
      förklaring: textAv((m[1].match(/<span>([\s\S]*?)<\/span>/) || [, ""])[1])
    }));

    const mätetal = alla(/<div class="metric">([\s\S]*?)<\/div>/g, html).map((m) => ({
      namn: textAv((m[1].match(/<strong>([\s\S]*?)<\/strong>/) || [, ""])[1]),
      innebörd: textAv((m[1].match(/<span>([\s\S]*?)<\/span>/) || [, ""])[1])
    }));

    const tabellrader = alla(/<tbody>([\s\S]*?)<\/tbody>/g, html).flatMap((tb) =>
      alla(/<tr>([\s\S]*?)<\/tr>/g, tb[1]).map((tr) => {
        const celler = alla(/<td>([\s\S]*?)<\/td>/g, tr[1]).map((td) => textAv(td[1]));
        return { om: celler[0], då: celler[1], förbehåll: celler[2] };
      })
    );

    const noder = alla(/<div class="arch-node[^"]*">([\s\S]*?)<\/div>\s*<\/div>/g, html).map((m) => ({
      lager: textAv((m[1].match(/<div class="arch-label">([\s\S]*?)<\/div>/) || [, ""])[1]),
      rubrik: textAv((m[1].match(/<div class="arch-title">([\s\S]*?)<\/div>/) || [, ""])[1])
    }));

    return {
      nummer,
      tema,
      tes: rubrik,
      källtext: stycken,
      ankare: [...citat, ...regel],
      noteringar,
      kort,
      steg,
      mätetal,
      tabellrader,
      arkitektur: noder
    };
  });
}

// --- Regelmotor -------------------------------------------------------------

/** HTML-strukturen avgör konfliktformen. Se KONCEPT.md §5. */
function väljKonfliktform(seg) {
  if (seg.kort.length) return "snabbrunda";
  if (seg.steg.length) return "trappan";
  if (seg.tabellrader.length) return "villkorsklockan";
  if (seg.mätetal.length) return "isberget";
  if (seg.arkitektur.length) return "ritningen";
  return "duell";
}

const FORMBESKRIVNING = {
  snabbrunda:
    "Snabbrunda. Ett kort i taget, max fyra repliker per kort. Taggen delar ut segern: " +
    "`remove` → Vera, `keep` → Bosse, `assess` → gräl som Förbehållsklockan avbryter.",
  trappan:
    "Trappan. Kör stegen som frågesport — lyssnaren ska hinna gissa före panelen. " +
    "Bosse svarar alltid 4. Vera svarar alltid 1. Rätt svar ligger nästan alltid däremellan.",
  villkorsklockan:
    "Villkorsklockan. Läs raderna som löften, och låt klockan ringa på sista kolumnen. " +
    "Ingen får komma undan ett 'om vi minskar X får vi Y' utan sitt 'men bara om'.",
  isberget:
    "Isberget. Vera läser posterna som en dödsruna, Bosse avfärdar dem som 'bara transitivt'. " +
    "Titanic-stråkarna spelas exakt en gång, inte två.",
  ritningen:
    "Ritningen. Beskriv arkitekturen i ljud — lagren måste gå att höra utan bild. " +
    "Båda tror att diagrammet bevisar deras sak. Ingen av dem har fel om sitt eget lager.",
  duell: "Duell. Fri dialog kring tesen. Öppna i oenighet, stäng på inläggets eget förbehåll."
};

/** Regel 2 i KONCEPT.md: ingen vinner två segment i rad. */
function fördelaSegrar(segment) {
  let förra = null;
  return segment.map((seg, i) => {
    let vinnare;
    if (seg.kort.length) {
      const keep = seg.kort.filter((k) => k.hållning === "keep").length;
      const remove = seg.kort.filter((k) => k.hållning === "remove").length;
      vinnare = keep === remove ? "delad" : keep > remove ? "bosse" : "vera";
    } else {
      vinnare = i % 2 === 0 ? "vera" : "bosse";
    }
    if (vinnare === förra) vinnare = vinnare === "vera" ? "bosse" : "vera";
    förra = vinnare === "delad" ? null : vinnare;
    return vinnare;
  });
}

// --- Utskrift ---------------------------------------------------------------

function byggPlan(frontMatter, segment) {
  const segrar = fördelaSegrar(segment);
  const ordbudget = Math.round(150 * 24 / segment.length); // ~24 min i 150 ord/min

  return {
    källa: frontMatter.title,
    slug: frontMatter.translationKey,
    ingress: frontMatter.dek,
    värdar: VARDAR,
    regler: [
      "Fakta får bara komma ur källtexten. Skämt får hittas på fritt.",
      "Varje faktapåstående får en 'källa:'-rad tillbaka till en mening i inlägget.",
      "Absurditeten sitter i personerna, aldrig i tekniken — Java-fakta ska vara korrekt även i en dum replik.",
      "Ankarcitaten sägs ordagrant, utan skämt, med två sekunders tystnad före och efter.",
      "Ingen vinner två segment i rad."
    ],
    segment: segment.map((seg, i) => ({
      ...seg,
      konfliktform: väljKonfliktform(seg),
      regi: FORMBESKRIVNING[väljKonfliktform(seg)],
      vinnare: segrar[i],
      ordbudget
    }))
  };
}

function byggPrompt(plan) {
  const rader = [];
  rader.push(`# Skriv poddmanus: "Beroendeframkallande" — ${plan.källa}`);
  rader.push("");
  rader.push(`Ingress ur inlägget: *${plan.ingress}*`);
  rader.push("");
  rader.push("## Värdar");
  rader.push(
    "- **Bosse Boot** (ramverksmaximalist). Svarar allt med 'det finns en starter för det'. " +
      "Har rätt om JSON, OAuth/OIDC, connection pools och telemetry. Har fel om räckvidden på sin egen reflex."
  );
  rader.push(
    "- **Vera Void** (JDK-purist). Citerar release notes som poesi. Har rätt om vad JDK:n redan ger. " +
      "Har fel om att systemets storlek mäts i JAR-filer."
  );
  rader.push(
    "- **Förbehållsklockan** 🔔 — inte en person, en klocka. Ringer när någon drar en slutsats utan sitt villkor."
  );
  rader.push("");
  rader.push("## Hårda regler");
  plan.regler.forEach((r) => rader.push(`- ${r}`));
  rader.push("");
  rader.push("## Format");
  rader.push("`**NAMN:** replik` per rad. Regianvisningar i *kursiv* på egen rad. Ankarcitat i blockquote.");
  rader.push("");
  rader.push("## Segment");

  for (const seg of plan.segment) {
    rader.push("");
    rader.push(`### ${seg.nummer} · ${seg.tema} — ca ${seg.ordbudget} ord`);
    rader.push(`**Tes:** ${seg.tes}`);
    rader.push(`**Konfliktform:** ${seg.regi}`);
    rader.push(`**Segmentet vinns av:** ${seg.vinnare}`);
    if (seg.ankare.length) {
      rader.push("**Ankare (sägs ordagrant):**");
      seg.ankare.forEach((a) => rader.push(`> ${a}`));
    }
    if (seg.kort.length) {
      rader.push("**Kort:**");
      seg.kort.forEach((k) => rader.push(`- \`${k.hållning}\` **${k.ämne}** — ${k.motivering}`));
    }
    if (seg.steg.length) {
      rader.push("**Steg:**");
      seg.steg.forEach((s, i) => rader.push(`- ${i + 1}. ${s.fråga} ${s.förklaring}`));
    }
    if (seg.mätetal.length) {
      rader.push("**Poster:**");
      seg.mätetal.forEach((m) => rader.push(`- **${m.namn}** — ${m.innebörd}`));
    }
    if (seg.tabellrader.length) {
      rader.push("**Löfte → villkor (klockan ringer på sista ledet):**");
      seg.tabellrader.forEach((r) => rader.push(`- Minska *${r.om}* → *${r.då}* — men bara om *${r.förbehåll}*`));
    }
    if (seg.arkitektur.length) {
      rader.push("**Lager:**");
      seg.arkitektur.forEach((n) => rader.push(`- ${n.lager}: ${n.rubrik}`));
    }
    if (seg.källtext.length) {
      rader.push("**Faktaunderlag (enda tillåtna källan för tekniska påståenden):**");
      seg.källtext.forEach((t) => rader.push(`- ${t}`));
    }
    if (seg.noteringar.length) {
      seg.noteringar.forEach((n) => rader.push(`**Obs:** ${n}`));
    }
  }

  rader.push("");
  rader.push("## Slutvinjett");
  rader.push('Bosse och Vera säger unisont "det fungerar på min maskin". Det är osant för minst en av dem.');
  rader.push("");
  return rader.join("\n");
}

// --- Main -------------------------------------------------------------------

function main() {
  const inl = process.argv[2];
  if (!inl) {
    console.error("Användning: node podd/tools/generera-podd.js <sökväg till inlägg.md>");
    process.exit(1);
  }

  const rå = fs.readFileSync(inl, "utf8");
  const { frontMatter, kropp } = delaFrontMatter(rå);
  const segment = extraheraSegment(kropp);

  if (!segment.length) {
    console.error(`Hittade inga <section>-block i ${inl}. Manusgeneratorn behöver inläggets sektionsstruktur.`);
    process.exit(1);
  }

  const plan = byggPlan(frontMatter, segment);
  const slug = frontMatter.translationKey || path.basename(inl, ".md");
  const utkatalog = path.join(__dirname, "..", "podd");
  fs.mkdirSync(utkatalog, { recursive: true });

  const planFil = path.join(utkatalog, `${slug}.plan.json`);
  const promptFil = path.join(utkatalog, `${slug}.prompt.md`);
  fs.writeFileSync(planFil, JSON.stringify(plan, null, 2) + "\n");
  fs.writeFileSync(promptFil, byggPrompt(plan));

  console.log(`${segment.length} segment ur "${plan.källa}"`);
  for (const seg of plan.segment) {
    console.log(`  ${seg.nummer} ${seg.tema.padEnd(34)} ${seg.konfliktform.padEnd(16)} vinnare: ${seg.vinnare}`);
  }
  console.log(`\nSkrev ${path.relative(process.cwd(), planFil)}`);
  console.log(`Skrev ${path.relative(process.cwd(), promptFil)}`);
}

main();
