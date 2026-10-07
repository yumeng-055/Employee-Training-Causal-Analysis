"""Readable charts derived exclusively from the observed data and fitted models."""
from pathlib import Path
import shutil
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.api as sm
from .descriptive_analysis import monthly_trends

COLORS = {0: "#64748b", 1: "#087e8b"}


def save_figure(fig, folder: Path, name: str) -> None:
    fig.savefig(folder / name, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def generate_figures(df, ols, models, did, root: Path) -> None:
    folder = root / "outputs" / "figures"
    folder.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.titleweight": "bold", "axes.labelcolor": "#334155"})
    trends = monthly_trends(df)
    fig, ax = plt.subplots(figsize=(11, 5))
    for group, label in [(0, "Control"), (1, "Treated")]:
        ax.plot(trends.index, trends[label.lower()], marker="o", ms=4, lw=2.2,
                color=COLORS[group], label=label)
    ax.axvspan(13, 24, color=COLORS[1], alpha=.05)
    ax.axvline(13, color="#d97706", linestyle="--", label="Training begins: Jan 2025")
    ax.set(title="Monthly Store Sales: Treated vs Control Groups", ylabel="Average monthly sales (dataset units)",
           xlabel="Observation month", xlim=(1, 24), ylim=(0, max(df.sales.max(), 80)))
    ax.set_xticks([1, 4, 7, 10, 13, 16, 19, 22, 24],
                  ["Jan 2024", "Apr", "Jul", "Oct", "Jan 2025", "Apr", "Jul", "Oct", "Dec"])
    ax.grid(axis="y", alpha=.2)
    ax.legend(loc="lower right", frameon=False)
    fig.tight_layout()
    save_figure(fig, folder, "monthly_sales_trends.png")

    fig, ax = plt.subplots(figsize=(9, 4.5))
    bins = np.linspace(df.sales.min(), df.sales.max(), 22)
    for group, label in [(0, "Control"), (1, "Treated")]:
        ax.hist(df.loc[df.treated == group, "sales"], bins=bins, alpha=.55, color=COLORS[group], label=label)
    ax.set(title="Sales Distribution Across All Store-Month Observations", xlabel="Monthly sales (dataset units)", ylabel="Observations")
    ax.legend(frameon=False)
    fig.tight_layout()
    save_figure(fig, folder, "sales_distribution.png")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    sm.qqplot(ols.resid, line="45", fit=True, ax=axes[0])
    axes[0].set_title("OLS residual Q-Q plot")
    axes[1].scatter(ols.fittedvalues, ols.resid, alpha=.25, s=12, color=COLORS[1])
    axes[1].axhline(0, color="#d97706", linestyle="--")
    axes[1].set(title="OLS residuals vs fitted values", xlabel="Fitted sales", ylabel="Residual")
    fig.tight_layout()
    save_figure(fig, folder, "regression_diagnostics.png")

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    for i, name in enumerate(["Pooled OLS", "Random Effects"]):
        model = models[name]
        ci = model.conf_int().loc["treated"]
        value = model.params["treated"]
        axes[0].errorbar(value, i, xerr=[[value-ci.iloc[0]], [ci.iloc[1]-value]], fmt="o", color=COLORS[0], capsize=5)
    axes[0].set_yticks([0, 1], ["Pooled OLS: treated", "Random Effects: treated"])
    axes[0].set(title="Conditional group differences", xlabel="Coefficient and 95% CI")
    axes[0].text(.02, .02, "Store FE absorbs treated; no separate coefficient.", transform=axes[0].transAxes, fontsize=9)
    value = did.params["treated:post"]
    ci = did.conf_int().loc["treated:post"]
    axes[1].errorbar(value, 0, xerr=[[value-ci.iloc[0]], [ci.iloc[1]-value]], fmt="o", color=COLORS[1], capsize=6)
    axes[1].set_yticks([0], ["TWFE: treated × post"])
    axes[1].set(title="DID estimate under stated assumptions", xlabel="Sales units and store-clustered 95% CI")
    for ax in axes:
        ax.axvline(0, color="#94a3b8", linestyle="--")
        ax.set_xlim(-1, 7)
        ax.set_ylim(-.7, 1.6)
        ax.grid(axis="x", alpha=.2)
    fig.suptitle("Different coefficients answer different business questions", fontsize=14, fontweight="bold")
    fig.tight_layout()
    save_figure(fig, folder, "model_comparison.png")

    fig = plt.figure(figsize=(12, 5), facecolor="#f8fafc")
    fig.text(.06, .86, "EMPLOYEE TRAINING  /  RETAIL PANEL CASE STUDY", color=COLORS[1], fontsize=13, weight="bold")
    fig.text(.06, .69, "Did employee training improve store sales?", fontsize=25, weight="bold", color="#0f172a")
    fig.text(.06, .42, f"+{value:.2f}", fontsize=55, weight="bold", color=COLORS[1])
    fig.text(.34, .46, "estimated monthly sales units\nTWFE DID · store-clustered standard errors", fontsize=15, color="#334155")
    fig.text(.06, .25, f"50 stores  |  24 months  |  1,200 observations  |  95% CI [{ci.iloc[0]:.2f}, {ci.iloc[1]:.2f}]", fontsize=13)
    fig.text(.06, .12, "Supports a monitored, phased rollout; causal interpretation depends on DID assumptions.", fontsize=12)
    fig.text(.06, .055, "Within-store changes · store and month fixed effects · no independently established pricing effect", fontsize=10, color="#64748b")
    save_figure(fig, folder, "project_overview.png")
    for source, target in [("project_overview.png", "project_overview.png"),
                           ("monthly_sales_trends.png", "key_visualization.png"), ("model_comparison.png", "did_result.png")]:
        shutil.copyfile(folder / source, root / "screenshots" / target)
