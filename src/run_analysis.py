"""Regenerate the case study outputs with python -m src.run_analysis."""
import hashlib
import json
import platform
from importlib.metadata import version
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from .data_processing import PROJECT_ROOT, DATA_PATH, load_data, validate_data
from .descriptive_analysis import descriptive_statistics, post_training_ttest, monthly_trends
from .regression_models import run_ols_model, calculate_vif, coefficient_table
from .panel_models import run_panel_models, model_selection
from .did_analysis import run_did_model, run_basic_did_model, time_effects_test
from .visualization import generate_figures


def run_analysis() -> dict:
    root = PROJECT_ROOT
    tables = root / "outputs" / "tables"
    tables.mkdir(parents=True, exist_ok=True)
    source = load_data(root / "data" / "original_course_data.xlsx")
    if not DATA_PATH.exists():
        source.to_csv(DATA_PATH, index=False)
    df = load_data()
    pd.testing.assert_frame_equal(source, df, check_dtype=False, check_exact=False, rtol=1e-14, atol=1e-14)
    quality = validate_data(df)
    ols = run_ols_model(df)
    models = run_panel_models(df)
    did = run_did_model(df)
    basic = run_basic_did_model(df)
    public_models = {name: model for name, model in models.items() if name != "FE for Hausman"}
    comparison = pd.concat({name: coefficient_table(model) for name, model in public_models.items()},
                           names=["model", "variable"])
    results = {
        "data_quality": quality, "descriptive_statistics": descriptive_statistics(df),
        "welch_ttest": post_training_ttest(df), "vif": calculate_vif(df),
        "model_comparison": comparison, "ols_results": coefficient_table(ols),
        "twfe_did_results": coefficient_table(did).loc[["treated:post"]],
        "basic_did_results": coefficient_table(basic), "monthly_trends": monthly_trends(df),
        "model_selection": model_selection(models), "time_effects_test": time_effects_test(df),
    }
    results["model_fit"] = pd.DataFrame([
        {"model": name, "r_squared": model.rsquared,
         "adjusted_r_squared": getattr(model, "rsquared_adj", np.nan),
         "note": "Within R-squared" if name == "Store FE" else "Estimator-specific R-squared; not directly comparable"}
        for name, model in {**public_models, "TWFE DID": did}.items()
    ])
    price_residual = smf.ols("avg_price ~ C(store_id) + C(month)", data=df).fit().resid
    design_rank = np.linalg.matrix_rank(did.model.exog)
    if design_rank != did.model.exog.shape[1]:
        raise ValueError("TWFE design must have full column rank.")
    results["design_diagnostics"] = pd.DataFrame([{
        "model": "TWFE DID", "design_columns": did.model.exog.shape[1], "design_rank": design_rank,
        "full_column_rank": True, "max_abs_price_residual_after_store_month_FE": abs(price_residual).max(),
        "price_interpretation": "Price variation is absorbed by store and month effects; no separate price coefficient estimated.",
    }])
    indexed = {"model_comparison", "ols_results", "twfe_did_results", "basic_did_results", "monthly_trends"}
    for name, table in results.items():
        table.to_csv(tables / f"{name}.csv", index=name in indexed)
    manifest = {
        "python": platform.python_version(),
        "packages": {p: version(p) for p in ["pandas", "numpy", "scipy", "statsmodels", "linearmodels",
                    "matplotlib", "openpyxl", "nbformat", "nbclient", "ipykernel", "jupyterlab"]},
        "sha256": {str(p.relative_to(root)).replace(chr(92), "/"): hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in [root / "data" / "original_course_data.xlsx", DATA_PATH]},
    }
    (tables / "reproducibility_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    generate_figures(df, ols, models, did, root)
    print(results["twfe_did_results"].to_string())
    print(results["model_selection"].to_string(index=False))
    return {"df": df, "ols": ols, "models": models, "did": did, "tables": results}


if __name__ == "__main__":
    run_analysis()
