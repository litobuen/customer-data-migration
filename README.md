# Customer Data Migration Pipeline

A small Python ETL script that reads messy customer records from a **CSV or JSON** file, cleans and standardizes them with pandas, and writes the result to a **CSV or JSON** file.

Real migration data is rarely clean. This project shows how I handle inconsistent formats, packed fields, and junk values in a repeatable, scriptable way.

## What it does

| Stage | Function | Description |
|-------|----------|-------------|
| Extract | `read_input()` | Reads a `.csv` or `.json` file (format chosen by file extension) |
| Transform | `transform()` | Cleans names, contacts, dates, country codes, and status flags |
| Load | `write_output()` | Writes the cleaned data to `.csv` or `.json` |

### Cleaning rules

- **Names:** trims extra spaces, fixes casing, and flips `Last, First` into `First Last` (`Buen, Lito` becomes `Lito Buen`)
- **Contacts:** when a cell holds several contacts, keeps the email; junk values such as `unknown`, `none`, and `N/A` become empty
- **Dates:** converts mixed formats (`10/02/2026`, `01-Oct-2026`, `2026/09/30`) to `YYYY-MM-DD`; invalid dates become empty
- **Country codes:** trimmed and uppercased
- **Status flag:** converted to an integer; blank values default to `1`
- **User ID:** `106.0` becomes `106`

## Before and after

| Raw name | Raw contact | Raw date | Clean name | Clean contact | Clean date |
|----------|-------------|----------|------------|---------------|------------|
| Buen, Lito | buen.lito@yahoo.com | 2026-10-04 | Lito Buen | buen.lito@yahoo.com | 2026-10-04 |
| john smith | +1-555-0199 | 10/02/2026 | John Smith | +1-555-0199 | 2026-10-02 |
| MARiA sANtOS | maria@gmail.com, 09171234567 | 01-Oct-2026 | Maria Santos | maria@gmail.com | 2026-10-01 |
| ANNA DE GUZMAN | anna.dg@outlook.com | 2026/09/30 | Anna De Guzman | anna.dg@outlook.com | 2026-09-30 |
| David Doe | unknown | N/A | David Doe | *(empty)* | *(empty)* |
| Juan Dela Cruz | 9175551234 | 2026-10-03 | Juan Dela Cruz | 9175551234 | 2026-10-03 |
| Anonymous Owner | none | 2026-10-01 | Anonymous Owner | *(empty)* | 2026-10-01 |

## Requirements

- Python 3.9 or newer
- pandas

```
pip install -r requirements.txt
```

## Usage

```
python migrate.py <input file> <output file>
```

The input and output formats are picked from the file extensions, so any combination works:

```
python migrate.py raw_customers.csv clean_customers.json
python migrate.py raw_customers.json clean_customers.csv
```

### Input format

The file needs these columns (CSV) or keys (JSON, as a list of records):

`user_id`, `full_name`, `contact_info`, `country_code`, `status_flag`, `signup_date`

### Running in Google Colab

Upload `migrate.py` and `raw_customers.csv` using the file panel, then run:

```
!pip install pandas
!python migrate.py raw_customers.csv clean_customers.json
```

## Files

| File | Purpose |
|------|---------|
| `migrate.py` | The pipeline script |
| `raw_customers.csv` / `raw_customers.json` | Sample messy input |
| `clean_customers.csv` / `clean_customers.json` | Sample cleaned output |
| `requirements.txt` | Python dependencies |

## Assumptions and limitations

- Dates like `10/02/2026` are read as month first (October 2).
- Only the first comma in a name is used, so a name with a suffix such as `Smith, John, Jr.` would not be flipped correctly.
- Records are not checked for duplicates.

## Ideas for next steps

- Add validation checks (row counts, date format, two-letter country codes) before writing output
- Load the cleaned data into a SQLite database with an upsert on `user_id`
- Use an LLM to handle edge cases that rules cannot cover
