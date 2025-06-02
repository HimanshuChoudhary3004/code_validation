import os
import yaml
from dotenv import load_dotenv
from utils.file_loader import load_input_data
from utils.logger import write_report
from metrics import generation, enhancement, ui5

load_dotenv()

def load_settings():
    with open('config/settings.yaml') as f:
        return yaml.safe_load(f)

def run():
    settings = load_settings()
    dual_mode = settings.get("dual_mode", False)

    if dual_mode:
        print("Dual mode enabled — running both code_generation and code_enhancement...")

        # --- Code Generation ---
        cg_settings = settings["code_generation"]
        rows_cg = load_input_data("code_generation")
        results_cg = generation.run_generation_kpis(rows_cg, cg_settings)
        write_report(results_cg, "code_generation")

        # --- Code Enhancement ---
        ce_settings = settings["code_enhancement"]
        rows_ce = load_input_data("code_enhancement")
        results_ce = enhancement.run_enhancement_kpis(rows_ce, ce_settings)
        write_report(results_ce, "code_enhancement")

    elif settings.get("code_generation", {}).get("enabled"):
        mode = "code_generation"
        mode_settings = settings["code_generation"]
        rows = load_input_data(mode)
        results = generation.run_generation_kpis(rows, mode_settings)
        write_report(results, mode)

    elif settings.get("code_enhancement", {}).get("enabled"):
        mode = "code_enhancement"
        mode_settings = settings["code_enhancement"]
        rows = load_input_data(mode)
        results = enhancement.run_enhancement_kpis(rows, mode_settings)
        write_report(results, mode)

    else:
        raise ValueError("⚠️ No mode enabled in settings.yaml")

if __name__ == "__main__":
    run()
