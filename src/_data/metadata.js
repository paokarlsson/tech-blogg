module.exports = {
  title: "Zero Duplications",
  description: "Om systemutveckling, filosofi och AI.",
  // Måste matcha var GitHub Pages faktiskt serverar sajten — härifrån härleds
  // pathPrefix. Custom domain är påslagen, så sajten ligger i domänens rot och
  // pathPrefix blir "/". Ändra inte på gissning: GitHubs Pages-API rapporterar
  // den faktiska URL:en i deploy-loggen ("Evaluated environment url").
  //
  // Tas custom domain bort under Settings → Pages hamnar sajten på
  // https://paokarlsson.github.io/tech-blogg igen, och då måste det här värdet
  // tillbaka dit — annars pekar css- och bildlänkar på roten och 404:ar.
  // src/CNAME styr inget av detta: vid publicering via GitHub Actions läses den
  // filen inte för att konfigurera domänen, den följer bara med i bygget.
  url: "https://zero-duplications.com",
  author: {
    name: "Ola Karlsson"
  }
};
