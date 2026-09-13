#!/usr/bin/env node
/**
 * Röstsätter ett poddmanus med ElevenLabs Text to Dialogue (eleven_v3).
 *
 *   ROST_BOSSE=<voice_id> ROST_VERA=<voice_id> ELEVENLABS_API_KEY=<nyckel> \
 *     node podd/tools/rosta-podd.js podd/avsnitt-01-mindre-ramverk-mer-java.md
 *
 * Utan API-nyckel körs en torrkörning: manuset parsas, delas i requests och
 * planen skrivs ut — men inget anrop görs. Bra för att se teckenbudgeten innan
 * man bränner kvot.
 *
 * Flaggor:
 *   --dry-run          torrkörning även med nyckel satt
 *   --ut <katalog>     utkatalog (default podd/audio/<slug>)
 *   --config <fil>     rosterfil (default podd/roster.json)
 *   --from <n> --to <n>  rendera bara ett spann av requests (för omtagningar)
 *
 * Gränser som styr chunkningen (se podd/ROSTNING.md):
 *   - Text to Dialogue: håll summan av alla inputs[].text ≤ 2 000 tecken/request.
 *   - Max 10 unika voice_id per request. Vi använder 2.
 *   - Request stitching (previous_request_ids) stöds INTE av eleven_v3, så
 *     skarvarna måste läggas där ett avbrott ändå låter naturligt.
 *   - Audiotaggar som [skratt] är vanlig text och räknas mot budgeten.
 */

const fs = require("fs");
const path = require("path");

const API = "https://api.elevenlabs.io/v1/text-to-dialogue";

// --- Argument ---------------------------------------------------------------

function parseArgv(argv) {
  const flaggor = { dryRun: false, ut: null, config: null, from: 1, to: Infinity };
  const positionella = [];
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--dry-run") flaggor.dryRun = true;
    else if (a === "--ut") flaggor.ut = argv[++i];
    else if (a === "--config") flaggor.config = argv[++i];
    else if (a === "--from") flaggor.from = Number(argv[++i]);
    else if (a === "--to") flaggor.to = Number(argv[++i]);
    else positionella.push(a);
  }
  return { flaggor, positionella };
}

// --- Manusparsning ----------------------------------------------------------

/**
 * Läser manuset till en sekvens av repliker och cue:er.
 *   { typ: "replik", talare, text }
 *   { typ: "cue", sort: "regi" | "sfx" | "unison", text }
 *   { typ: "brytpunkt", text }   ← segmentrubrik, naturlig skarv
 */
