import csv
import os

def write_report(results, mode):
    """
    Writes output CSV with UTF-8 encoding.
    Filename includes the mode.
    """
    out_path = f"output/{mode}_report.csv"
    os.makedirs("output", exist_ok=True)

    with open(out_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        for row in results:
            writer.writerow(row)
