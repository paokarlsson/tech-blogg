# tech-blogg

Statisk blogg byggd med [Eleventy](https://www.11ty.dev/) och publicerad till GitHub Pages.

## Skriv ett nytt inlägg

1. Skapa `src/posts/YYYY-MM-DD-slug.md` med front matter:

   ```yaml
   ---
   layout: post.njk
   title: "Rubrik"
   subtitle: "Underrubrik"
   eyebrow: "Kategori · Taggar"
   dek: "Ingress som visas i hero-sektionen."
   description: "Kort beskrivning för startsidan och RSS-feeden."
   date: 2026-09-01
   image: "/assets/images/mitt-inlagg-hero.webp"
   imageAlt: "Beskrivning av bilden"
   chips:
     - "Tagg 1"
     - "Tagg 2"
   ---
   ```

2. Skriv brödtexten som Markdown eller HTML. De delade komponentklasserna i
   `src/css/style.css` (`.callout`, `.flow`/`.step`, `.arch`, `.cards`, `.quote`,
   `.table-wrap`, `.metrics`, `.note` m.fl.) kan användas direkt som HTML för
   rikare layout — se `src/posts/2026-09-01-mindre-ramverk-mer-java.md` för exempel.
3. Lägg ev. bilder i `src/assets/images/`.

## Förhandsgranska lokalt

Utan Node installerat — via Docker Compose (kräver bara Docker):

```
docker compose up dev
```

Öppna `http://localhost:8080/tech-blogg/`. Filändringar i `src/` reloadar automatiskt.
Bygg produktionsversionen (till `_site/`) utan att starta dev-servern:

```
docker compose run --rm build
```

Med Node installerat lokalt går det förstås även direkt:

```
npm install
npm run serve
```

## Publicering

Push till `main` triggar `.github/workflows/deploy.yml`, som bygger sajten och
publicerar den till GitHub Pages automatiskt. Ingen manuell deploy behövs.

Se till att **Settings → Pages → Source** är satt till **GitHub Actions** i
repot första gången.

### Byta till zero-duplications.com

Sajten ligger på `https://paokarlsson.github.io/tech-blogg/`.

`src/CNAME` gör ingenting i dagsläget. Vid publicering via GitHub Actions läses
den filen inte för att konfigurera custom domain — den följer bara med som en
inert fil i bygget. Domänen måste sättas i repo-inställningarna.

#### 1. Komplettera DNS (görs hos DigitalOcean)

Domänen ligger på `ns1–ns3.digitalocean.com`. För en apex-domän kräver GitHub
**alla fyra** A-posterna — med bara några av dem avvisas domänen med
`NotServedByPagesError`:

| Namn  | Typ   | Värde |
| ----- | ----- | ----- |
| `@`   | A     | `185.199.108.153` |
| `@`   | A     | `185.199.109.153` |
| `@`   | A     | `185.199.110.153` |
| `@`   | A     | `185.199.111.153` |
| `www` | CNAME | `paokarlsson.github.io.` |

Valfritt men rekommenderat, för IPv6, är fyra AAAA-poster på `@`:
`2606:50c0:8000::153`, `2606:50c0:8001::153`, `2606:50c0:8002::153`,
`2606:50c0:8003::153`.

Kontrollera mot källan, inte mot din egen resolver:

```
dig +short zero-duplications.com A @ns1.digitalocean.com
```

Fyra rader = klart. Använd `dig`, inte `getent hosts` eller `nslookup` —
`getent` returnerar bara en av flera adresser och får en ofullständig
uppsättning att se komplett ut.

#### 2. Slå på domänen i GitHub

**Settings → Pages → Custom domain** → `zero-duplications.com`. Vänta tills
DNS-checken är grön, kryssa sedan i **Enforce HTTPS**.

#### 3. Först därefter: byt URL i koden

Ändra `url` i `src/_data/metadata.js` till `https://zero-duplications.com`
och pusha.

Ordningen spelar roll. Görs steg 3 först blir `pathPrefix` `/` medan sajten
fortfarande serveras under `/tech-blogg/` — då 404:ar all CSS och alla bilder
och sidan blir ostylad.
