import lizard

def calculate_cyclomatic_complexity(code, file_extension=".abap"):
    """
    Uses lizard to analyze cyclomatic complexity of provided code.
    """
    analysis = lizard.analyze_file.analyze_source_code(file_extension, code)
    total = 0
    for func in analysis.function_list:
        total += func.cyclomatic_complexity
    return total

def normalize_score(raw_value, baseline, threshold):
    """
    Converts a raw value to a 0–1 score:
    - Score = 1 if <= baseline
    - Score = 0 if >= threshold
    - Linearly interpolated in between
    """
    if raw_value <= baseline:
        return 1.0
    elif raw_value >= threshold:
        return 0.0
    else:
        return 1.0 - (raw_value - baseline) / (threshold - baseline)



def detect_code_smells(code, language):
    smells = []
    lines = code.splitlines()
    total_possible_smells = 10  # Update if you add more rules

    for idx, line in enumerate(lines, 1):
        uline = line.strip().upper()

        # ABAP / RAP
        if language in ["abap", "rap"]:
            if "WRITE" in uline:
                smells.append((idx, "Avoid 'WRITE' statement; use modern UI or ALV"))

            if "TRY." not in code.upper() or "CATCH" not in code.upper():
                smells.append((0, "Missing exception handling block (TRY...CATCH)"))  # Global smell

            if line.count('.') > 10:
                smells.append((idx, "Long chained statement (low readability)"))

            if "BAPI_" in uline and "CALL TRANSFORMATION" not in code.upper():
                smells.append((idx, "Obsolete BAPI usage without transformation"))

            if language == "rap":
                if "SELECT" in uline or "OPEN CURSOR" in uline:
                    smells.append((idx, "Direct DB access in RAP logic (should use CDS views)"))

                if "I_" not in code.upper() and "SELECT" in uline:
                    smells.append((idx, "CDS view not reused (missing I_* views)"))

                if "DETERMINATION" not in code.upper() and "VALIDATION" not in code.upper():
                    smells.append((0, "Business logic not modularized via determination/validation"))

                if "@" not in code:
                    smells.append((0, "Missing annotation metadata in RAP artifacts"))

        # SQL
        elif language == "sql":
            if "SELECT *" in uline:
                smells.append((idx, "Avoid SELECT *; specify needed fields"))
            if "WHERE" not in code.upper():
                smells.append((0, "Query missing WHERE clause (may impact performance)"))
            if "JOIN" not in code.upper() and "FROM" in uline:
                smells.append((idx, "No JOIN detected; consider normalized structure"))

        # PLSQL
        elif language == "plsql":
            if "SELECT *" in uline:
                smells.append((idx, "Avoid SELECT * in PLSQL"))
            if "WHEN OTHERS" in uline and "RAISE" not in code.upper() and "LOG" not in code.upper():
                smells.append((idx, "WHEN OTHERS block lacks RAISE or LOG"))
            if "OPEN CURSOR" in uline:
                smells.append((idx, "Avoid cursors in simple queries"))

        # UI5 / JavaScript
        elif language in ["js", "ui5"]:
            if "VAR " in uline:
                smells.append((idx, "Avoid 'var'; use 'let' or 'const'"))
            if "CONSOLE.LOG" in uline:
                smells.append((idx, "Remove console.log from production code"))
            if "FUNCTION(" in uline and "=>" not in uline:
                smells.append((idx, "Consider arrow functions for cleaner structure"))

    # Deduplicate global-level smells (line 0)
    unique_smells = list(dict.fromkeys(smells))

    # Score calculation
    detected_count = len(unique_smells)
    score = max(0.0, 1.0 - (detected_count / total_possible_smells))

    # Build detailed explanation
    explanation_lines = [f"{detected_count} smell(s) found:"]
    for line_num, desc in unique_smells:
        prefix = f"Line {line_num}" if line_num > 0 else "Global"
        explanation_lines.append(f"- {prefix}: {desc}")
    explanation_lines.append(f"Code Smell Score = 1 - ({detected_count} / {total_possible_smells}) = {round(score, 2)}")

    return {
        "score": round(score, 2),
        "explanation": "\n".join(explanation_lines)
    }