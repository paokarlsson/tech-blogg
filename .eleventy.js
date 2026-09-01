const pluginRss = require("@11ty/eleventy-plugin-rss");
const metadata = require("./src/_data/metadata.js");

module.exports = function (eleventyConfig) {
  eleventyConfig.addPlugin(pluginRss);

  eleventyConfig.addFilter("readableDate", (dateObj) =>
    new Intl.DateTimeFormat("sv-SE", { year: "numeric", month: "long", day: "numeric" }).format(dateObj)
  );
  eleventyConfig.addFilter("htmlDateString", (dateObj) =>
    dateObj.toISOString().slice(0, 10)
  );

  eleventyConfig.addPassthroughCopy("src/css");
  eleventyConfig.addPassthroughCopy("src/assets");
  eleventyConfig.addPassthroughCopy("src/CNAME");

  eleventyConfig.addCollection("posts", (collectionApi) =>
    collectionApi.getFilteredByGlob("src/posts/*.md").sort((a, b) => b.date - a.date)
  );

  // pathPrefix härleds ur metadata.url, som i sin tur härleds ur src/CNAME.
  // Egen domän (CNAME finns) → "/". Projektsida → "/tech-blogg/".
  // Byt domän genom att redigera src/CNAME, inte här.
  const basePath = new URL(metadata.url).pathname;

  return {
    dir: {
      input: "src",
      includes: "_includes",
      output: "_site"
    },
    pathPrefix: basePath.endsWith("/") ? basePath : `${basePath}/`
  };
};
