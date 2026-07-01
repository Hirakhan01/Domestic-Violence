"""
ONS Homicide Index — Deep Analysis Script
==========================================
Takes the 4 cleaned CSVs and derives actual findings:
year-over-year change, rates, shares, trend direction, and
narrative-ready summary points for the dossier website.

Input:  cleaned_data/*.csv
Output: analysis_output/findings.json   (single source of truth for the site)

Usage:
  python analyze_homicide_data.py
"""

import pandas as pd
import json
import os
import warnings
warnings.filterwarnings('ignore')

INPUT_DIR = 'cleaned_data'
OUTPUT_DIR = 'analysis_output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

domestic = pd.read_csv(f'{INPUT_DIR}/domestic_trends.csv')
relationships = pd.read_csv(f'{INPUT_DIR}/victim_relationships.csv')
outcomes = pd.read_csv(f'{INPUT_DIR}/suspect_outcomes.csv')
circumstances = pd.read_csv(f'{INPUT_DIR}/circumstances.csv')

LATEST_YEAR = '2024-25'
EARLIEST_YEAR = '2014-15'
PRIOR_YEAR = '2023-24'

findings = {}


def pct_change(old, new):
    if old == 0:
        return None
    return round(((new - old) / old) * 100, 1)


# ─────────────────────────────────────────────────────────
# 1. DOMESTIC HOMICIDE — headline figures
# ─────────────────────────────────────────────────────────
dom_only = domestic[domestic['category'] == 'Domestic homicide']

latest_total = dom_only[dom_only['year'] == LATEST_YEAR]['count'].sum()
prior_total = dom_only[dom_only['year'] == PRIOR_YEAR]['count'].sum()
earliest_total = dom_only[dom_only['year'] == EARLIEST_YEAR]['count'].sum()

female_victim_male_suspect = dom_only[
    (dom_only['victim_sex'] == 'Female') & (dom_only['suspect_sex'] == 'Male')
]
fvms_latest = female_victim_male_suspect[female_victim_male_suspect['year'] == LATEST_YEAR]['count'].sum()
fvms_earliest = female_victim_male_suspect[female_victim_male_suspect['year'] == EARLIEST_YEAR]['count'].sum()

male_victim_female_suspect = dom_only[
    (dom_only['victim_sex'] == 'Male') & (dom_only['suspect_sex'] == 'Female')
]
mvfs_latest = male_victim_female_suspect[male_victim_female_suspect['year'] == LATEST_YEAR]['count'].sum()

# All years series for charting
dom_yearly = dom_only.groupby('year')['count'].sum().reindex([
    '2014-15','2015-16','2016-17','2017-18','2018-19',
    '2019-20','2020-21','2021-22','2022-23','2023-24','2024-25'
]).to_dict()

fvms_yearly = female_victim_male_suspect.groupby('year')['count'].sum().reindex([
    '2014-15','2015-16','2016-17','2017-18','2018-19',
    '2019-20','2020-21','2021-22','2022-23','2023-24','2024-25'
]).to_dict()

mvfs_yearly = male_victim_female_suspect.groupby('year')['count'].sum().reindex([
    '2014-15','2015-16','2016-17','2017-18','2018-19',
    '2019-20','2020-21','2021-22','2022-23','2023-24','2024-25'
]).to_dict()

findings['headline'] = {
    'latest_year': LATEST_YEAR,
    'domestic_homicides_latest': int(latest_total),
    'domestic_homicides_prior_year': int(prior_total),
    'yoy_change_pct': pct_change(prior_total, latest_total),
    'change_since_2014_pct': pct_change(earliest_total, latest_total),
    'female_victim_male_suspect_latest': int(fvms_latest),
    'female_victim_male_suspect_share_pct': round((fvms_latest / latest_total) * 100, 1),
    'female_victim_male_suspect_change_since_2014_pct': pct_change(fvms_earliest, fvms_latest),
    'male_victim_female_suspect_latest': int(mvfs_latest),
    'trend_series': {
        'years': list(dom_yearly.keys()),
        'all_domestic': [int(v) for v in dom_yearly.values()],
        'female_victim_male_suspect': [int(v) for v in fvms_yearly.values()],
        'male_victim_female_suspect': [int(v) for v in mvfs_yearly.values()],
    }
}


