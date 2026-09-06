# Thumbnail Brief Generator — Deion Demo

An autonomous multi-step Claude agent that transforms a YouTube video title into a structured thumbnail design brief.

## What it does

Given a YouTube title like *"I Survived 100 Days With No Sleep"*, the agent runs 5 sequential reasoning steps:

1. **Parse title intent** — identifies hook type, content category, creator persona
2. **Infer viewer emotion** — determines target emotion and viewer psychology
3. **Generate visual concept** — designs the composition, subject, background, layout
4. **Select color palette** — chooses 3 harmonious hex colors + contrast strategy
5. **Craft overlay text** — writes punchy text, picks font style, lists design mistakes to avoid

Each step builds on the last — accumulated context is passed forward so the agent reasons coherently across the full brief.

## Setup

```bash
# 1. Clone / download this project
# 2. Enter the project directory
cd thumbnail-brief-agent

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set your Anthropic API key
export ANTHROPIC_API_KEY=your_key_here

# 5. Run the server
python app.py
```

Then open [http://localhost:5000](http://localhost:5000) in your browser.

## Architecture

```text
thumbnail-brief-agent/
├── app.py          — Flask server + multi-step agent workflow
├── static/
│   └── index.html  — Frontend UI
└── requirements.txt
```

The agent uses the Anthropic API for five sequential reasoning steps. Each step receives the context accumulated from the previous steps so the final brief stays consistent across intent, emotion, visual direction, color, and overlay text.

After the brief is complete, the app can also request a generated thumbnail concept image from Pollinations using the final image prompt.

## Tech Stack

Python · Flask · Anthropic API · HTML/CSS/JavaScript · Pollinations
