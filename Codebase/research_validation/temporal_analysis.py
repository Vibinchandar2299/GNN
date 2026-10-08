"""
Temporal and Evolving Job Requirements Descriptive Analysis for HireGraph AI.
Analyzes empirical shifts across recruitment cycles (2023, 2024, 2025, 2026) using
strictly real dataset features without causal over-claims or synthetic data.
"""

import os
import shutil
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

RESULTS_DIR = r"c:\Users\VIBIN\Vibin Projects\GNN\Codebase\research_validation\results"
FIGURES_DIR = r"c:\Users\VIBIN\Vibin Projects\GNN\Codebase\research_validation\figures"
CODEBASE_DIR = r"c:\Users\VIBIN\Vibin Projects\GNN\Codebase"
EXCEL_PATH = r"c:\Users\VIBIN\Vibin Projects\GNN\Dataset\GNN_Placement_Dataset.xlsx"


def run_temporal_analysis(excel_path: str = EXCEL_PATH):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(FIGURES_DIR, exist_ok=True)

    print("Loading unified dataset for temporal analysis...")
    xls = pd.ExcelFile(excel_path)
    df = pd.read_excel(xls, sheet_name="unified_dataset")

    # Clean
    df = df.drop_duplicates().copy()
    df = df.drop_duplicates(subset=["application_id"], keep="first").copy()
    df = df.dropna().reset_index(drop=True)

    cycles = sorted(df["recruitment_cycle"].unique())
    print(f"Cycles available: {cycles}")

    records = []
    for cycle in cycles:
        sub = df[df["recruitment_cycle"] == cycle]
        app_count = len(sub)
        sel_count = int((sub["final_status"] == 1).sum())
        rej_count = int((sub["final_status"] == 0).sum())
        sel_rate = float(sel_count / app_count) if app_count > 0 else 0.0

        records.append({
            "cycle": int(cycle),
            "application_count": app_count,
            "selected_count": sel_count,
            "rejected_count": rej_count,
            "selection_rate": round(sel_rate, 4),
            "average_required_skill_count": round(float(sub["required_skill_count"].mean()), 3),
            "std_required_skill_count": round(float(sub["required_skill_count"].std()), 3),
            "average_skill_match_ratio": round(float(sub["skill_match_ratio"].mean()), 4),
            "std_skill_match_ratio": round(float(sub["skill_match_ratio"].std()), 4),
            "average_required_skill_level_gap": round(float(sub["required_skill_level_gap"].mean()), 4),
            "std_required_skill_level_gap": round(float(sub["required_skill_level_gap"].std()), 4),
            "average_role_shift_score": round(float(sub["role_shift_score"].mean()), 4),
            "average_role_experience_match": round(float(sub["role_experience_match"].mean()), 4),
            "average_cgpa": round(float(sub["cgpa"].mean()), 2),
            "average_salary_lpa": round(float(sub["salary_lpa"].mean()), 2),
            "average_experience_required_months": round(float(sub["experience_required_months"].mean()), 2)
        })

    summary_df = pd.DataFrame(records)
    print("\n--- Temporal Analysis Summary Table ---")
    print(summary_df.to_string(index=False))

    # Save to research results
    res_path = os.path.join(RESULTS_DIR, "temporal_hiring_analysis.csv")
    summary_df.to_csv(res_path, index=False)
    # Also save to Codebase/
    root_path = os.path.join(CODEBASE_DIR, "temporal_hiring_analysis.csv")
    summary_df.to_csv(root_path, index=False)
    print(f"Saved: {res_path} and {root_path}")

    # Set publication styling
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    plt.rcParams.update({
        "font.family": "serif",
        "font.size": 11,
        "axes.labelsize": 12,
        "axes.titlesize": 13,
        "xtick.labelsize": 11,
        "ytick.labelsize": 11,
        "legend.fontsize": 11,
        "figure.titlesize": 14,
        "figure.dpi": 300
    })

    # 1. Temporal Selection Rate Figure
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(summary_df["cycle"], summary_df["selection_rate"] * 100, marker='o', color='#1f77b4', linewidth=2.2, markersize=7)
    for _, row in summary_df.iterrows():
        ax.annotate(
            f"{row['selection_rate']*100:.1f}%\n(N={row['application_count']})",
            (row["cycle"], row["selection_rate"] * 100),
            textcoords="offset points",
            xytext=(0, 10),
            ha='center',
            fontsize=9.5,
            fontweight='bold',
            color='#1f77b4'
        )
    ax.set_title("Recruitment Cycle Selection Rate Trend (2023–2026)", pad=14, fontweight='bold')
    ax.set_xlabel("Recruitment Cycle", labelpad=8)
    ax.set_ylabel("Selection Rate (%)", labelpad=8)
    ax.set_xticks(summary_df["cycle"])
    ax.set_ylim(40, 70)
    ax.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    fig1_path = os.path.join(FIGURES_DIR, "temporal_selection_rate.png")
    fig.savefig(fig1_path, dpi=300)
    fig.savefig(os.path.join(CODEBASE_DIR, "temporal_selection_rate.png"), dpi=300)
    plt.close(fig)
    print(f"Saved: {fig1_path}")

    # 2. Temporal Skill Requirements Figure
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.errorbar(
        summary_df["cycle"],
        summary_df["average_required_skill_count"],
        yerr=summary_df["std_required_skill_count"],
        marker='s',
        color='#2ca02c',
        linewidth=2.2,
        markersize=7,
        capsize=5,
        capthick=1.5,
        label="Required Skill Count (Mean ± Std)"
    )
    for _, row in summary_df.iterrows():
        ax.annotate(
            f"{row['average_required_skill_count']:.2f}",
            (row["cycle"], row["average_required_skill_count"]),
            textcoords="offset points",
            xytext=(0, 10),
            ha='center',
            fontsize=9.5,
            fontweight='bold',
            color='#2ca02c'
        )
    ax.set_title("Evolution of Required Skill Count per Job Opening", pad=14, fontweight='bold')
    ax.set_xlabel("Recruitment Cycle", labelpad=8)
    ax.set_ylabel("Average Required Skill Count", labelpad=8)
    ax.set_xticks(summary_df["cycle"])
    ax.set_ylim(0, max(summary_df["average_required_skill_count"]) + 2.5)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="upper left")
    plt.tight_layout()
    fig2_path = os.path.join(FIGURES_DIR, "temporal_skill_requirements.png")
    fig.savefig(fig2_path, dpi=300)
    fig.savefig(os.path.join(CODEBASE_DIR, "temporal_skill_requirements.png"), dpi=300)
    plt.close(fig)
    print(f"Saved: {fig2_path}")

    # 3. Temporal Skill Match & Level Gap Figure
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    ax.plot(
        summary_df["cycle"],
        summary_df["average_skill_match_ratio"],
        marker='^',
        color='#d62728',
        linewidth=2.2,
        markersize=7,
        label="Skill Match Ratio"
    )
    ax.plot(
        summary_df["cycle"],
        summary_df["average_required_skill_level_gap"],
        marker='v',
        color='#9467bd',
        linewidth=2.2,
        markersize=7,
        linestyle='--',
        label="Required Skill Level Gap"
    )
    for _, row in summary_df.iterrows():
        ax.annotate(f"{row['average_skill_match_ratio']:.3f}", (row["cycle"], row["average_skill_match_ratio"]),
                    textcoords="offset points", xytext=(0, 8), ha='center', fontsize=9, color='#d62728', fontweight='bold')
        ax.annotate(f"{row['average_required_skill_level_gap']:.3f}", (row["cycle"], row["average_required_skill_level_gap"]),
                    textcoords="offset points", xytext=(0, -14), ha='center', fontsize=9, color='#9467bd', fontweight='bold')
    ax.set_title("Evolution of Applicant Skill Alignment across Cycles", pad=14, fontweight='bold')
    ax.set_xlabel("Recruitment Cycle", labelpad=8)
    ax.set_ylabel("Metric Value (0 to 1 scale)", labelpad=8)
    ax.set_xticks(summary_df["cycle"])
    ax.set_ylim(0, 1.0)
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="best")
    plt.tight_layout()
    fig3_path = os.path.join(FIGURES_DIR, "temporal_skill_match.png")
    fig.savefig(fig3_path, dpi=300)
    fig.savefig(os.path.join(CODEBASE_DIR, "temporal_skill_match.png"), dpi=300)
    plt.close(fig)
    print(f"Saved: {fig3_path}")

    return summary_df


if __name__ == "__main__":
    run_temporal_analysis()
