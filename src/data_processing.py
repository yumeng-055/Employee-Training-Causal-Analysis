"""Load the unchanged course dataset and validate its panel structure."""
from pathlib import Path
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "employee_training_data.csv"
FEATURES = ["treated", "post", "staff_num", "avg_price", "competitor_num"]


def load_data(path: str | Path = DATA_PATH) -> pd.DataFrame:
    path = Path(path)
    return pd.read_excel(path) if path.suffix == ".xlsx" else pd.read_csv(path)


def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    required = ["store_id", "month", "sales", *FEATURES]
    if not set(required).issubset(df.columns):
        raise ValueError("Required analysis columns are missing.")
    checks = {
        "1,200 observations": len(df) == 1200,
        "50 stores": df.store_id.nunique() == 50,
        "Months 1 through 24": set(df.month) == set(range(1, 25)),
        "No missing analysis values": not df[required].isna().any().any(),
        "Unique store-month keys": not df.duplicated(["store_id", "month"]).any(),
        "24 months per store": df.groupby("store_id").month.nunique().eq(24).all(),
        "Binary treatment": df.treated.isin([0, 1]).all(),
        "Treatment constant within store": df.groupby("store_id").treated.nunique().eq(1).all(),
        "Post begins in month 13": np.array_equal(df.post, (df.month >= 13).astype(int)),
        "25 treated and 25 control stores": df.groupby("store_id").treated.first().value_counts().to_dict() == {0: 25, 1: 25},
    }
    result = pd.DataFrame({"check": checks.keys(), "passed": checks.values()})
    if not result.passed.all():
        raise ValueError(result.loc[~result.passed, "check"].tolist())
    return result


def prepare_panel_data(df: pd.DataFrame) -> pd.DataFrame:
    return df.set_index(["store_id", "month"]).sort_index()
