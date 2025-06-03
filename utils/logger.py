import csv
import os
import logging

def write_report(results, mode):
    """
    Writes output CSV with UTF-8 encoding.
    Filename includes the mode.
    Logs each step for traceability.
    """
    out_path = f"output/{mode}_report.csv"
    os.makedirs("output", exist_ok=True)

    try:
        logging.info(f"📄 Writing report for {mode} to {out_path}")
        with open(out_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            for row in results:
                writer.writerow(row)
        logging.info(f"✅ Report saved: {out_path}")
    except Exception as e:
        logging.error(f"❌ Failed to write report for {mode}: {e}")
