const pluginRss = require("@11ty/eleventy-plugin-rss");
const metadata = require("./src/_data/metadata.js");

module.exports = function (eleventyConfig) {
  eleventyConfig.addPlugin(pluginRss);

  eleventyConfig.addFilter("readableDate", (dateObj, lang) =>
    new Intl.DateTimeFormat(lang === "en" ? "en" : "sv-SE", { year: "numeric", month: "long", day: "numeric" }).format(dateObj)
  );
  eleventyConfig.addFilter("htmlDateString", (dateObj) =>
    dateObj.toISOString().slice(0, 10)
  );

  // Slår upp motsvarande sida på ett annat språk via delad `translationKey`
  // i front matter. Används av språkväxlaren och hreflang-länkarna i base.njk.
  eleventyConfig.addFilter("translationUrl", (allItems, translationKey, targetLang) => {
    if (!translationKey) return null;
    const match = allItems.find(
      (item) => item.data.translationKey === translationKey && item.data.lang === targetLang
    );
    return match ? match.url : null;
  });

  eleventyConfig.addPassthroughCopy("src/css");
  eleventyConfig.addPassthroughCopy("src/assets");
  eleventyConfig.addPassthroughCopy("src/CNAME");

  eleventyConfig.addCollection("posts_sv", (collectionApi) =>
    collectionApi.getFilteredByGlob("src/sv/posts/*.md").sort((a, b) => b.date - a.date)
  );
  eleventyConfig.addCollection("posts_en", (collectionApi) =>
    collectionApi.getFilteredByGlob("src/en/posts/*.md").sort((a, b) => b.date - a.date)
  );

  // pathPrefix härleds ur metadata.url (enda källan till repots bassökväg) —
  // ändra bara där, t.ex. vid byte av repo-namn eller egen domän.
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
