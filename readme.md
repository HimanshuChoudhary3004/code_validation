# Code KPI Validator

An intelligent system for evaluating the **quality** of code generated or enhanced by Large Language Models (LLMs) like GPT. It performs automated validation using a combination of **static analysis tools**, **custom rules**, and **GPT-based scoring**, across multiple **enterprise-grade programming languages** including ABAP, RAP, SQL, PL/SQL, and UI5.

---

##  Features

- ✅ Supports **two distinct modes**:
  - `code_generation`: Validates fresh code from prompt.
  - `code_enhancement`: Compares original vs. enhanced code.
- ✅ **Dynamic prompt engine** (Jinja2 templated) with GPT scoring logic.
- ✅ Built-in support for:
  - Maintainability
  - Code Smells
  - Complexity (Cyclomatic & Cognitive)
  - Functional Correctness
  - Goal Fulfillment & Regression Safety
- ✅ Designed for **SAP + Oracle stack** (ABAP, RAP, SQL, PL/SQL, UI5)
- ✅ Fully configurable via YAML files
- ✅ Dual-mode reporting with separate outputs per scenario
- ✅ Prompt repository stored centrally in a single `.yaml` file

---

## 📁 Project Structure

code_kpi_validator/
├── main.py                     #  Entry point – runs generation and/or enhancement modes
├── requirements.txt            #  Python dependencies

├── config/
│   ├── settings.yaml           #  Controls mode, KPIs, thresholds, model, etc.
│   └── kpi_definitions.yaml    #  Descriptions of each KPI (optional)

├── input/
│   ├── code_generation.csv     #  Prompts and code to evaluate
│   ├── code_enhancement.csv    #  Original, enhancement prompt, and enhanced code
│   └── ui5/                    #  UI5 folder-based input (subfolders with .meta.yaml + files)

├── output/
│   ├── code_generation_report.csv
│   └── code_enhancement_report.csv

├── prompts/
│   └── prompt_templates.yaml   #  All GPT prompt templates in YAML (mode → KPI → prompt)

├── metrics/
│   ├── generation.py           #  KPI logic for code_generation mode
│   ├── enhancement.py          #  KPI logic for code_enhancement mode
│   └── shared.py               #  Shared utilities: complexity, smell detection, scoring

├── utils/
│   ├── helpers.py              #  GPT client, prompt rendering, response parsing
│   ├── file_loader.py          #  Loads and parses input files
│   └── logger.py               #  Writes CSV output reports
````

---

##  Supported KPIs

| KPI Name                | Scenario         | Evaluator | Description                                            |
| ----------------------- | ---------------- | --------- | ------------------------------------------------------ |
| functional\_correctness | both             | GPT       | Checks if code fulfills its prompt/function            |
| maintainability         | both             | GPT       | Assesses readability, modularity, naming, and comments |
| code\_smells            | generation only  | GPT       | Detects smells like long methods, poor naming, etc.    |
| smell\_delta            | enhancement only | GPT       | Compares smells before and after                       |
| cyclomatic\_complexity  | generation only  | Lizard    | Measures decision branching in code                    |
| cognitive\_complexity   | generation only  | Static    | Estimates mental burden based on nesting/depth         |
| cyclomatic\_delta       | enhancement only | Lizard    | Delta of branching complexity                          |
| cognitive\_delta        | enhancement only | Static    | Delta of logical nesting and complexity                |
| goal\_fulfillment       | enhancement only | GPT       | Did the enhancement fulfill the new requirement?       |
| regression\_safety      | enhancement only | GPT       | Did it break or preserve original behavior?            |

>  All scores range from **0.0 to 1.0** with structured natural language explanations.

---

##  Input Format

###  Code Generation (CSV)

file_extension,prompt,code
abap,Write a report to display current date,"DATA lv_date TYPE sy-datum. lv_date = sy-datum. WRITE: / lv_date."
```

###  Code Enhancement (CSV)

file_extension,original_code,enhancement_prompt,enhanced_code
sql,"SELECT * FROM users","Add a WHERE clause to filter active users","SELECT * FROM users WHERE status = 'active';"
```

###  UI5 Input (Folder)

```bash
input/ui5/1/
├── Controller.js
├── View.view.xml
├── manifest.json
├── .meta.yaml   # Contains prompt ID and actual prompt
```

---

##  Configuration (`config/settings.yaml`)

```yaml
mode: dual        # Options: code_generation, code_enhancement, dual
model: gpt-4o     # OpenAI model for GPT-based KPIs

kpis:
  functional_correctness:
    enabled: true
    threshold: 0.85
  maintainability:
    enabled: true
    threshold: 0.75
  code_smells:
    enabled: true
    threshold: 0.85
  goal_fulfillment:
    enabled: true
    threshold: 0.85
  regression_safety:
    enabled: true
    threshold: 0.9
```

---

##  Prompts (`prompts/prompt_templates.yaml`)

All prompts are centrally managed in YAML format using Jinja2 variables (`{{code}}`, `{{prompt}}`, etc.).

Each prompt includes:

* Evaluation criteria
* Scoring formula
* Required output format (SCORE + EXPLANATION)

---

##  Libraries Used

| Package      | Purpose                          |
| ------------ | -------------------------------- |
| `openai`     | GPT-3.5/4 API interface          |
| `lizard`     | Cyclomatic complexity analysis   |
| `pandas`     | CSV I/O and DataFrame processing |
| `jinja2`     | Prompt templating engine         |
| `yaml`       | Config and template management   |
| `re`, `time` | Parsing, retries                 |

---

##  Flow of Execution

1.  Set `config/settings.yaml` to desired mode and KPIs
2.  Place your input files in `input/`
3.  Run the script:

   ```bash
   python main.py
   ```
4.  Get results in `output/` as:

   * `code_generation_report.csv`
   * `code_enhancement_report.csv`
5.  Review `*_score` and `*_explanation` for each KPI

---

##  Example Output (CSV)

| file\_extension | functional\_correctness\_score | functional\_correctness\_explanation |
| --------------- | ------------------------------ | ------------------------------------ |
| abap            | 1.0                            | Covers all steps, logic correct      |
| sql             | 0.8                            | Minor logic deviation detected       |

---

##  Notes

*  GPT scoring is cached per prompt session
*  Scores are normalized using configurable thresholds
*  All prompts follow explainable scoring models
*  API key should be stored in `.env` as `OPENAI_API_KEY`


##  Contributing

To contribute or extend the system:

1. Fork the repo
2. Add new KPI templates in `prompt_templates.yaml`
3. Register new logic in `generation.py` or `enhancement.py`
4. Run `python main.py` and test outputs

---