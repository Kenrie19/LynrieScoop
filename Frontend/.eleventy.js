// Change to ESM export for Eleventy config
export default function(eleventyConfig) {
  // Pas de passthrough copy aan zodat stylesheets en andere resources gekopieerd worden
  eleventyConfig.addPassthroughCopy({
    "resources/Css": "resources/css",
    "resources/Images": "resources/images",
    "resources/Javascript": "resources/javascript",
    "resources/videos": "resources/videos",
  });

  // Optioneel: kopieer ook alles uit resources als fallback
  // eleventyConfig.addPassthroughCopy({ "resources": "resources" });

  return {
    dir: {
      input: ".",
      output: "_site"
    }
  };
};
