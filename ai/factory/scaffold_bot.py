#!/usr/bin/env python3
"""
Bot Factory — Frontend Scaffolder

Reads a bot's config.yml and generates the frontend structure:
  - app/{bot_id}.html          (from template, with config values)
  - app/bot_scripts/{bot_id}/  (empty, for bot-specific JS/CSS)
  - app/assets/{bot_id}/       (empty, for bot-specific images)

Usage:
  python3 ai/factory/scaffold_bot.py guitar
  python3 ai/factory/scaffold_bot.py robbai

Run from the project root (~/myPortfolio/aws-serverless-resume/).
"""

import sys
import os
import yaml
from pathlib import Path


def load_config(bot_id: str) -> dict:
    """Load and validate a bot's config.yml."""
    config_path = Path(f"ai/factory/bots/{bot_id}/config.yml")
    if not config_path.exists():
        print(f"❌ Config not found: {config_path}")
        sys.exit(1)

    with open(config_path) as f:
        config = yaml.safe_load(f)

    # Validate required fields
    required = ["bot.id", "bot.name", "suggestions", "frontend.subtitle",
                "frontend.welcome", "frontend.placeholder"]
    for field in required:
        parts = field.split(".")
        val = config
        for part in parts:
            val = val.get(part, {}) if isinstance(val, dict) else None
        if not val:
            print(f"❌ Missing required field: {field}")
            sys.exit(1)

    return config


def build_nav_html(nav_items: list, bot_id: str) -> str:
    """Generate the left nav HTML from config nav entries."""
    lines = []
    for i, item in enumerate(nav_items):
        active = ' class="active"' if i == 0 else ""
        lines.append(
            f'        <a href="#{item["section"]}"{active}>\n'
            f'            <span class="nav-icon">{item["icon"]}</span> {item["label"]}\n'
            f'        </a>'
        )
    return "\n".join(lines)


def build_suggestions_html(suggestions: list) -> str:
    """Generate suggestion chip buttons from config."""
    lines = []
    for suggestion in suggestions:
        lines.append(
            f'                    <button class="suggestion-chip" '
            f'onclick="sendSuggestion(this)">{suggestion}</button>'
        )
    return "\n".join(lines)


def generate_html(config: dict) -> str:
    """Build the full HTML page from config values."""
    bot = config["bot"]
    frontend = config.get("frontend", {})
    bot_id = bot["id"]
    bot_name = bot["name"]
    subtitle = frontend.get("subtitle", f"{bot_name} Assistant")
    welcome = frontend.get("welcome", f"Hi! I'm {bot_name}. How can I help?")
    placeholder = frontend.get("placeholder", "Type a message...")
    badge = frontend.get("badge", "Beta")
    nav_items = frontend.get("nav", [])
    suggestions = config.get("suggestions", [])

    nav_html = build_nav_html(nav_items, bot_id)
    suggestions_html = build_suggestions_html(suggestions)

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{bot_name} — {subtitle}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet">

    <!-- Shared bot factory styles -->
    <link rel="stylesheet" href="bot_scripts/bot-factory.css">
    <!-- Bot-specific styles (add your CSS here) -->
    <link rel="stylesheet" href="bot_scripts/{bot_id}/{bot_id}.css">
