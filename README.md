# tech-blogg

Statisk blogg byggd med [Eleventy](https://www.11ty.dev/) och publicerad till GitHub Pages.

## Språk

Sajten finns på svenska (`/sv/`) och engelska (`/en/`) med en språkväxlare i
navigationen. Roten `/` innehåller ingen egen sida — den avgör besökarens
webbläsarspråk med JavaScript och skickar vidare till `/sv/` eller `/en/`
(fallback är svenska).

## Skriv ett nytt inlägg

1. Skapa `src/sv/posts/YYYY-MM-DD-slug.md` med front matter:

   ```yaml
   ---
   layout: post.njk
   translationKey: mitt-inlagg
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
   rikare layout — se `src/sv/posts/2026-09-01-mindre-ramverk-mer-java.md` för exempel.
3. Lägg ev. bilder i `src/assets/images/`.
4. Skriv en engelsk översättning i `src/en/posts/YYYY-MM-DD-slug.md` med
   **samma `translationKey`** som den svenska filen (annars hittar inte
   språkväxlaren tillbaka till rätt inlägg). Saknas översättningen tillfälligt
   kan `src/en/posts/` lämnas utan den filen — språkväxlaren faller då tillbaka
   till startsidan på engelska.

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

Sajten ligger på `https://zero-duplications.com/`, med custom domain påslagen
under **Settings → Pages**. Eftersom den serveras från domänens rot är
`pathPrefix` `/`, härlett ur `url` i `src/_data/metadata.js`.

De två måste följas åt. Säger de emot varandra pekar all CSS och alla bilder
på fel bassökväg, och sidan renderar med rätt text men helt utan styling.

`src/CNAME` styr ingenting. Vid publicering via GitHub Actions läses den filen
inte för att konfigurera custom domain — den följer bara med som en inert fil
i bygget. Domänen sitter i repo-inställningarna.

#### DNS

Apex kräver **alla fyra** A-posterna mot GitHub Pages; med bara några av dem
avvisas domänen med `NotServedByPagesError`. Zonen ligger hos DigitalOcean.

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

Vill du testa sajten utan att blanda in din egen DNS-cache:

```
curl -sI --resolve zero-duplications.com:80:185.199.108.153 http://zero-duplications.com/
```

#### Om domänen någon gång tas bort

Sajten hamnar då på `https://paokarlsson.github.io/tech-blogg/` igen. Ta bort
custom domain i inställningarna **först**, och ändra `url` i metadata.js
tillbaka dit **efteråt** — i den ordningen, annars går sajten sönder däremellan.
