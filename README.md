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

Sajten ligger på `https://paokarlsson.github.io/tech-blogg/`. DNS för
`zero-duplications.com` pekar redan på GitHub Pages (apex → 185.199.108.153,
www → `paokarlsson.github.io`), men domänen är **inte** påslagen på GitHubs sida.

`src/CNAME` gör ingenting i dagsläget. Vid publicering via GitHub Actions läses
den filen inte för att konfigurera custom domain — den följer bara med som en
inert fil i bygget. Domänen måste sättas i repo-inställningarna.

Byt i den här ordningen, annars går sajten sönder:

1. **Settings → Pages → Custom domain** → `zero-duplications.com`, spara och
   vänta tills DNS-checken är grön. Kryssa i **Enforce HTTPS**.
2. Först därefter: ändra `url` i `src/_data/metadata.js` till
   `https://zero-duplications.com` och pusha.

Gör man steg 2 först blir `pathPrefix` `/` medan sajten fortfarande serveras
under `/tech-blogg/` — då 404:ar all CSS och alla bilder och sidan blir ostylad.
