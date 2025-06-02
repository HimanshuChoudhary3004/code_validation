import os
import yaml
from utils.helpers import gpt_score, load_prompt_template, render_prompt

def run_ui5_analysis(mode_settings):
    base_dir = 'input/ui5/'
    results = []

    for folder in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder)
        meta_file = os.path.join(folder_path, '.meta.yaml')

        if not os.path.isfile(meta_file):
            continue

        with open(meta_file, 'r', encoding='utf-8') as f:
            meta = yaml.safe_load(f)

        prompt_id = meta.get("prompt_id", f"folder_{folder}")
        prompt_text = meta.get("prompt", "")

        # Aggregate all JS/JSON/YAML/XML code from folder
        all_code = ""
        for file in os.listdir(folder_path):
            if file.endswith(('.js', '.json', '.yaml', '.yml', '.xml')):
                with open(os.path.join(folder_path, file), 'r', encoding='utf-8') as code_file:
                    all_code += f"\n\n// --- {file} ---\n" + code_file.read()

        result = {
            "prompt_id": prompt_id,
            "prompt": prompt_text
        }

        lang = "UI5 JavaScript + config"

        for kpi, config in mode_settings['kpis'].items():
            if not config.get("enabled"):
                continue

            if kpi in ["functional_correctness", "maintainability", "code_smells"]:
                template = load_prompt_template("code_generation", kpi)
                prompt = render_prompt(template, {
                    "lang": lang,
                    "code": all_code,
                    "prompt": prompt_text
                })
                explanation = gpt_score(prompt, model=mode_settings['model'])
                result[f"{kpi}_score"] = 1.0
                result[f"{kpi}_explanation"] = explanation

        results.append(result)

    return results