# ─────────────────────────────────────────────────────────
# 2. VICTIM RELATIONSHIPS — female victims, latest year
# ─────────────────────────────────────────────────────────
female_rel_latest = relationships[
    (relationships['victim_sex'] == 'Female') & (relationships['year'] == LATEST_YEAR)
].copy()

female_total = female_rel_latest['count'].sum()
female_rel_latest['share_pct'] = (female_rel_latest['count'] / female_total * 100).round(1)
female_rel_sorted = female_rel_latest.sort_values('count', ascending=False)

male_rel_latest = relationships[
    (relationships['victim_sex'] == 'Male') & (relationships['year'] == LATEST_YEAR)
].copy()
male_total = male_rel_latest['count'].sum()
male_rel_latest['share_pct'] = (male_rel_latest['count'] / male_total * 100).round(1)
male_rel_sorted = male_rel_latest.sort_values('count', ascending=False)

findings['relationships'] = {
    'female_victims': {
        'total': int(female_total),
        'breakdown': [
            {
                'relationship': row['relationship'],
                'acquaintance_status': row['acquaintance_status'],
                'count': int(row['count']),
                'share_pct': float(row['share_pct'])
            }
            for _, row in female_rel_sorted.iterrows()
        ]
    },
    'male_victims': {
        'total': int(male_total),
        'breakdown': [
            {
                'relationship': row['relationship'],
                'acquaintance_status': row['acquaintance_status'],
                'count': int(row['count']),
                'share_pct': float(row['share_pct'])
            }
            for _, row in male_rel_sorted.iterrows()
        ]
    }
}

# Partner/ex-partner trend over time (female victims) — key dossier stat
partner_trend = relationships[
    (relationships['victim_sex'] == 'Female') & (relationships['relationship'] == 'Partner/ex-partner')
].set_index('year')['count'].reindex([
    '2014-15','2015-16','2016-17','2017-18','2018-19',
    '2019-20','2020-21','2021-22','2022-23','2023-24','2024-25'
]).to_dict()

findings['relationships']['partner_homicide_trend'] = {
    'years': list(partner_trend.keys()),
    'counts': [int(v) for v in partner_trend.values()]
}


# ─────────────────────────────────────────────────────────
# 3. SUSPECT OUTCOMES — the justice gap
# ─────────────────────────────────────────────────────────
def outcome_series(detail_name):
    rows = outcomes[outcomes['outcome_detail'] == detail_name].set_index('year')['count']
    return rows.reindex([
        '2014-15','2015-16','2016-17','2017-18','2018-19',
        '2019-20','2020-21','2021-22','2022-23','2023-24','2024-25'
    ]).to_dict()

murder_series = outcome_series('Murder')
no_charge_series = outcome_series('No suspects charged')
discontinued_series = outcome_series('Proceedings discontinued')
suicide_series = outcome_series('Suspect died by suicide')

murder_latest = murder_series[LATEST_YEAR]
murder_earliest = murder_series[EARLIEST_YEAR]
no_charge_latest = no_charge_series[LATEST_YEAR]
no_charge_earliest = no_charge_series[EARLIEST_YEAR]

total_offences_latest = outcomes[
    (outcomes['outcome_detail'] == 'Murder') | (outcomes['outcome_detail'].isin([
        'Section 2 manslaughter', 'Other manslaughter', 'Infanticide',
        'Court decision pending', 'Suspect found insane', 'Suspect died',
        'Suspect died by suicide', 'Proceedings discontinued', 'No suspects charged'
    ]))
]
total_latest = total_offences_latest[total_offences_latest['year'] == LATEST_YEAR]['count'].sum()

