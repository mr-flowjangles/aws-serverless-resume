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
      name: "aws-serverless-resume",
      label: "Serverless Resume",
      description:
        "This site — with RobbAI chat widget powered by Bot Factory. Serverless resume running FastAPI on Lambda, deployed with Terraform.",
      color: "#0f172a",
    },
    {
      name: "bot-factory",
      label: "Bot Factory",
      description:
        "Powers the RobbAI chat on this site and The Fret Detective. Reusable RAG chatbot platform — define bots with YAML, deploy to serverless AWS.",
      color: "#0f172a",
    },
    {
      name: "bot-factory-ui",
      label: "Bot Factory UI",
      description:
        "Forkable frontend package for integrating with a Bot Factory RAG chatbot.",
      color: "#0f172a",
    },
    {
      name: "the-fret-detective",
      label: "The Fret Detective",
      description:
        "AI guitar teacher built on Bot Factory. Learn chords, scales, and theory through conversation.",
      color: "#0f172a",
      url: "https://thefretdetective.com",
    },
  ],
};
