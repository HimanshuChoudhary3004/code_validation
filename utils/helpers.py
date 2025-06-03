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
    """Send a prompt to OpenAI and return the best-available response, even if it's not valid JSON."""
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

        # Remove markdown formatting like ```json or ``` if present
        if content.startswith("```"):
            content = content.split("```")[1].strip()

        if not content:
            return {
                "score": 1.0,
                "explanation": "[GPT Error] Empty response",
                "raw_output": ""
            }

        try:
            parsed = json.loads(content)
            score = parsed.get("score", 1.0)
            explanation = parsed.get("explanation", parsed)
            return {
                "score": score,
                "explanation": explanation,
                "raw_output": content
            }
        except json.JSONDecodeError:
            # Still capture the raw output for inspection even if JSON fails
            return {
                "score": 1.0,
                "explanation": "[GPT Error] Invalid JSON format",
                "raw_output": content
            }

    except Exception as e:
        return {
            "score": 1.0,
            "explanation": f"[GPT Error] {str(e)}",
            "raw_output": ""
        }

