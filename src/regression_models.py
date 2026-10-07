"""Pooled OLS specification and multicollinearity diagnostics."""
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor
from .data_processing import FEATURES


def run_ols_model(df: pd.DataFrame):
    return sm.OLS(df.sales, sm.add_constant(df[FEATURES])).fit()


def calculate_vif(df: pd.DataFrame) -> pd.DataFrame:
    x = sm.add_constant(df[FEATURES])
    return pd.DataFrame([{"variable": name, "VIF": variance_inflation_factor(x.values, i)}
                         for i, name in enumerate(x.columns) if name != "const"])


def coefficient_table(model) -> pd.DataFrame:
    se = model.std_errors if hasattr(model, "std_errors") else model.bse
    ci = model.conf_int()
    return pd.DataFrame({"coefficient": model.params, "standard_error": se,
                         "p_value": model.pvalues, "ci_lower": ci.iloc[:, 0], "ci_upper": ci.iloc[:, 1]})
