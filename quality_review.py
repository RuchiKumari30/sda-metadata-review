"""
quality_review.py
-----------------
Section 1: Metadata Quality Review
State Data Authority – UP Metadata Platform Assignment

This script reads metadata_submissions.csv, applies a set of quality checks
defined by the SDA, and produces:
  - data/processed/quality_flags.csv  : submissions with one or more issues
  - data/processed/clean_submissions.csv : submissions that pass all checks
  - data/processed/review_summary.txt : plain-text data quality report

Author : [Student Name]
Date   : June 2026
"""

import pandas as pd
import re
import os
from datetime import datetime

# ── paths ──────────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR  = os.path.join(BASE_DIR, "data")
OUT_DIR   = os.path.join(DATA_DIR, "processed")
os.makedirs(OUT_DIR, exist_ok=True)

SUBMISSIONS_FILE  = os.path.join(DATA_DIR, "metadata_submissions.csv")
TRACKER_FILE      = os.path.join(DATA_DIR, "compliance_tracker.csv")
FLAGS_OUT         = os.path.join(OUT_DIR,  "quality_flags.csv")
CLEAN_OUT         = os.path.join(OUT_DIR,  "clean_submissions.csv")
SUMMARY_OUT       = os.path.join(OUT_DIR,  "review_summary.txt")

# ── load data ──────────────────────────────────────────────────────────────────
df = pd.read_csv(SUBMISSIONS_FILE, dtype=str)
df = df.fillna("")   # treat NaN as empty string for consistency

print(f"Loaded {len(df)} submissions from {SUBMISSIONS_FILE}")

# ── helper functions ───────────────────────────────────────────────────────────

VALID_CLASSIFICATIONS = {"Public", "Restricted", "Confidential"}
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def is_valid_date(date_str):
    """Return True if date_str matches YYYY-MM-DD and is a real calendar date."""
    if not DATE_PATTERN.match(date_str.strip()):
        return False
    try:
        datetime.strptime(date_str.strip(), "%Y-%m-%d")
        return True
    except ValueError:
        return False


def is_live_api(row):
    """Return True if the dataset is a live API (formats field contains 'API')."""
    return "API" in str(row.get("formats", "")).upper()


# ── quality checks ─────────────────────────────────────────────────────────────

def run_quality_checks(df):
    """
    Apply all SDA quality checks to every row.
    Returns a list of dicts with submission_id, department, dataset_title, issues.
    """
    flagged = []

    for _, row in df.iterrows():
        issues = []

        # Check 1: Data owner present
        if not row["data_owner_name"].strip():
            issues.append("Missing data owner name")

        # Check 2: Description adequate (not blank, at least 20 characters)
        desc = row["description"].strip()
        if not desc:
            issues.append("Description is blank")
        elif len(desc) < 20:
            issues.append("Description too short (< 20 characters)")

        # Check 3: Classification present and valid
        classification = row["data_classification"].strip()
        if not classification:
            issues.append("Data classification is blank")
        elif classification not in VALID_CLASSIFICATIONS:
            issues.append(f"Invalid classification value: '{classification}'")

        # Check 4: DPDP flag consistent
        # If personal data = Yes, classification must be Restricted or Confidential
        dpdp = row["dpdp_personal_data"].strip()
        if dpdp.lower() == "yes":
            if classification not in {"Restricted", "Confidential"}:
                issues.append(
                    "DPDP inconsistency: personal data marked Yes but classification is not Restricted/Confidential"
                )

        # Check 5: last_updated date format (must be YYYY-MM-DD)
        last_updated = row["last_updated"].strip()
        if last_updated and not is_valid_date(last_updated):
            issues.append(f"last_updated date format invalid: '{last_updated}' (expected YYYY-MM-DD)")

        # Check 6: record_count – blank is OK only for live API datasets
        rc = row["record_count"].strip()
        if not rc:
            if not is_live_api(row):
                issues.append("Record count is blank (dataset is not a live API)")
        else:
            try:
                val = int(float(rc))
                if val <= 0:
                    issues.append("Record count must be a positive integer")
            except ValueError:
                issues.append(f"Record count is not a valid integer: '{rc}'")

        # Check 7: submitted_on date format (must be YYYY-MM-DD)
        submitted_on = row["submitted_on"].strip()
        if not is_valid_date(submitted_on):
            issues.append(
                f"submitted_on date format invalid: '{submitted_on}' (expected YYYY-MM-DD)"
            )

        if issues:
            flagged.append({
                "submission_id":  row["submission_id"],
                "department":     row["department"],
                "dataset_title":  row["dataset_title"],
                "issues":         "; ".join(issues),
            })

    return flagged


