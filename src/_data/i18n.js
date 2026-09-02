// Gränssnittssträngar per språk. `lang` sätts per katalog av src/sv/sv.json
// och src/en/en.json och plockas upp i mallarna som `i18n[lang]` (alias `t`).
module.exports = {
  sv: {
    home: "Hem",
    allPosts: "Alla inlägg",
    rss: "RSS",
    switchTo: "English",
    siteDescription: "Om systemutveckling, filosofi och AI.",
    onlyInOtherLang: "Det här inlägget finns bara på engelska ännu."
  },
  en: {
    home: "Home",
    allPosts: "All posts",
    rss: "RSS",
    switchTo: "Svenska",
    siteDescription: "On software engineering, philosophy, and AI.",
    onlyInOtherLang: "This post is only available in Swedish for now."
  }
};
