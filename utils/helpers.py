import yaml
from pathlib import Path
from jinja2 import Template
from openai import OpenAI
import json

client = OpenAI()

def render_template(template_str: str, context: dict) -> str:
    """Render a Jinja2 template string with given variables."""
    return Template(template_str).render(**context)

def load_yaml(path: str) -> dict:
    """Load a YAML file and return its contents as a dictionary."""
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def call_gpt(system_prompt: str, user_prompt: str, model: str) -> dict:
    """Send a prompt to OpenAI and return the structured response (score + explanation)."""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2
        )
        content = response.choices[0].message.content.strip()

        # Remove markdown fences like ```json or ```
        if content.startswith("```"):
            content = content.split("```")[1].strip()

        if not content:
            return {"score": 1.0, "explanation": "[GPT Error] Empty response"}

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {
                "score": 1.0,
                "explanation": f"[GPT Error] Invalid JSON format\nRaw GPT output:\n{content}"
            }

    except Exception as e:
        return {
            "score": 1.0,
            "explanation": f"[GPT Error] {str(e)}"
        }
