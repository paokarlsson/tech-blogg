#!/usr/bin/env node
/**
 * Klipper ihop ett röstsatt avsnitt till en färdig fil:
 *
 *   intro → part-001 → cut → part-002 → cut → … → part-NNN → outro
 *
 *   node tools/klipp-ihop.js podd/audio/avsnitt-01-mindre-ramverk-mer-java
 *
 * Antalet delar läses ur katalogens manifest.json, så det följer manuset
 * automatiskt. Vilka sfx-filer som används står i podd/roster.json under
 * "klippning".
 *
 * Flaggor:
 *   --dry-run      skriver ut ffmpeg-kommandot utan att köra det
 *   --ut <fil>     utfil (default <katalog>/<slug>.mp3)
 *   --config <fil> rosterfil (default podd/roster.json)
 *
 * Varför concat-FILTRET och inte concat-demuxern med `-c copy`: dialogspåren
 * kommer från ElevenLabs (mp3_44100_128) men sfx-filerna från annat håll och
 * kan ha annan samplerate eller kanaluppsättning. `-c copy` skulle då ge en
 * fil som spelar upp fel efter första skarven. Filtret samplar om i stället,
 * till priset av en omkodning.
 */

const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");

function parseArgv(argv) {
  const flaggor = { dryRun: false, ut: null, config: null };
  const positionella = [];
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--dry-run") flaggor.dryRun = true;
    else if (a === "--ut") flaggor.ut = argv[++i];
    else if (a === "--config") flaggor.config = argv[++i];
    else positionella.push(a);
  }
  return { flaggor, positionella };
}

function main() {
  const { flaggor, positionella } = parseArgv(process.argv.slice(2));
  const katalog = positionella[0];
  if (!katalog) {
    console.error("Användning: node tools/klipp-ihop.js <ljudkatalog> [--dry-run] [--ut <fil>]");
    process.exit(1);
  }

  const rot = path.join(__dirname, "..");
  const roster = JSON.parse(fs.readFileSync(flaggor.config || path.join(rot, "podd", "roster.json"), "utf8"));
  const klipp = roster.klippning || {};
  const manifest = JSON.parse(fs.readFileSync(path.join(katalog, "manifest.json"), "utf8"));

  const sfx = (nyckel) => (klipp[nyckel] ? path.join(rot, "podd", klipp[nyckel]) : null);
  const intro = sfx("intro");
  const cut = sfx("mellan_segment");
  const outro = sfx("outro");

  // Bygg spellistan. Saknas en sfx-fil hoppas den över i stället för att stoppa
  // klippningen — man ska kunna lyssna på ett avsnitt innan vinjetterna är klara.
  const spår = [];
  const saknade = [];
  const läggTill = (fil, etikett) => {
    if (!fil) return;
    if (!fs.existsSync(fil)) return saknade.push(etikett);
    spår.push({ fil, etikett });
  };

  läggTill(intro, "intro");
  manifest.requests.forEach((r, i) => {
    if (i > 0) läggTill(cut, "cut");
    const del = path.join(katalog, r.fil);
    if (!fs.existsSync(del)) {
      console.error(`Saknar ${r.fil} — kör rosta-podd.js först (eller --from ${r.nr} --to ${r.nr}).`);
      process.exit(1);
    }
    spår.push({ fil: del, etikett: `${r.fil} · ${r.segment || ""}` });
  });
  läggTill(outro, "outro");

  const slug = path.basename(katalog);
  const utfil = flaggor.ut || path.join(katalog, `${slug}.mp3`);

  console.log(`${spår.length} spår:`);
  spår.forEach((s, i) => console.log(`  ${String(i + 1).padStart(2)} ${s.etikett}`));
  if (saknade.length) console.log(`\n  ⚠ hoppar över (filen finns inte): ${saknade.join(", ")}`);

  const args = [];
  spår.forEach((s) => args.push("-i", s.fil));
  const kedja = spår.map((_, i) => `[${i}:a]`).join("");
  args.push(
    "-filter_complex", `${kedja}concat=n=${spår.length}:v=0:a=1[ut]`,
    "-map", "[ut]",
    "-c:a", "libmp3lame", "-b:a", "128k", "-ar", "44100", "-ac", "2",
    "-y", utfil
  );

  if (flaggor.dryRun) {
    console.log(`\nffmpeg ${args.map((a) => (/[ []/.test(a) ? `"${a}"` : a)).join(" ")}`);
    return;
  }

  console.log("\nkör ffmpeg…");
  const res = spawnSync("ffmpeg", ["-loglevel", "warning", ...args], { stdio: "inherit" });
  if (res.error && res.error.code === "ENOENT") {
    console.error("ffmpeg saknas. Installera med: sudo apt install -y ffmpeg");
    process.exit(1);
  }
  if (res.status !== 0) process.exit(res.status ?? 1);

  const kb = fs.statSync(utfil).size / 1024;
  console.log(`\nSkrev ${path.relative(process.cwd(), utfil)} (${(kb / 1024).toFixed(1)} MB)`);
}

main();
