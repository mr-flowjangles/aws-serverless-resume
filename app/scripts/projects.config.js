/**
 * Projects Configuration
 * Edit this file to update what shows on the Projects section.
 *
 * Fields:
 *   name        — exact GitHub repo name (must match exactly)
 *   label       — display name shown on the card
 *   description — your own description, shown instead of GitHub's
 *   color       — header band color (use a hex code)
 */

export const PROJECTS_CONFIG = {
  github_username: "mr-flowjangles",

  repos: [
    {
      name: "the-fret-detective",
      label: "The Fret Detective",
      description: "AI Guitar Teacher, forked from bot-factory-ui.",
      // color: "#0284c7",
      color: "#0f172a",
      url: "https://thefretdetective.com",
    },
    {
      name: "bot-factory-ui",
      label: "Bot Factory UI",
      description:
        "Forkable web package to integrate with a RAG chatbot. bot-factory coming soon.",
      color: "#0f172a",
    },
  ],
};
