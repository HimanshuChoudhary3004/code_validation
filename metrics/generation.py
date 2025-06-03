import json
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from typing import Tuple
from utils.helpers import (
    call_gpt,
    load_yaml,
    render_template
)

class CodeGenerationEvaluator:
    def __init__(self, settings: dict, input_path: str, output_path: str):
        self.settings = settings
        self.input_path = input_path
        self.output_path = output_path
        self.model = settings['model']
        self.kpis = settings['kpis']
        self.max_workers = settings.get('max_workers', 4)

        # Load template and system prompt
        self.templates = load_yaml("prompts/template_generation.yaml")
        self.system_prompt = load_yaml("system_prompts/code_generation_system_prompt.yaml")["system_prompt"]

    def run_kpi(self, kpi_name: str, prompt_text: str) -> Tuple[float, dict]:
        try:
            response = call_gpt(
                system_prompt=self.system_prompt,
                user_prompt=prompt_text,
                model=self.model
            )
            return float(response["score"]), response["explanation"]
        except Exception as e:
            return 1.0, f"[GPT Error] {str(e)}"

    def evaluate_row(self, row: pd.Series, kpi_name: str, kpi_config: dict) -> Tuple[str, float, dict]:
        try:
            template_entry = self.templates.get(kpi_name)
            if not template_entry:
                if kpi_name in ["cyclomatic_complexity", "cognitive_complexity"]:
                    return kpi_name, 1.0, "[Internal Info] Template not needed (static KPI)"
                return kpi_name, 1.0, "[Internal Error] Template not found"

            prompt_text = render_template(template_entry["prompt"], {
                "lang": row["file_extension"],
                "prompt": row["prompt"],
                "code": row["code"]
            })

            score, explanation = self.run_kpi(kpi_name, prompt_text)
            return kpi_name, score, explanation

        except Exception as e:
            return kpi_name, 1.0, f"[Internal Error] {str(e)}"

    def run(self):
        df = pd.read_csv(self.input_path)
        print(f"📦 Loaded {len(df)} rows from {self.input_path}")
        results = []

        for i, row in df.iterrows():
            row_result = row.copy()
            print(f"🔍 Evaluating row {i + 1}/{len(df)}: Language = {row['file_extension']}")

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                tasks = [
                    executor.submit(self.evaluate_row, row, kpi, config)
                    for kpi, config in self.kpis.items() if config.get("enabled", True)
                ]

                for task in tasks:
                    kpi, score, explanation = task.result()
                    row_result[f"{kpi}_score"] = score
                    row_result[f"{kpi}_explanation"] = explanation

            results.append(row_result)

        pd.DataFrame(results).to_csv(self.output_path, index=False)
        print(f"✅ Code Generation Evaluation complete. Output saved to: {self.output_path}")
