import yaml
from metrics.generation import CodeGenerationEvaluator
from metrics.enhancement import EnhancementKPIEvaluator

def run():
    with open("config/settings.yaml", "r") as f:
        config = yaml.safe_load(f)

    if config.get("code_generation", {}).get("enabled", False):
        gen_cfg = config["code_generation"]
        print("🚀 [Start] Code Generation Evaluation")
        evaluator = CodeGenerationEvaluator(
            settings=gen_cfg,
            input_path=gen_cfg["input"],
            output_path=gen_cfg["output"]
        )
        evaluator.run()
        print("✅ [Done] Code Generation Evaluation")

    if config.get("code_enhancement", {}).get("enabled", False):
        enh_cfg = config["code_enhancement"]
        print("🚀 [Start] Code Enhancement Evaluation")
        evaluator = EnhancementKPIEvaluator(
            config=enh_cfg,
            input_path=enh_cfg["input"],
            output_path=enh_cfg["output"]
        )
        evaluator.run_all()
        print("✅ [Done] Code Enhancement Evaluation")

if __name__ == "__main__":
    run()
