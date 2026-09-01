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

Öppna `http://localhost:8080/`. Filändringar i `src/` reloadar automatiskt.
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

### Domän och bassökväg

`src/CNAME` är enda stället där sajtens adress bestäms. Den kopieras med i
bygget och är det som sätter GitHub Pages custom domain — och samma fil
härleder `metadata.url` och därmed `pathPrefix`:

| `src/CNAME`            | Sajten ligger på                          | `pathPrefix` |
| ---------------------- | ----------------------------------------- | ------------ |
| finns (egen domän)     | `https://<domänen>/`                      | `/`          |
| borttagen              | `https://paokarlsson.github.io/tech-blogg/` | `/tech-blogg/` |

Byt alltså domän genom att redigera eller ta bort `src/CNAME` — redigera
aldrig `url` i `src/_data/metadata.js` för hand. Går de två isär pekar alla
länkar, CSS och bilder på fel bassökväg och sajten blir ostylad med trasiga
bilder.
