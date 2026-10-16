"""
File-based migration pipeline: read CSV/JSON -> clean -> write CSV/JSON.

Usage:
    python migrate.py raw_customers.csv clean_customers.json
    python migrate.py raw_customers.json clean_customers.csv
"""
import argparse
import json
from pathlib import Path

import pandas as pd

EMPTY_VALUES = {"", "unknown", "none", "nan", "null", "n/a"}


# ---------- EXTRACT ----------
def read_input(path):
    """Read a .csv or .json file into a DataFrame (everything as raw text/values)."""
    ext = Path(path).suffix.lower()
    if ext == ".csv":
        # dtype=str + keep_default_na=False keeps the raw text so WE decide what's "missing"
        return pd.read_csv(path, dtype=str, keep_default_na=False)
    if ext == ".json":
        with open(path, encoding="utf-8") as f:
            return pd.DataFrame(json.load(f))  # expects a list of records
    raise ValueError(f"Unsupported input type '{ext}'. Use .csv or .json")


# ---------- TRANSFORM ----------
def parse_contact(value):
    """Prefer an email if several contacts are packed in one cell; blank out junk values."""
    text = str(value).strip()
    if text.lower() in EMPTY_VALUES:
        return None
    if "@" in text:
        for part in (p.strip() for p in text.split(",")):
            if "@" in part:
                return part
    return text


def parse_date(value):
    """Parse one date string in any common format -> 'YYYY-MM-DD', or None if invalid."""
    parsed = pd.to_datetime(str(value).strip(), errors="coerce")
    return None if pd.isna(parsed) else parsed.strftime("%Y-%m-%d")


def normalize_name(value):
    """Clean a name and flip 'Last, First' into 'First Last'.

    A comma means the part before it is the surname and the part after it is
    the first name(s): 'Buen, Lito' -> 'Lito Buen'.
    """
    text = " ".join(str(value).split())  # trim and collapse extra spaces
    if "," in text:
        last, first = (p.strip() for p in text.split(",", 1))
        if last and first:
            text = f"{first} {last}"
        else:
            text = text.replace(",", "").strip()  # stray comma, just remove it
    return text.title()


def transform(df):
    df = df.copy()
    df["user_id"] = pd.to_numeric(df["user_id"], errors="coerce").astype("Int64")
    df["full_name"] = df["full_name"].apply(normalize_name)
    df["contact_info"] = df["contact_info"].apply(parse_contact)
    df["country_code"] = df["country_code"].astype(str).str.strip().str.upper()
    df["status_flag"] = pd.to_numeric(df["status_flag"], errors="coerce").fillna(1).astype(int)
    df["signup_date"] = df["signup_date"].apply(parse_date)
    return df


# ---------- LOAD ----------
def write_output(df, path):
    """Write the cleaned DataFrame to .csv or .json."""
    ext = Path(path).suffix.lower()
    if ext == ".csv":
        df.to_csv(path, index=False)
    elif ext == ".json":
        df.to_json(path, orient="records", indent=2)
    else:
        raise ValueError(f"Unsupported output type '{ext}'. Use .csv or .json")


def main():
    parser = argparse.ArgumentParser(description="Clean a messy user file.")
    parser.add_argument("input", help="Path to input .csv or .json")
    parser.add_argument("output", help="Path to output .csv or .json")
    args = parser.parse_args()

    raw = read_input(args.input)
    print(f"--- STEP 1: READ {len(raw)} rows from {args.input} ---")
    print(raw[["user_id", "full_name", "signup_date"]])

    clean = transform(raw)
    print("\n--- STEP 2: TRANSFORMED DATA ---")
    print(clean[["user_id", "full_name", "signup_date", "contact_info"]])

    write_output(clean, args.output)
    print(f"\n--- STEP 3: SUCCESS! Wrote {len(clean)} rows to {args.output} ---")


if __name__ == "__main__":
    main()
