/**
 * Eleventy configuration file for the LynrieScoop frontend project
 * @file Eleventy configuration
 * @module .eleventy
 */

/**
 * Configures Eleventy static site generator settings
 * @param {Object} eleventyConfig - The Eleventy configuration object
 * @returns {Object} The Eleventy configuration object
 */
export default function (eleventyConfig) {
  // Pas de passthrough copy aan zodat stylesheets en andere resources gekopieerd worden
  /**
   * Configure resource paths to be copied to the output directory
   */
  eleventyConfig.addPassthroughCopy({
    'resources/Css': 'resources/css',
    'resources/Images': 'resources/images',
    'resources/Javascript': 'resources/javascript',
    'resources/videos': 'resources/videos',
  });

  // Optioneel: kopieer ook alles uit resources als fallback
  // eleventyConfig.addPassthroughCopy({ "resources": "resources" });
  /**
   * Define the directory structure for Eleventy
   */
  return {
    dir: {
      input: '.', // Input directory (project root)
      output: '_site', // Output directory for built site
    },
  };
}
