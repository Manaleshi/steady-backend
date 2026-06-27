import os
import json
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEYO")

@app.route("/")
def index():
    return jsonify({"message": "Steady API is running"})

@app.route("/question", methods=["POST"])
def generate_question():
    data = request.get_json()
    topic = data.get("topic", "General Chemistry")
    section = data.get("section", "Chemical & Physical Foundations")
    is_weak = data.get("is_weak", False)

    weak_hint = "The student is struggling with this topic. Include a brief scaffolding hint in the explanation to build confidence." if is_weak else ""

    prompt = f"""You are an MCAT tutor. Generate ONE multiple-choice question.
Section: {section}
Topic: {topic}
{weak_hint}
Respond ONLY with valid JSON, no markdown:
{{"question":"...","options":["A) ...","B) ...","C) ...","D) ..."],"correct_index":0,"explanation":"Under 80 words, warm and encouraging."}}
Rules: MCAT-level difficulty, plausible distractors, correct_index is 0-based."""

    response = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "Content-Type": "application/json",
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01"
        },
        json={
            "model": "claude-sonnet-4-6",
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": prompt}]
        }
    )

    result = response.json()
    raw = result["content"][0]["text"]
    clean = raw.replace("```json", "").replace("```", "").strip()
    question = json.loads(clean)
    return jsonify(question)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port, debug=True)