# ── run checks ─────────────────────────────────────────────────────────────────
flagged_records = run_quality_checks(df)
flagged_ids     = {r["submission_id"] for r in flagged_records}
clean_df        = df[~df["submission_id"].isin(flagged_ids)].copy()
flags_df        = pd.DataFrame(flagged_records)

print(f"\nResults:")
print(f"  Submissions with issues : {len(flags_df)}")
print(f"  Clean submissions       : {len(clean_df)}")

# ── save outputs ───────────────────────────────────────────────────────────────
flags_df.to_csv(FLAGS_OUT, index=False)
clean_df.to_csv(CLEAN_OUT, index=False)
print(f"\nSaved quality flags  -> {FLAGS_OUT}")
print(f"Saved clean records  -> {CLEAN_OUT}")

# ── 1.2 cross-check with compliance tracker ────────────────────────────────────
tracker = pd.read_csv(TRACKER_FILE, dtype=str).fillna("")

# strip any leading/trailing spaces from final_status
tracker["final_status"] = tracker["final_status"].str.strip()

approved_in_tracker = set(
    tracker[tracker["final_status"] == "Approved"]["submission_id"]
)
pending_in_tracker  = set(
    tracker[tracker["final_status"].str.startswith("Pending")]["submission_id"]
)

# Mis-approved: flagged by our checks but tracker says Approved
mis_approved = flagged_ids & approved_in_tracker

# Potentially ready: tracker says Pending but we found no issues
# (i.e. not in flagged_ids)
potentially_ready = pending_in_tracker - flagged_ids

correctly_approved = (set(df["submission_id"]) - flagged_ids) & approved_in_tracker
correctly_pending  = flagged_ids & pending_in_tracker

print("\n-- Cross-check with compliance tracker ------------------------------")
print(f"  Correctly Approved      : {len(correctly_approved)}")
print(f"  Correctly Pending       : {len(correctly_pending)}")
print(f"  Potentially Mis-Approved: {len(mis_approved)}")
if mis_approved:
    print(f"    IDs: {', '.join(sorted(mis_approved))}")
print(f"  Potentially Ready to Approve: {len(potentially_ready)}")
if potentially_ready:
    print(f"    IDs: {', '.join(sorted(potentially_ready))}")

# ── build issue type frequency table ──────────────────────────────────────────
all_issues = []
for row in flagged_records:
    for issue in row["issues"].split(";"):
        issue = issue.strip()
        if issue:
            all_issues.append(issue)

from collections import Counter
issue_counts = Counter(all_issues)

# ── write review_summary.txt ───────────────────────────────────────────────────
with open(SUMMARY_OUT, "w", encoding="utf-8") as f:
    f.write("=" * 60 + "\n")
    f.write("  SDA METADATA PLATFORM – DATA QUALITY REVIEW SUMMARY\n")
    f.write("  Generated: {}\n".format(datetime.now().strftime("%Y-%m-%d %H:%M")))
    f.write("=" * 60 + "\n\n")

    f.write(f"Total submissions received : {len(df)}\n")
    f.write(f"Submissions passing checks : {len(clean_df)}\n")
    f.write(f"Submissions with issues    : {len(flags_df)}\n\n")

    f.write("PASS RATE: {:.1f}%\n\n".format(100 * len(clean_df) / len(df)))

    f.write("── MOST COMMON ISSUE TYPES ─────────────────────────────\n")
    for issue, count in issue_counts.most_common():
        f.write(f"  [{count:2d}]  {issue}\n")

    f.write("\n── CROSS-CHECK WITH COMPLIANCE TRACKER ─────────────────\n")
    f.write(f"  Correctly Approved       : {len(correctly_approved)}\n")
    f.write(f"  Correctly Pending        : {len(correctly_pending)}\n")
    f.write(f"  Potentially Mis-Approved : {len(mis_approved)}\n")
    if mis_approved:
        f.write(f"    -> {', '.join(sorted(mis_approved))}\n")
    f.write(f"  Potentially Ready to Approve: {len(potentially_ready)}\n")
    if potentially_ready:
        f.write(f"    -> {', '.join(sorted(potentially_ready))}\n")

    f.write("\n── FLAGGED SUBMISSIONS DETAIL ───────────────────────────\n")
    for rec in flagged_records:
        f.write(f"\n  {rec['submission_id']} | {rec['department']}\n")
        f.write(f"  Dataset : {rec['dataset_title']}\n")
        f.write(f"  Issues  : {rec['issues']}\n")

    f.write("\n" + "=" * 60 + "\n")

print(f"\nSaved review summary     -> {SUMMARY_OUT}")
print("\nQuality review complete.")
