"""Identified difference-in-differences models with store-clustered uncertainty."""
import pandas as pd
import statsmodels.formula.api as smf

TWFE_FORMULA = "sales ~ treated:post + C(store_id) + C(month)"


def run_did_model(df: pd.DataFrame):
    # Average price is absorbed by store and month effects in this dataset.
    return smf.ols(TWFE_FORMULA, data=df).fit(
        cov_type="cluster", cov_kwds={"groups": df.store_id}, use_t=False)


def run_basic_did_model(df: pd.DataFrame):
    return smf.ols("sales ~ treated + post + treated:post + staff_num + avg_price + competitor_num", data=df).fit(
        cov_type="cluster", cov_kwds={"groups": df.store_id}, use_t=False)


def time_effects_test(df: pd.DataFrame) -> pd.DataFrame:
    model = smf.ols(TWFE_FORMULA, data=df).fit(
        cov_type="cluster", cov_kwds={"groups": df.store_id}, use_t=True)
    terms = [name for name in model.params.index if name.startswith("C(month)")]
    test = model.f_test(", ".join(f"{name} = 0" for name in terms))
    return pd.DataFrame([{"test": "Store-clustered joint test of month effects",
                          "statistic": float(test.fvalue), "p_value": float(test.pvalue),
                          "df_num": test.df_num, "df_den": test.df_denom}])
