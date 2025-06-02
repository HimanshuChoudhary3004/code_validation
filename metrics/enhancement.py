from utils.helpers import gpt_score, load_prompt_template, render_prompt
from metrics.shared import calculate_cyclomatic_complexity, normalize_score

def run_enhancement_kpis(rows, mode_settings):
    output = []
    for row in rows:
        result = row.copy()
        original = row['original_code']
        enhanced = row['enhanced_code']
        lang = row['file_extension'].lower()
        enhancement_prompt = row.get('enhancement_prompt', '')

        for kpi, config in mode_settings['kpis'].items():
            if not config.get('enabled'):
                continue

            if kpi in [
                'functional_correctness', 'maintainability',
                'goal_fulfillment', 'regression_safety', 'code_smells',
                'hallucination', 'technical_bias' 
            ]:
                template = load_prompt_template("code_enhancement", kpi)
                prompt = render_prompt(template, {
                    "lang": lang,
                    "original": original,
                    "enhanced": enhanced,
                    "enhancement_prompt": enhancement_prompt
                })
                response = gpt_score(prompt, model=mode_settings['model'])
                score = response.get("score", 0.0)
                explanation = response.get("explanation", "No explanation returned.")
                result[f"{kpi}_score"] = round(score, 2)
                result[f"{kpi}_explanation"] = explanation

            elif kpi == 'smell_delta':
                template = load_prompt_template("code_enhancement", "smell_delta")
                prompt = render_prompt(template, {
                    "lang": lang,
                    "original": original,
                    "enhanced": enhanced
                })
                response = gpt_score(prompt, model=mode_settings['model'])
                score = response.get("score", 0.0)
                explanation = response.get("explanation", "No explanation returned.")
                result["smell_delta_score"] = round(score, 2)
                result["smell_delta_explanation"] = explanation

            elif kpi == 'cyclomatic_delta':
                before = calculate_cyclomatic_complexity(original, f".{lang}")
                after = calculate_cyclomatic_complexity(enhanced, f".{lang}")
                delta = before - after
                score = normalize_score(delta, 0, config['threshold'])
                result[f"{kpi}_score"] = round(score, 2)
                result[f"{kpi}_explanation"] = f"Cyclomatic complexity changed: {before} → {after}."

            elif kpi == 'cognitive_delta':
                nesting_before = original.count('IF') + original.count('CASE')
                nesting_after = enhanced.count('IF') + enhanced.count('CASE')
                delta = nesting_before - nesting_after
                score = normalize_score(delta, 0, config['threshold'])
                result[f"{kpi}_score"] = round(score, 2)
                result[f"{kpi}_explanation"] = f"Cognitive nesting changed: {nesting_before} → {nesting_after}."

        output.append(result)
    return output
