import re
import time
import yaml
from jinja2 import Template
import openai

# Use the default OpenAI client (will use API key from env)
client = openai.OpenAI()

# Global cache for prompt templates
PROMPT_CACHE = None

def render_prompt(template_str: str, context: dict) -> str:
    return Template(template_str).render(**context)

def load_prompt_template(mode: str, kpi: str) -> str:
    global PROMPT_CACHE
    if PROMPT_CACHE is None:
        with open("prompts/prompt_templates.yaml", "r", encoding="utf-8") as f:
            PROMPT_CACHE = yaml.safe_load(f)

    try:
        return PROMPT_CACHE[mode][kpi]
    except KeyError:
        raise ValueError(f"Prompt not found for mode='{mode}' and kpi='{kpi}'.")

def gpt_score(prompt: str, model: str, retries=3) -> dict:
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )
            content = response.choices[0].message.content
            return parse_gpt_response(content)
        except Exception as e:
            print(f"⚠️ GPT call failed on attempt {attempt + 1}: \n{e}")
            time.sleep(1)
    return {"score": 0.0, "explanation": "GPT call failed."}

def parse_gpt_response(content: str) -> dict:
    score_match = re.search(r"SCORE:\s*([0-9.]+)", content, re.IGNORECASE)
    score = float(score_match.group(1)) if score_match else 0.0

    explanation_match = re.search(r"EXPLANATION:\s*(.*)", content, re.IGNORECASE | re.DOTALL)
    explanation = explanation_match.group(1).strip() if explanation_match else "No explanation provided."

    return {
        "score": score,
        "explanation": explanation
    }
