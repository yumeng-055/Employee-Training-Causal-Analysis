"""Group summaries and a store-level Welch test."""
import pandas as pd
from scipy import stats


def descriptive_statistics(df: pd.DataFrame) -> pd.DataFrame:
    result = df.groupby(["treated", "post"]).sales.agg(
        count="count", mean="mean", median="median", std="std", min="min", max="max",
        IQR=lambda x: x.quantile(.75) - x.quantile(.25), skew="skew",
    ).reset_index()
    result["group"] = result.treated.map({0: "Control", 1: "Treated"})
    result["period"] = result.post.map({0: "Pre-training", 1: "Post-training"})
    return result


def post_training_ttest(df: pd.DataFrame) -> pd.DataFrame:
    stores = df.loc[df.post == 1].groupby(["store_id", "treated"]).sales.mean().reset_index()
    control = stores.loc[stores.treated == 0, "sales"]
    treated = stores.loc[stores.treated == 1, "sales"]
    test = stats.ttest_ind(control, treated, equal_var=False)
    return pd.DataFrame([{"test": "Store-level Welch t-test", "statistic": test.statistic,
                          "p_value": test.pvalue, "control_stores": len(control), "treated_stores": len(treated)}])


def monthly_trends(df: pd.DataFrame) -> pd.DataFrame:
    result = df.groupby(["month", "treated"]).sales.mean().unstack()
    result.columns = ["control", "treated"]
    result["difference"] = result.treated - result.control
    return result
