import anthropic
import json
import requests
import base64
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder="static")
CORS(app)

client = anthropic.Anthropic()

POLLINATIONS_URL = "https://image.pollinations.ai/prompt/"

AGENT_STEPS = [
    {
        "id": "intent",
        "name": "Parse title intent",
        "prompt": """Analyze this YouTube title and identify:
1. hook_type: one of [curiosity_gap, transformation, controversy, how_to, extreme, listicle, authority]
2. content_category: the niche/topic (e.g. "food challenge", "finance", "gaming", "lifestyle")
3. creator_persona: what kind of creator likely made this (e.g. "challenge creator", "educator", "vlogger")

Respond ONLY with valid JSON, no markdown."""
    },
    {
        "id": "emotion",
        "name": "Infer viewer emotion",
        "prompt": """Based on the title and its hook type, identify:
1. target_emotion: the primary emotion to trigger (e.g. "shock", "envy", "fear", "excitement", "awe", "curiosity")
2. viewer_psychology: one sentence on WHY this emotion drives clicks for this title

Respond ONLY with valid JSON, no markdown."""
    },
    {
        "id": "visual",
        "name": "Generate visual concept",
        "prompt": """Design the visual composition:
1. visual_concept: 1-2 sentence description of the main scene
2. subject: who or what is the focal point
3. background: background treatment (color, environment, texture)
4. layout: one of [face_dominant, text_dominant, split_screen, before_after, object_hero]

Respond ONLY with valid JSON, no markdown."""
    },
    {
        "id": "color",
        "name": "Select color palette",
        "prompt": """Choose a color strategy:
1. palette: array of exactly 3 hex color codes that work for this thumbnail
2. contrast_strategy: one sentence on how to make the subject pop

Respond ONLY with valid JSON, no markdown."""
    },
    {
        "id": "text",
        "name": "Craft overlay text",
        "prompt": """Design the text elements:
1. overlay_text: punchy 3-7 word overlay text (or empty string if none needed)
2. font_style: one of [bold_impact, clean_sans, hand_drawn, urgent_red, neon_glow]
3. do_nots: array of 2-3 specific design mistakes to avoid for THIS thumbnail
4. image_prompt: a detailed Stable Diffusion prompt (50-80 words) to generate the thumbnail image. Include style, lighting, composition, colors, and mood. End with: "YouTube thumbnail, 16:9, high contrast, vibrant colors, professional photography"

Respond ONLY with valid JSON, no markdown."""
    },
]


def run_agent_step(title: str, step: dict, accumulated: dict) -> dict:
    context = f'YouTube title: "{title}"\n'
    if accumulated:
        context += f"Previously determined: {json.dumps(accumulated, indent=2)}\n"
    context += f"\nTask: {step['prompt']}"

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=600,
        system="You are a senior YouTube thumbnail designer and visual strategist. Always respond ONLY with valid JSON — no markdown fences, no explanation.",
        messages=[{"role": "user", "content": context}]
    )

    raw = message.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(raw)


def generate_image(prompt: str) -> str | None:
    try:
        encoded = requests.utils.quote(prompt)
        url = f"{POLLINATIONS_URL}{encoded}?width=1280&height=720&nologo=true"
        response = requests.get(url, timeout=60)
        if response.status_code == 200:
            b64 = base64.b64encode(response.content).decode("utf-8")
            return f"data:image/jpeg;base64,{b64}"
        return None
    except Exception:
        return None


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    title = data.get("title", "").strip()
    if not title:
        return jsonify({"error": "Title is required"}), 400

    accumulated = {}
    steps_output = []

    for step in AGENT_STEPS:
        try:
            result = run_agent_step(title, step, accumulated)
            accumulated.update(result)
            steps_output.append({
                "id": step["id"],
                "name": step["name"],
                "output": result
            })
        except Exception as e:
            return jsonify({"error": f"Step '{step['name']}' failed: {str(e)}"}), 500

    image_data = None
    if accumulated.get("image_prompt"):
        image_data = generate_image(accumulated["image_prompt"])

    return jsonify({
        "title": title,
        "brief": accumulated,
        "steps": steps_output,
        "image": image_data
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