</head>
<body>

    <!-- HEADER -->
    <header class="site-header">
        <div class="header-logo-area">
            <img src="assets/{bot_id}/logo.png" alt="{bot_name}" class="header-image">
        </div>
        <div class="header-text">
            <div class="header-title">{bot_name}</div>
            <div class="header-subtitle">{subtitle}</div>
        </div>
        <span class="header-badge">{badge}</span>
    </header>

    <!-- LEFT NAV -->
    <nav class="site-nav">
        <div class="nav-section-label">Topics</div>
{nav_html}

        <div class="nav-spacer"></div>
        <div class="nav-footer">
            Built with <a href="#">Bot Factory</a>
        </div>
    </nav>

    <!-- MAIN CONTENT -->
    <main class="main-content">

        <section class="section" id="chat">
            <h2 class="section-title">Ask {bot_name}</h2>

            <div class="chat-container">
                <div class="chat-header">
                    <div class="chat-header-dot"></div>
                    <span class="chat-header-title">{bot_name}</span>
                    <span class="chat-header-status">Online</span>
                </div>

                <div class="chat-messages" id="chatMessages">
                    <div class="chat-message bot">
                        <div class="bot-label">{bot_name}</div>
                        {welcome}
                    </div>
                </div>

                <div class="chat-suggestions" id="chatSuggestions">
{suggestions_html}
                </div>

                <div class="chat-input-area">
                    <input type="text" id="chatInput" placeholder="{placeholder}">
                    <button class="chat-send-btn" onclick="sendMessage()">Send</button>
                </div>
            </div>
        </section>

        <section class="section" id="about">
            <h2 class="section-title">About {bot_name}</h2>
            <div class="card">
                <h3>What is this?</h3>
                <p>Add a description of {bot_name} here.</p>
            </div>
        </section>

    </main>

    <footer class="site-footer">
        <p>Built with <a href="#">Bot Factory</a> — a reusable RAG chatbot framework</p>
    </footer>

    <!-- ================================================================
         SCRIPTS

         Load order:
         1. BOT_CONFIG  — bot identity and API endpoint
         2. (optional)  — bot-specific formatter in bot_scripts/{bot_id}/
         3. chat.js     — shared chat module
         4. navigation  — shared nav highlighting
         ================================================================ -->
    <script>
        window.BOT_CONFIG = {{
            apiUrl: '/api/{bot_id}',
            botName: '{bot_name}',
            placeholder: '{placeholder}'
        }};
    </script>
    <!-- Add bot-specific scripts here (e.g. formatter.js) -->
    <script src="bot_scripts/chat.js"></script>
    <script src="bot_scripts/navigation.js"></script>

</body>
</html>'''


def scaffold(bot_id: str):
    """Main entry point — read config, create folders, write HTML."""
    config = load_config(bot_id)

    bot_name = config["bot"]["name"]
    app_dir = Path("app")

    # Paths to create
    scripts_dir = app_dir / "bot_scripts" / bot_id
    assets_dir = app_dir / "assets" / bot_id
    html_file = app_dir / f"{bot_id}.html"
    css_file = scripts_dir / f"{bot_id}.css"

    # Safety check — don't overwrite existing HTML
    if html_file.exists():
        print(f"⚠️  {html_file} already exists. Overwrite? (y/n): ", end="")
        if input().strip().lower() != "y":
            print("Aborted.")
            sys.exit(0)

    # Create directories
    scripts_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)

    # Create empty bot CSS if it doesn't exist
    if not css_file.exists():
        css_file.write_text(
            f"/* ================================================================\n"
            f"   {bot_name.upper()} — Bot-Specific Styles\n"
            f"   Add custom styles for {bot_name} here.\n"
            f"   ================================================================ */\n"
        )
        print(f"  ✅ Created {css_file}")

    # Generate HTML
    html = generate_html(config)
    html_file.write_text(html)
    print(f"  ✅ Created {html_file}")

    # Summary
    print(f"\n🎉 Scaffolded {bot_name}!")
    print(f"   HTML:    {html_file}")
    print(f"   Scripts: {scripts_dir}/")
    print(f"   Assets:  {assets_dir}/")
    print(f"\n   Next steps:")
    print(f"   1. Add a logo to {assets_dir}/logo.png")
    print(f"   2. Add bot-specific styles to {css_file}")
    print(f"   3. (Optional) Add a formatter.js in {scripts_dir}/")
    print(f"   4. docker compose up and visit localhost:8080/{bot_id}.html")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 ai/factory/scaffold_bot.py <bot_id>")
        print("Example: python3 ai/factory/scaffold_bot.py guitar")
        sys.exit(1)

    scaffold(sys.argv[1])
