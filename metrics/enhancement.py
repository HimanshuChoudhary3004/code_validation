import json
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from utils.helpers import (
    call_gpt,
    load_yaml,
    render_template
)

class EnhancementKPIEvaluator:
    def __init__(self, config: dict, input_path: str, output_path: str):
        self.config = config
        self.input_path = input_path
        self.output_path = output_path
        self.model = config['model']
        self.kpis = config['kpis']
        self.max_workers = config.get('workers', 4)

        # Load system prompt and KPI templates
        self.system_prompt = load_yaml("system_prompts/code_enhancement_system_prompt.yaml")["system_prompt"]
        self.templates = load_yaml("prompts/template_enhancement.yaml")

    def run_kpi(self, kpi_name: str, prompt: str):
        try:
            result = call_gpt(
                system_prompt=self.system_prompt,
                user_prompt=prompt,
                model=self.model
            )
            return float(result["score"]), result["explanation"]
        except Exception as e:
            return 1.0, f"[GPT Error] {str(e)}"

    def evaluate_kpi_wrapper(self, kpi_name: str, prompt_text: str):
        score, explanation = self.run_kpi(kpi_name, prompt_text)
        return kpi_name, score, explanation

    def evaluate_row(self, row: pd.Series, row_index: int):
        result_row = row.copy()
        print(f"🔍 Evaluating row {row_index + 1}: lang = {row['file_extension']}")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            tasks = []

            for kpi_name, kpi_cfg in self.kpis.items():
                if not kpi_cfg.get("enabled", True):
                    continue

                template = self.templates.get(kpi_name)
                if not template:
                    if kpi_name in ["cyclomatic_complexity", "cognitive_complexity"]:
                        continue  # Skip non-GPT KPIs gracefully
                    print(f"[Warning] Missing template for KPI: {kpi_name}")
                    continue

                prompt_text = render_template(template["prompt"], {
                    "lang": row["file_extension"],
                    "original_code": row["original_code"],
                    "enhancement_prompt": row.get("enhancement_prompt", ""),
                    "enhanced_code": row["enhanced_code"]
                })

                tasks.append(executor.submit(self.evaluate_kpi_wrapper, kpi_name, prompt_text))

            for task in tasks:
                kpi_name, score, explanation = task.result()
                result_row[f"{kpi_name}_score"] = score
                result_row[f"{kpi_name}_explanation"] = explanation

        return result_row

    def run_all(self):
        df = pd.read_csv(self.input_path)
        print(f"📦 Loaded {len(df)} enhancement rows from {self.input_path}")

        results = []
        for i, row in df.iterrows():
            evaluated = self.evaluate_row(row, i)
            results.append(evaluated)

        pd.DataFrame(results).to_csv(self.output_path, index=False)
        print(f"✅ Enhancement KPI Evaluation complete. Output saved to: {self.output_path}")
