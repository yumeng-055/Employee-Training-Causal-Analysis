"""Panel estimators and qualified comparisons of store heterogeneity."""
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from linearmodels.panel import PanelOLS, RandomEffects
from .data_processing import FEATURES, prepare_panel_data


def run_panel_models(df: pd.DataFrame) -> dict:
    panel = prepare_panel_data(df)
    y, x = panel.sales, panel[FEATURES]
    within_x = x.drop(columns="treated")
    return {
        "Pooled OLS": PanelOLS(y, sm.add_constant(x)).fit(cov_type="unadjusted"),
        # Time-invariant treated is absorbed by store effects.
        "Store FE": PanelOLS(y, within_x, entity_effects=True).fit(
            cov_type="clustered", cluster_entity=True),
        "Random Effects": RandomEffects(y, sm.add_constant(x)).fit(),
        # Standard Hausman comparison uses compatible conventional covariances.
        "FE for Hausman": PanelOLS(y, within_x, entity_effects=True).fit(cov_type="unadjusted"),
    }


def hausman_test(fe, re) -> dict:
    common = [name for name in fe.params.index if name in re.params.index]
    diff = (fe.params[common] - re.params[common]).to_numpy()
    covariance = (fe.cov.loc[common, common] - re.cov.loc[common, common]).to_numpy()
    eigenvalues = np.linalg.eigvalsh(covariance)
    positive_definite = bool(eigenvalues.min() > 0)
    statistic = float(diff @ np.linalg.solve(covariance, diff)) if positive_definite else np.nan
    valid = positive_definite and statistic >= 0
    return {"test": "Standard Hausman comparison of FE and RE", "statistic": statistic if valid else np.nan,
            "df_num": len(common), "df_den": np.nan,
            "p_value": stats.chi2.sf(statistic, len(common)) if valid else np.nan,
            "minimum_covariance_difference_eigenvalue": eigenvalues.min(),
            "covariance_positive_definite": positive_definite,
            "status": "Validated classical inference" if valid else "Chi-square inference unavailable",
            "interpretation": "Classical covariance assumptions apply." if valid else
                "Covariance difference is indefinite or singular; no validated chi-square inference or rejection of RE consistency."}


def model_selection(models: dict) -> pd.DataFrame:
    pooled, fe = models["Pooled OLS"], models["Store FE"]
    restrictions = pooled.df_resid - fe.df_resid
    statistic = ((pooled.resid_ss - fe.resid_ss) / restrictions) / (fe.resid_ss / fe.df_resid)
    return pd.DataFrame([
        {"test": "Classical F comparison of pooled OLS and store FE", "statistic": statistic,
         "df_num": restrictions, "df_den": fe.df_resid,
         "p_value": stats.f.sf(statistic, restrictions, fe.df_resid), "status": "Classical inference",
         "interpretation": "Evidence of store heterogeneity under classical F assumptions; not a cluster-robust joint test."},
        hausman_test(models["FE for Hausman"], models["Random Effects"]),
    ])
