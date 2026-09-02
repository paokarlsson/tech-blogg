module.exports = {
  title: "Zero Duplications",
  description: "Om systemutveckling, filosofi och AI.",
  // Detta ÄR den faktiska live-URL:en. GitHubs Pages-API rapporterar den i
  // deploy-loggen ("Evaluated environment url"), så ändra inget här på gissning.
  //
  // Att byta till "https://zero-duplications.com" kräver ETT manuellt steg först:
  // sätt domänen under Settings → Pages → Custom domain. src/CNAME räcker INTE —
  // vid publicering via GitHub Actions (actions/deploy-pages) läses den filen inte
  // för att konfigurera domänen, den följer bara med som en inert fil i bygget.
  // DNS är INTE klart (kontrollerat 2026-09-02): apex har bara 1 av de 4
  // A-poster GitHub kräver, därav NotServedByPagesError. www är korrekt.
  // Se README → "Byta till zero-duplications.com" för vad som ska läggas till.
  //
  // Ordningen spelar roll. Byts URL:en här först blir pathPrefix "/" medan sajten
  // fortfarande ligger under /tech-blogg/ → alla css- och bildlänkar 404:ar.
  url: "https://paokarlsson.github.io/tech-blogg",
  author: {
    name: "Ola Karlsson"
  }
};
