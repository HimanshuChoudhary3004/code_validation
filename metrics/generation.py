from utils.helpers import gpt_score, load_prompt_template, render_prompt
from metrics.shared import calculate_cyclomatic_complexity, normalize_score

def run_generation_kpis(rows, mode_settings):
    output = []
    for row in rows:
        code = row['code']
        lang = row['file_extension'].lower()
        prompt_text = row.get('prompt', '')
        result = row.copy()

        for kpi, config in mode_settings['kpis'].items():
            if not config.get('enabled'):
                continue

            if kpi in ['functional_correctness', 'maintainability', 'code_smells','hallucination', 'technical_bias' ]:
                template = load_prompt_template("code_generation", kpi)
                prompt = render_prompt(template, {
                    "lang": lang,
                    "code": code,
                    "prompt": prompt_text
                })
                response = gpt_score(prompt, model=mode_settings['model'])
                score, explanation = response.get("score", 0.0), response.get("explanation", "No explanation returned.")
                result[f"{kpi}_score"] = round(score, 2)
                result[f"{kpi}_explanation"] = explanation

            elif kpi == 'cyclomatic_complexity':
                raw = calculate_cyclomatic_complexity(code, f".{lang}")
                score = normalize_score(raw, baseline=5, threshold=config['threshold'])
                result[f"{kpi}_score"] = round(score, 2)
                result[f"{kpi}_explanation"] = f"Cyclomatic complexity is {raw}. Target is under {config['threshold']}."

            elif kpi == 'cognitive_complexity':
                nesting_level = code.count('IF') + code.count('CASE')
                score = normalize_score(nesting_level, baseline=2, threshold=config['threshold'])
                result[f"{kpi}_score"] = round(score, 2)
                result[f"{kpi}_explanation"] = f"Estimated nesting level is {nesting_level}. Target should be under {config['threshold']}."

        output.append(result)
    return output