function parsaManus(md, roster) {
  const poster = [];
  const talarnamn = new Set(Object.keys(roster.roster));
  const unison = new Set(Object.keys(roster.unison || {}));
  const sfxTecken = Object.keys(roster.ljudeffekter || {});

  let iTabell = false;

  for (const råRad of md.split(/\r?\n/)) {
    const rad = råRad.trim();
    if (!rad) continue;

    // Tabeller och metadata i manuset ska inte läsas upp.
    if (rad.startsWith("|")) { iTabell = true; continue; }
    if (iTabell && !rad.startsWith("|")) iTabell = false;
    if (rad === "---" || rad.startsWith("**Källa:**") || rad.startsWith("**Längd:**") ||
        rad.startsWith("**Medverkande:**") || rad.startsWith("**Genererat")) continue;

    // Segmentrubrik = naturlig skarv mellan requests.
    if (/^#{2,3}\s/.test(rad)) {
      poster.push({ typ: "brytpunkt", text: rad.replace(/^#+\s*/, "").replace(/\s*—\s*\*.*\*$/, "").trim() });
      continue;
    }
    if (rad.startsWith("#") || rad.startsWith(">") === false && rad.startsWith("*Referensmanus")) continue;

    // Ren ljudeffekt på egen rad.
    const sfx = sfxTecken.find((t) => rad.startsWith(t));
    if (sfx && rad.replace(sfx, "").replace(/[*_\s]/g, "").length < 40) {
      poster.push({ typ: "cue", sort: "sfx", tecken: sfx, text: rad });
      continue;
    }

    // Regianvisning: hel rad i kursiv. Källhänvisningar är manusmetadata, inte regi.
    if (/^\*[^*].*\*$/.test(rad)) {
      const text = rad.replace(/^\*|\*$/g, "");
      if (/^Källa:/.test(text)) continue;
      const iRegi = sfxTecken.find((t) => text.includes(t));
      poster.push({ typ: "cue", sort: iRegi ? "sfx" : "regi", tecken: iRegi, text });
      continue;
    }

    // Ankarcitat hör till föregående talare.
    if (rad.startsWith(">")) {
      const citat = rad.replace(/^>\s?/, "").trim();
      const senaste = [...poster].reverse().find((p) => p.typ === "replik");
      if (senaste && citat) senaste.text += (senaste.text ? " " : "") + citat;
      continue;
    }

    // Replik: **NAMN:** text
    const replik = rad.match(/^\*\*([^:*]+):\*\*\s*(.*)$/);
    if (replik) {
      const namn = replik[1].trim().toUpperCase();
      const text = städaReplik(replik[2]);
      if (!text) continue;
      if (unison.has(namn)) {
        poster.push({ typ: "cue", sort: "unison", talare: namn, text });
        continue;
      }
      if (!talarnamn.has(namn)) {
        console.warn(`  ⚠ okänd talare "${namn}" — hoppar över: ${text.slice(0, 50)}…`);
        continue;
      }
      poster.push({ typ: "replik", talare: namn, text });
      continue;
    }

    // Fortsättningsrad på föregående replik.
    const senaste = poster[poster.length - 1];
    if (senaste && senaste.typ === "replik" && !rad.startsWith("**")) {
      const extra = städaReplik(rad);
      if (extra) senaste.text += " " + extra;
    }
  }

  return poster;
}

/**
 * Regianvisningar i löpande text — *(torrt)* — ska inte läsas upp.
 * Kända anvisningar blir audiotaggar i stället; resten faller bort.
 * Audiotaggar är vanlig text för modellen och räknas mot teckenbudgeten.
 *
 * eleven_v3 validerar inte taggarna — de är vanlig text i inputen, så en
 * påhittad tagg ger inget API-fel. Den däremot risken är att modellen
 * ignorerar den eller läser upp den högt.
 *
 * Därför skickar vi ENGELSKA taggar. Alla taggar ElevenLabs dokumenterar är
 * engelska ([laughs], [whispers], [curious], [thoughtful], [sighs],
 * [sarcastic], [short pause] …) och det finns inget stöd i dokumentationen
 * för att svenska motsvarigheter tolkas. Manuset skrivs fortfarande på
 * svenska — *(torrt)* — och den här listan är översättningslagret.
 * Taggar markerade ✅ finns ordagrant i ElevenLabs dokumentation; övriga är
 * vanliga engelska känsloord av samma typ som de dokumenterade.
 */
const TAGGAR = [
  [/rakt,?\s*utan skämt/i, "[serious]"],
  [/dödsruna/i, "[solemn]"],
  [/paus/i, "[short pause]"], // ✅
  [/unisont/i, ""],
  [/långsamt/i, "[slowly]"],
  [/skratt/i, "[laughs]"], // ✅
  [/\btorrt\b/i, "[dryly]"],
  [/nyfiket/i, "[curious]"], // ✅
  [/tvekande|tveksamt/i, "[hesitant]"],
  [/fundersamt|tankfullt/i, "[thoughtful]"], // ✅
  [/\broad\b/i, "[chuckles]"], // ✅
  [/varmt/i, "[warm]"],
  [/sarkastiskt/i, "[sarcastic]"], // ✅
  [/skeptiskt/i, "[skeptical]"],
  [/suck(ar)?/i, "[sighs]"], // ✅
  [/viskar|viskande/i, "[whispers]"], // ✅
  [/uppgivet/i, "[resigned]"],
  [/bestämt/i, "[firm]"],
  [/surt|tjurig[t]?/i, "[annoyed]"],
  [/nöjt/i, "[pleased]"],
  [/motvilligt/i, "[reluctant]"],
  [/otåligt/i, "[impatient]"]
];

function städaReplik(text) {
  let ut = text.replace(/\*\(([^)]*)\)\*/g, (_, inne) => {
    const träff = TAGGAR.find(([re]) => re.test(inne));
    return träff ? träff[1] : "";
  });
  ut = ut.replace(/\*\*/g, "").replace(/(^|\s)\*(\S[^*]*)\*/g, "$1$2");
  return ut.replace(/\s+/g, " ").trim();
}

// --- Chunkning --------------------------------------------------------------

const längd = (turer) => turer.reduce((n, t) => n + t.text.length, 0);

/** Delar en för lång replik vid meningsgräns så budgeten håller. */
function delaReplik(tur, tak) {
  if (tur.text.length <= tak) return [tur];
  const meningar = tur.text.match(/[^.!?…]+[.!?…]*\s*/g) || [tur.text];
  const bitar = [];
  let buffert = "";
  for (const mening of meningar) {
    if (buffert && (buffert + mening).length > tak) {
      bitar.push({ ...tur, text: buffert.trim() });
      buffert = "";
    }
    // En enskild mening längre än taket klipps hårt — sällsynt, men får inte tappas.
    if (mening.length > tak) {
      for (let i = 0; i < mening.length; i += tak) {
        bitar.push({ ...tur, text: mening.slice(i, i + tak).trim() });
      }
      continue;
    }
    buffert += mening;
  }
  if (buffert.trim()) bitar.push({ ...tur, text: buffert.trim() });
  return bitar;
}

/**
 * Bygger requests under teckenbudgeten. Skarv läggs helst vid en brytpunkt
 * (segmentrubrik) eftersom eleven_v3 inte stöder request stitching — då blir
 * avbrottet ett medvetet andetag i stället för en hörbar söm mitt i en replik.
 *
 * Inom ett segment delas turerna jämnt i stället för att fyllas girigt: girig
 * fyllning lämnar en sista request på några tiotal tecken, och en ensam kort
 * replik utan sammanhang låter platt när modellen saknar omgivande dialog.
 */
function chunka(poster, roster) {
  const tak = Math.min(roster.max_tecken_per_request, roster.hard_gräns);
  const segment = [];
  let aktuellt = { namn: null, turer: [], cues: [] };

  for (const post of poster) {
    if (post.typ === "brytpunkt") {
      segment.push(aktuellt);
      aktuellt = { namn: post.text, turer: [], cues: [] };
      continue;
    }
    if (post.typ === "cue") {
      aktuellt.cues.push({ ...post, efterTur: aktuellt.turer.length });
      continue;
    }
    for (const bit of delaReplik(post, tak)) {
      aktuellt.turer.push({ voice_id: roster.roster[bit.talare].voice_id, talare: bit.talare, text: bit.text });
    }
  }
  segment.push(aktuellt);

  const requests = [];
  for (const seg of segment) {
    if (!seg.turer.length) continue;
    const totalt = längd(seg.turer);
    const delar = Math.max(1, Math.ceil(totalt / tak));
    const mål = totalt / delar;

    let del = { turer: [], segment: seg.namn };
    for (const tur of seg.turer) {
      // Stäng när målvikten passerats, men aldrig så att taket spräcks.
      if (del.turer.length && (längd(del.turer) >= mål || längd(del.turer) + tur.text.length > tak)) {
        requests.push(del);
        del = { turer: [], segment: seg.namn };
      }
      del.turer.push(tur);
    }
    if (del.turer.length) requests.push(del);

    // Cue:erna hör till segmentet — placera dem i den request deras turindex faller i.
    let förskjutning = 0;
    const delarISeg = requests.filter((r) => r.segment === seg.namn);
    for (const r of delarISeg) {
      r.cues = seg.cues.filter((c) => c.efterTur >= förskjutning && c.efterTur < förskjutning + r.turer.length)
        .map((c) => ({ ...c, efterTur: c.efterTur - förskjutning }));
      förskjutning += r.turer.length;
    }
    const sista = delarISeg[delarISeg.length - 1];
    if (sista) sista.cues.push(...seg.cues.filter((c) => c.efterTur >= förskjutning).map((c) => ({ ...c, efterTur: sista.turer.length })));
  }

  return requests.map((r, i) => ({ ...r, nr: i + 1, tecken: längd(r.turer), cues: r.cues || [] }));
}

// --- Roster -----------------------------------------------------------------

function läsRoster(fil) {
  const roster = JSON.parse(fs.readFileSync(fil, "utf8"));
  for (const [nyckel, r] of Object.entries(roster.roster)) {
    const frånEnv = r.env && process.env[r.env];
    if (frånEnv) r.voice_id = frånEnv.trim();
    if (!r.voice_id) {
      throw new Error(
        `Saknar voice_id för ${nyckel}. Sätt ${r.env} i miljön, eller fyll i "voice_id" i ${fil}.\n` +
          `Hämta id:n med: curl -H "xi-api-key: $ELEVENLABS_API_KEY" https://api.elevenlabs.io/v2/voices`
      );
    }
  }
  const unika = new Set(Object.values(roster.roster).map((r) => r.voice_id));
  if (unika.size > 10) throw new Error("Text to Dialogue tar max 10 unika voice_id per request.");
  if (unika.size !== Object.keys(roster.roster).length) {
    console.warn("  ⚠ två roller delar voice_id — de kommer låta likadant.");
  }
  return roster;
}

// --- API --------------------------------------------------------------------

async function generera(request, roster, apiKey) {
  const kropp = {
    inputs: request.turer.map((t) => ({ text: t.text, voice_id: t.voice_id })),
    model_id: roster.model_id,
    output_format: roster.output_format,
    settings: roster.dialogue_settings
  };
  if (roster.language_code) kropp.language_code = roster.language_code;
  if (roster.seed != null) kropp.seed = roster.seed;

  let senasteFel;
  for (let försök = 1; försök <= 4; försök++) {
    const svar = await fetch(API, {
      method: "POST",
      headers: { "xi-api-key": apiKey, "Content-Type": "application/json" },
      body: JSON.stringify(kropp)
    });
    if (svar.ok) return Buffer.from(await svar.arrayBuffer());

    const text = await svar.text().catch(() => "");
    senasteFel = `HTTP ${svar.status}: ${text.slice(0, 300)}`;
    // 4xx utom 429 är vårt fel — ingen idé att försöka igen.
    if (svar.status < 500 && svar.status !== 429) break;
    const väntan = 2000 * 2 ** (försök - 1);
    console.warn(`    försök ${försök} misslyckades (${svar.status}), väntar ${väntan / 1000}s`);
    await new Promise((r) => setTimeout(r, väntan));
  }
  throw new Error(senasteFel);
}

// --- Main -------------------------------------------------------------------

async function main() {
  const { flaggor, positionella } = parseArgv(process.argv.slice(2));
  const manusfil = positionella[0];
  if (!manusfil) {
    console.error("Användning: node podd/tools/rosta-podd.js <manus.md> [--dry-run] [--ut <katalog>]");
    process.exit(1);
  }

  const rot = path.join(__dirname, "..");
  const roster = läsRoster(flaggor.config || path.join(rot, "podd", "roster.json"));
  const poster = parsaManus(fs.readFileSync(manusfil, "utf8"), roster);
  const requests = chunka(poster, roster);

  const slug = path.basename(manusfil, ".md");
  const utkatalog = flaggor.ut || path.join(rot, "podd", "audio", slug);

  const repliker = poster.filter((p) => p.typ === "replik");
  const totalt = längd(repliker);
  console.log(`Manus: ${slug}`);
  console.log(`  ${repliker.length} repliker · ${totalt} tecken · ${requests.length} requests`);
  console.log(`  modell ${roster.model_id} · budget ${roster.max_tecken_per_request}/${roster.hard_gräns} tecken\n`);

  let varning = false;
  for (const r of requests) {
    const spärr = r.tecken > roster.hard_gräns ? " ❌ ÖVER HÅRD GRÄNS" : "";
    if (spärr) varning = true;
    const röster = [...new Set(r.turer.map((t) => t.talare))].join("+");
    console.log(
      `  #${String(r.nr).padStart(2, "0")} ${String(r.tecken).padStart(4)} tecken · ` +
        `${String(r.turer.length).padStart(2)} turer · ${röster.padEnd(11)} ${(r.segment || "").slice(0, 34)}${spärr}`
    );
  }
  if (varning) {
    console.error("\nEn request överskrider den hårda gränsen. Sänk max_tecken_per_request.");
    process.exit(1);
  }

  const cues = requests.flatMap((r) =>
    r.cues.map((c) => ({ request: r.nr, efterTur: c.efterTur, sort: c.sort, text: c.text }))
  );
  const unisonCues = cues.filter((c) => c.sort === "unison");
  if (unisonCues.length) {
    console.log(
      `\n  ⚠ ${unisonCues.length} unison-replik(er) kan inte genereras av Text to Dialogue.` +
        ` De ligger i manifestet och behöver läggas som två spår i mixen.`
    );
  }

  const apiKey = process.env.ELEVENLABS_API_KEY;
  const torrt = flaggor.dryRun || !apiKey;
  if (torrt) {
    console.log(`\n${apiKey ? "Torrkörning (--dry-run)" : "Ingen ELEVENLABS_API_KEY satt — torrkörning"}. Inget genererat.`);
  }

  fs.mkdirSync(utkatalog, { recursive: true });
  const manifest = {
    manus: path.relative(rot, manusfil),
    modell: roster.model_id,
    output_format: roster.output_format,
    seed: roster.seed,
    tecken_totalt: totalt,
    roster: Object.fromEntries(Object.entries(roster.roster).map(([k, v]) => [k, v.voice_id])),
    requests: requests.map((r) => ({
      nr: r.nr,
      fil: `part-${String(r.nr).padStart(3, "0")}.mp3`,
      segment: r.segment,
      tecken: r.tecken,
      turer: r.turer.map((t) => ({ talare: t.talare, text: t.text }))
    })),
    cues
  };
  fs.writeFileSync(path.join(utkatalog, "manifest.json"), JSON.stringify(manifest, null, 2) + "\n");

  if (!torrt) {
    console.log("");
    for (const r of requests) {
      if (r.nr < flaggor.from || r.nr > flaggor.to) continue;
      const fil = path.join(utkatalog, `part-${String(r.nr).padStart(3, "0")}.mp3`);
      process.stdout.write(`  genererar #${r.nr} (${r.tecken} tecken)… `);
      const ljud = await generera(r, roster, apiKey);
      fs.writeFileSync(fil, ljud);
      console.log(`${(ljud.length / 1024).toFixed(0)} kB`);
    }
    const lista = requests.map((r) => `file 'part-${String(r.nr).padStart(3, "0")}.mp3'`).join("\n");
    fs.writeFileSync(path.join(utkatalog, "concat.txt"), lista + "\n");
    console.log(`\n  ffmpeg -f concat -safe 0 -i concat.txt -c copy ${slug}.mp3`);
  }

  console.log(`\nSkrev ${path.relative(process.cwd(), path.join(utkatalog, "manifest.json"))}`);
}

main().catch((fel) => {
  console.error(`\n${fel.message}`);
  process.exit(1);
});