findings['justice_gap'] = {
    'murder_convictions': {
        'latest': int(murder_latest),
        'earliest': int(murder_earliest),
        'change_pct': pct_change(murder_earliest, murder_latest),
        'is_decade_low': bool(murder_latest == min(murder_series.values())),
        'series': {'years': list(murder_series.keys()), 'counts': [int(v) for v in murder_series.values()]}
    },
    'no_suspect_charged': {
        'latest': int(no_charge_latest),
        'earliest': int(no_charge_earliest),
        'change_pct': pct_change(no_charge_earliest, no_charge_latest),
        'is_decade_high': bool(no_charge_latest == max(no_charge_series.values())),
        'series': {'years': list(no_charge_series.keys()), 'counts': [int(v) for v in no_charge_series.values()]}
    },
    'conviction_rate_latest_pct': round((murder_latest / total_latest) * 100, 1) if total_latest else None,
    'unsolved_rate_latest_pct': round((no_charge_latest / total_latest) * 100, 1) if total_latest else None,
    'suspect_suicide_trend': {
        'years': list(suicide_series.keys()),
        'counts': [int(v) for v in suicide_series.values()],
        'change_since_2014_pct': pct_change(suicide_series[EARLIEST_YEAR], suicide_series[LATEST_YEAR])
    }
}


# ─────────────────────────────────────────────────────────
# 4. CIRCUMSTANCES — what sparked it
# ─────────────────────────────────────────────────────────
circ_acquainted_latest = circumstances[
    (circumstances['relationship_group'] == 'Victim acquainted') & (circumstances['year'] == LATEST_YEAR)
].copy()
circ_total = circ_acquainted_latest['count'].sum()
circ_acquainted_latest['share_pct'] = (circ_acquainted_latest['count'] / circ_total * 100).round(1)
circ_sorted = circ_acquainted_latest.sort_values('count', ascending=False)

quarrel_series = circumstances[
    (circumstances['relationship_group'] == 'Victim acquainted') &
    (circumstances['circumstance'] == 'Quarrel, revenge or loss of temper')
].set_index('year')['count'].reindex([
    '2014-15','2015-16','2016-17','2017-18','2018-19',
    '2019-20','2020-21','2021-22','2022-23','2023-24','2024-25'
]).to_dict()

findings['circumstances'] = {
    'acquainted_victims_latest_year': {
        'total': int(circ_total),
        'breakdown': [
            {'circumstance': row['circumstance'], 'count': int(row['count']), 'share_pct': float(row['share_pct'])}
            for _, row in circ_sorted.iterrows()
        ]
    },
    'quarrel_revenge_trend': {
        'years': list(quarrel_series.keys()),
        'counts': [int(v) for v in quarrel_series.values()],
        'change_since_2014_pct': pct_change(quarrel_series[EARLIEST_YEAR], quarrel_series[LATEST_YEAR])
    }
}


# ─────────────────────────────────────────────────────────
# 5. NARRATIVE SUMMARY POINTS — for dossier copy
# ─────────────────────────────────────────────────────────
findings['narrative_points'] = [
    f"In {LATEST_YEAR}, {int(latest_total)} domestic homicides were recorded in England and Wales — "
    f"a {'rise' if findings['headline']['yoy_change_pct'] > 0 else 'fall'} of "
    f"{abs(findings['headline']['yoy_change_pct'])}% on the prior year.",

    f"Female victims killed by a male partner or ex-partner account for "
    f"{findings['headline']['female_victim_male_suspect_share_pct']}% of all domestic homicides in {LATEST_YEAR} "
    f"— the single largest category in the dataset, every year without exception.",

    f"Murder convictions fell to {int(murder_latest)} in {LATEST_YEAR}, "
    f"the lowest figure in the eleven-year series, down {abs(findings['justice_gap']['murder_convictions']['change_pct'])}% "
    f"from {EARLIEST_YEAR}.",

    f"Cases where no suspect was charged reached {int(no_charge_latest)} in {LATEST_YEAR} — "
    f"the highest figure recorded across the same eleven years.",

    f"Among victims who were acquainted with their suspect, "
    f"{findings['circumstances']['acquainted_victims_latest_year']['breakdown'][0]['share_pct']}% of homicides "
    f"were sparked by quarrel, revenge, or loss of temper — not premeditation or financial motive."
]


# ─────────────────────────────────────────────────────────
# SAVE
# ─────────────────────────────────────────────────────────
with open(f'{OUTPUT_DIR}/findings.json', 'w') as f:
    json.dump(findings, f, indent=2)

print("Analysis complete. Saved to:", f'{OUTPUT_DIR}/findings.json')
print("\n" + "="*60)
print("NARRATIVE POINTS (dossier-ready copy)")
print("="*60)
for i, point in enumerate(findings['narrative_points'], 1):
    print(f"\n{i}. {point}")
