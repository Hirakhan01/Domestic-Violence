"""
ONS Homicide Index — Data Cleaning Script
==========================================
Source: homicideinenglandandwalesappendixtablesyemar2025finalv2.xlsx
Output: 4 clean CSVs ready for Power BI

CSVs produced:
  1. domestic_trends.csv        — from Table 34
  2. victim_relationships.csv   — from Worksheet 14
  3. suspect_outcomes.csv       — from Table 25
  4. circumstances.csv          — from Worksheet 17

Usage:
  pip install pandas openpyxl
  python clean_homicide_data.py
"""

import pandas as pd
import re
import os
import warnings
warnings.filterwarnings('ignore')

SOURCE_FILE = 'homicideinenglandandwalesappendixtablesyemar2025finalv2.xlsx'
OUTPUT_DIR = 'cleaned_data'

os.makedirs(OUTPUT_DIR, exist_ok=True)

xl = pd.ExcelFile(SOURCE_FILE)

YEAR_LABELS = [
    '2014-15', '2015-16', '2016-17', '2017-18', '2018-19',
    '2019-20', '2020-21', '2021-22', '2022-23', '2023-24', '2024-25'
]

def clean_text(val):
    """Strip footnote references like [note 12], [x], extra whitespace."""
    val = str(val).strip()
    val = re.sub(r'\[note[s]?\s?\d+,?\d*\]', '', val)
    val = re.sub(r'\[Notes?\s[\d,]+\]', '', val)
    val = re.sub(r'\[\d+\]', '', val)
    val = val.replace('[x]', '0')
    val = re.sub(r'\s+', ' ', val).strip()
    return val

def to_int(val):
    """Safely convert to integer, return 0 if not possible."""
    try:
        return int(float(str(val).strip()))
    except (ValueError, TypeError):
        return 0


# ─────────────────────────────────────────────────────────
# 1. DOMESTIC TRENDS  (Table 34)
#    Columns: category, victim_sex, suspect_sex, year, count
# ─────────────────────────────────────────────────────────
print("Processing Table 34 — Domestic trends...")

df34 = pd.read_excel(xl, sheet_name='Table 34', header=None)

DATA_ROWS = {
    7:  ('Domestic homicide',          'Male',   'Male'),
    8:  ('Domestic homicide',          'Male',   'Female'),
    9:  ('Domestic homicide',          'Female', 'Male'),
    10: ('Domestic homicide',          'Female', 'Female'),
    12: ('Non-domestic (16+)',         'Male',   'Male'),
    13: ('Non-domestic (16+)',         'Male',   'Female'),
    14: ('Non-domestic (16+)',         'Female', 'Male'),
    15: ('Non-domestic (16+)',         'Female', 'Female'),
    17: ('Non-domestic (under 16)',    'Male',   'Male'),
    18: ('Non-domestic (under 16)',    'Male',   'Female'),
    19: ('Non-domestic (under 16)',    'Female', 'Male'),
    20: ('Non-domestic (under 16)',    'Female', 'Female'),
}

records = []
for row_idx, (category, victim_sex, suspect_sex) in DATA_ROWS.items():
    row = df34.iloc[row_idx]
    counts = [to_int(row[col]) for col in range(3, 14)]
    for year, count in zip(YEAR_LABELS, counts):
        records.append({
            'category':    category,
            'victim_sex':  victim_sex,
            'suspect_sex': suspect_sex,
            'year':        year,
            'count':       count
        })

domestic_trends = pd.DataFrame(records)
domestic_trends.to_csv(f'{OUTPUT_DIR}/domestic_trends.csv', index=False)
print(f"  Saved domestic_trends.csv — {len(domestic_trends)} rows")


# ─────────────────────────────────────────────────────────
# 2. VICTIM RELATIONSHIPS  (Worksheet 14 — Table 14a only)
#    Columns: victim_sex, acquaintance_status, relationship, year, count
# ─────────────────────────────────────────────────────────
print("Processing Worksheet 14 — Victim relationships...")

df14 = pd.read_excel(xl, sheet_name='Worksheet 14', header=None)

# Table 14a (counts) rows 8–31, columns 0=sex, 1=acquaintance, 2=relationship, 3-13=years
# Stop before row 44 where Table 14b (percentages) begins
RELATIONSHIP_ROWS = {
    8:  ('Male',   'Acquainted',     'Son or daughter'),
    9:  ('Male',   'Acquainted',     'Parent'),
    10: ('Male',   'Acquainted',     'Partner/ex-partner'),
    11: ('Male',   'Acquainted',     'Other family'),
    12: ('Male',   'Acquainted',     'Friend/acquaintance'),
    13: ('Male',   'Acquainted',     'Other'),
    15: ('Male',   'Not acquainted', 'Stranger'),
    16: ('Male',   'Not acquainted', 'Relationship not known'),
    17: ('Male',   'Not acquainted', 'No suspect charged'),
    20: ('Female', 'Acquainted',     'Son or daughter'),
    21: ('Female', 'Acquainted',     'Parent'),
    22: ('Female', 'Acquainted',     'Partner/ex-partner'),
    23: ('Female', 'Acquainted',     'Other family'),
    24: ('Female', 'Acquainted',     'Friend/acquaintance'),
    25: ('Female', 'Acquainted',     'Other'),
    27: ('Female', 'Not acquainted', 'Stranger'),
    28: ('Female', 'Not acquainted', 'Relationship not known'),
    29: ('Female', 'Not acquainted', 'No suspect charged'),
}

