#!/usr/bin/env node
/**
 * Genererar ljudeffekter/stingers till podden med ElevenLabs Sound Effects
 * (`/v1/sound-generation`) — samma konto och nyckel som Text to Dialogue,
 * men en annan endpoint: text-till-ljud för korta effekter, inte röst.
 *
 * Recepten (prompt, längd, hur hårt modellen ska hålla sig till texten)
 * ligger i podd/roster.json under "ljud_recept", nyckel = utfilens sökväg
 * relativt podd/. Det är samma fil som redan styr röstsättningen, så all
 * poddkonfig bor på ett ställe.
 *
 *   ELEVENLABS_API_KEY=<nyckel> node podd/tools/generera-sfx.js
 *   node --env-file=podd/.env podd/tools/generera-sfx.js
 *
 * Flaggor:
 *   --dry-run    visar vad som skulle genereras, gör inga anrop
 *   --force      regenererar även filer som redan finns
 *   --config <fil>   rosterfil (default podd/roster.json)
 *
 * Utan argument genereras alla recept som saknar fil. Ange ett eller flera
 * receptnamn (sökvägarna, t.ex. "sfx/forbehallsklockan.mp3") för att bara
 * göra dem.
 */

const fs = require("fs");
const path = require("path");

const API = "https://api.elevenlabs.io/v1/sound-generation";

function parseArgv(argv) {
  const flaggor = { dryRun: false, force: false, config: null };
  const namn = [];
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--dry-run") flaggor.dryRun = true;
    else if (a === "--force") flaggor.force = true;
    else if (a === "--config") flaggor.config = argv[++i];
    else namn.push(a);
  }
  return { flaggor, namn };
}

async function generera(recept, apiKey) {
  const kropp = { text: recept.text };
  if (recept.duration_seconds != null) kropp.duration_seconds = recept.duration_seconds;
  if (recept.prompt_influence != null) kropp.prompt_influence = recept.prompt_influence;

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
    if (svar.status < 500 && svar.status !== 429) break;
    const väntan = 2000 * 2 ** (försök - 1);
    console.warn(`    försök ${försök} misslyckades (${svar.status}), väntar ${väntan / 1000}s`);
    await new Promise((r) => setTimeout(r, väntan));
  }
  throw new Error(senasteFel);
}

async function main() {
  const { flaggor, namn } = parseArgv(process.argv.slice(2));
  const rot = path.join(__dirname, "..");
  const roster = JSON.parse(fs.readFileSync(flaggor.config || path.join(rot, "podd", "roster.json"), "utf8"));
  const alla = roster.ljud_recept || {};

  if (!Object.keys(alla).length) {
    console.error('Inga recept i "ljud_recept" i roster.json.');
    process.exit(1);
  }

  const välda = namn.length ? namn : Object.keys(alla);
  const okända = välda.filter((n) => !alla[n]);
  if (okända.length) {
    console.error(`Okänt receptnamn: ${okända.join(", ")}\nTillgängliga: ${Object.keys(alla).join(", ")}`);
    process.exit(1);
  }

  const apiKey = process.env.ELEVENLABS_API_KEY;
  const torrt = flaggor.dryRun || !apiKey;
  if (torrt) {
    console.log(`${apiKey ? "Torrkörning (--dry-run)" : "Ingen ELEVENLABS_API_KEY satt — torrkörning"}. Inget genererat.\n`);
  }

  for (const receptnamn of välda) {
    const recept = alla[receptnamn];
    const fil = path.join(rot, "podd", receptnamn);
    const finnsRedan = fs.existsSync(fil);

    console.log(`${receptnamn}`);
    console.log(`  "${recept.text}"`);
    console.log(`  ${recept.duration_seconds ?? "auto"}s · prompt_influence ${recept.prompt_influence ?? "default"}`);

    if (finnsRedan && !flaggor.force) {
      console.log("  finns redan — hoppar över (--force för att skriva över)\n");
      continue;
    }
    if (torrt) {
      console.log("");
      continue;
    }

    process.stdout.write("  genererar… ");
    const ljud = await generera(recept, apiKey);
    fs.mkdirSync(path.dirname(fil), { recursive: true });
    fs.writeFileSync(fil, ljud);
    console.log(`${(ljud.length / 1024).toFixed(0)} kB → ${path.relative(process.cwd(), fil)}\n`);
  }
}

main().catch((fel) => {
  console.error(`\n${fel.message}`);
  process.exit(1);
});
