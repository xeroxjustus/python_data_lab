
import csv
from collections import Counter

INPUT = "ai_models.csv"
OUTPUT = "us_ai_models.csv"

# Backup list, used only if the file has no country column
US_COMPANIES = ["OpenAI", "Anthropic", "Meta", "Microsoft", "NVIDIA",
                "xAI", "Google", "Amazon", "Apple", "IBM",
                "Salesforce", "Databricks"]


def find_country_column(fieldnames):
    for name in fieldnames:
        if "country" in name.lower():
            return name
    return None


def is_american(row, country_col):
    if country_col:
        country = row.get(country_col, "").lower()
        return "united states" in country or country.strip() in ("usa", "us")
    org = row.get("Organization", "").lower()
    return any(c.lower() in org for c in US_COMPANIES)


def to_billions(value):
    try:
        return round(float(value) / 1e9, 3)
    except ValueError:
        return ""


def main():
    with open(INPUT, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames or []

        needed = ["Organization", "Model", "Publication date", "Parameters"]
        missing = [c for c in needed if c not in fields]
        if missing:
            print("Missing columns:", missing)
            print("Columns found:", fields)
            return

        country_col = find_country_column(fields)
        if country_col:
            print("Using country column:", country_col)
        else:
            print("No country column found, using the company list")

        total = 0
        results = []
        for row in reader:
            total += 1
            if not is_american(row, country_col):
                continue
            params = row["Parameters"].strip()
            if not params:
                continue
            results.append({
                "Organization": row["Organization"].strip(),
                "Model": row["Model"].strip(),
                "Publication date": row["Publication date"].strip(),
                "Parameters": params,
                "Parameters (billions)": to_billions(params),
            })

    results.sort(key=lambda r: (r["Organization"], r["Publication date"]))

    columns = ["Organization", "Model", "Publication date",
               "Parameters", "Parameters (billions)"]
    with open(OUTPUT, "w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=columns)
        writer.writeheader()
        writer.writerows(results)

    print(f"Read {total} models, kept {len(results)} American models with parameters")
    print("Top companies:")
    for org, n in Counter(r["Organization"] for r in results).most_common(8):
        print(f"  {org}: {n}")


main()