records = []
for row_idx, (victim_sex, acquaintance_status, relationship) in RELATIONSHIP_ROWS.items():
    row = df14.iloc[row_idx]
    counts = [to_int(row[col]) for col in range(3, 14)]
    for year, count in zip(YEAR_LABELS, counts):
        records.append({
            'victim_sex':          victim_sex,
            'acquaintance_status': acquaintance_status,
            'relationship':        relationship,
            'year':                year,
            'count':               count
        })

victim_relationships = pd.DataFrame(records)
victim_relationships.to_csv(f'{OUTPUT_DIR}/victim_relationships.csv', index=False)
print(f"  Saved victim_relationships.csv — {len(victim_relationships)} rows")


# ─────────────────────────────────────────────────────────
# 3. SUSPECT OUTCOMES  (Table 25)
#    Columns: outcome_group, outcome_detail, year, count
# ─────────────────────────────────────────────────────────
print("Processing Table 25 — Suspect outcomes...")

df25 = pd.read_excel(xl, sheet_name='Table 25', header=None)

OUTCOME_ROWS = {
    9:  ('Convicted at court',      'Murder'),
    10: ('Convicted at court',      'Section 2 manslaughter'),
    11: ('Convicted at court',      'Other manslaughter'),
    12: ('Convicted at court',      'Infanticide'),
    14: ('Pending/unresolved',      'Court decision pending'),
    15: ('Proceedings not pursued', 'Suspect found insane'),
    16: ('Proceedings not pursued', 'Suspect died'),
    17: ('Proceedings not pursued', 'Suspect died by suicide'),
    18: ('Proceedings not pursued', 'Proceedings discontinued'),
    20: ('No justice',              'No suspects charged'),
}

# Rows 14 and 20 have no "detail" column — col 1 is blank (nan), years start at col 2, same as all other rows
records = []
for row_idx, (outcome_group, outcome_detail) in OUTCOME_ROWS.items():
    row = df25.iloc[row_idx]
    counts = [to_int(row[col]) for col in range(2, 13)]
    for year, count in zip(YEAR_LABELS, counts):
        records.append({
            'outcome_group':  outcome_group,
            'outcome_detail': outcome_detail,
            'year':           year,
            'count':          count
        })

suspect_outcomes = pd.DataFrame(records)
suspect_outcomes.to_csv(f'{OUTPUT_DIR}/suspect_outcomes.csv', index=False)
print(f"  Saved suspect_outcomes.csv — {len(suspect_outcomes)} rows")


# ─────────────────────────────────────────────────────────
# 4. CIRCUMSTANCES  (Worksheet 17 — Table 17a counts only)
#    Columns: relationship_group, circumstance, year, count
# ─────────────────────────────────────────────────────────
print("Processing Worksheet 17 — Circumstances...")

df17 = pd.read_excel(xl, sheet_name='Worksheet 17', header=None)

CIRCUMSTANCE_ROWS = {
    9:  ('Victim acquainted',     'Quarrel, revenge or loss of temper'),
    10: ('Victim acquainted',     'In furtherance of theft or gain'),
    11: ('Victim acquainted',     'Terrorism'),
    12: ('Victim acquainted',     'Restraint/arrest attempt'),
    13: ('Victim acquainted',     'Arson'),
    14: ('Victim acquainted',     'Other circumstances'),
    15: ('Victim acquainted',     'Irrational act'),
    16: ('Victim acquainted',     'Not known'),
    18: ('Victim not acquainted', 'Quarrel, revenge or loss of temper'),
    19: ('Victim not acquainted', 'In furtherance of theft or gain'),
    20: ('Victim not acquainted', 'Terrorism'),
    21: ('Victim not acquainted', 'Restraint/arrest attempt'),
    22: ('Victim not acquainted', 'Arson'),
    23: ('Victim not acquainted', 'Other circumstances'),
    24: ('Victim not acquainted', 'Irrational act'),
    25: ('Victim not acquainted', 'Not known'),
    27: ('All victims',           'Quarrel, revenge or loss of temper'),
    28: ('All victims',           'In furtherance of theft or gain'),
    29: ('All victims',           'Terrorism'),
    30: ('All victims',           'Restraint/arrest attempt'),
    31: ('All victims',           'Arson'),
    32: ('All victims',           'Other circumstances'),
    33: ('All victims',           'Irrational act'),
    34: ('All victims',           'Not known'),
}

records = []
for row_idx, (relationship_group, circumstance) in CIRCUMSTANCE_ROWS.items():
    row = df17.iloc[row_idx]
    raw_vals = [str(row[col]).strip() for col in range(2, 13)]
    counts = [0 if v in ['[x]', 'nan', 'None', ''] else to_int(v) for v in raw_vals]
    for year, count in zip(YEAR_LABELS, counts):
        records.append({
            'relationship_group': relationship_group,
            'circumstance':       circumstance,
            'year':               year,
            'count':              count
        })

circumstances = pd.DataFrame(records)
circumstances.to_csv(f'{OUTPUT_DIR}/circumstances.csv', index=False)
print(f"  Saved circumstances.csv — {len(circumstances)} rows")


# ─────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────
print("\n" + "="*50)
print("All done. Files saved to:", OUTPUT_DIR)
print("="*50)
for fname in os.listdir(OUTPUT_DIR):
    fpath = os.path.join(OUTPUT_DIR, fname)
    df = pd.read_csv(fpath)
    print(f"  {fname}: {len(df)} rows, {len(df.columns)} columns — {list(df.columns)}")
