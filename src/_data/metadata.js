const fs = require("fs");
const path = require("path");

// src/CNAME är enda källan till var sajten faktiskt ligger: samma fil styr
// GitHub Pages custom domain. Finns den serveras sajten från domänens rot,
// och pathPrefix i .eleventy.js blir därmed "/". Tas den bort faller vi
// tillbaka på projektsidans URL, där bassökvägen är /tech-blogg/.
// Ändra alltså domän genom att redigera (eller ta bort) src/CNAME — aldrig
// genom att handredigera url här, det var det som gick isär tidigare.
const cnamePath = path.join(__dirname, "..", "CNAME");
const customDomain = fs.existsSync(cnamePath)
  ? fs.readFileSync(cnamePath, "utf8").split("\n")[0].trim()
  : "";

module.exports = {
  title: "Zero Duplications",
  description: "Om systemutveckling, filosofi och AI.",
  // Utan avslutande snedstreck — feed.njk bygger absoluta URL:er som metadata.url + post.url.
  url: customDomain
    ? `https://${customDomain}`
    : "https://paokarlsson.github.io/tech-blogg",
  author: {
    name: "Ola Karlsson"
  }
};
