#!/usr/bin/env python3
"""
Simple SEO Scorer for Subdomain Takeovers
Scores vulnerabilities 1-10 based on DR/backlinks only
"""

import pandas as pd
from pathlib import Path

def calculate_seo_score(row):
    """
    Calculate SEO score 1-9 based on trust_score (0-100)

    Maps trust_score to 1-9 scale:
    - 80-100 = 9 (Excellent)
    - 70-79  = 8 (Very Good)
    - 60-69  = 7 (Good)
    - 50-59  = 6 (Above Average)
    - 40-49  = 5 (Average)
    - 30-39  = 4 (Below Average)
    - 20-29  = 3 (Low)
    - 10-19  = 2 (Very Low)
    - 0-9    = 1 (Minimal)
    """
    trust = row.get('trust_score', 0)

    if trust >= 80:
        return 9
    elif trust >= 70:
        return 8
    elif trust >= 60:
        return 7
    elif trust >= 50:
        return 6
    elif trust >= 40:
        return 5
    elif trust >= 30:
        return 4
    elif trust >= 20:
        return 3
    elif trust >= 10:
        return 2
    else:
        return 1

def score_csv(input_csv, output_csv=None):
    """Score vulnerabilities from CSV"""

    df = pd.read_csv(input_csv)

    print(f"📊 Loaded {len(df)} vulnerabilities")
    print(f"🔍 Calculating SEO scores (1-10)...\n")

    # Calculate scores
    df['seo_score'] = df.apply(calculate_seo_score, axis=1)

    # Sort by score
    df = df.sort_values('seo_score', ascending=False)

    # Show distribution
    print("📈 Score Distribution:")
    for score in range(9, 0, -1):
        count = len(df[df['seo_score'] == score])
        if count > 0:
            bar = "█" * min(50, count)
            print(f"  {score:2d}: {bar} ({count})")

    print(f"\n✅ Average SEO Score: {df['seo_score'].mean():.1f}/9")

    # Show top 10
    print("\n🏆 TOP 10 HIGHEST SEO VALUE:")
    print("="*80)
    for idx, row in df.head(10).iterrows():
        print(f"{row['seo_score']}/9 - {row['subdomain']}")
        print(f"       Trust Score: {row.get('trust_score', 0)}/100")
        print()

    # Save
    if output_csv:
        df.to_csv(output_csv, index=False)
        print(f"💾 Saved to: {output_csv}")

    return df

if __name__ == "__main__":
    input_csv = Path.home() / "Desktop/Subdomain_Takeover_Results/Niche_Analysis/niche_analysis.csv"
    output_csv = Path.home() / "Desktop/Subdomain_Takeover_Results/Niche_Analysis/niche_analysis_scored.csv"

    if input_csv.exists():
        score_csv(input_csv, output_csv)
    else:
        print(f"❌ Not found: {input_csv}")
