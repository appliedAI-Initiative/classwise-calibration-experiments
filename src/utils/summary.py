import pandas as pd

__all__ = ["create_summary_table_with_relative_change_and_stddev"]


def create_summary_table_with_relative_change_and_stddev(
    df: pd.DataFrame,
) -> pd.DataFrame:
    df = df.groupby(
        ["Model, Dataset", "Calibration Method", "Reduction Method"], as_index=False
    ).agg({"Score": ["mean", "std"]})
    df.columns = ["_".join(filter(bool, col)) for col in df.columns.values]
    df["Score"] = list(zip(df["Score_mean"], df["Score_std"]))
    df = df.drop(columns=["Score_mean", "Score_std"])
    df = df.pivot_table(
        "Score",
        ["Model, Dataset", "Calibration Method"],
        "Reduction Method",
        aggfunc=lambda x: x,
    )
    reduction_methods = [
        "Class-wise",
        "Reduced",
        "Class-wise reduced",
        "Weighted Reduced",
        "Class-wise weighted reduced",
    ]

    baseline_values = df["Baseline"].apply(pd.Series)

    for method in reduction_methods:
        if method not in df.columns:
            continue
        df[method] = list(
            zip(
                (
                    (df[method].apply(pd.Series)[0] - baseline_values[0])
                    * 100
                    / baseline_values[0]
                ).apply(
                    lambda x: f"{'+' if x > 0 else ('-' if x < 0 else '')}{abs(x):.2f}%"
                ),
                ((df[method].apply(pd.Series)[1]) * 100 / baseline_values[0]).apply(
                    lambda x: f"±{x:.2f}%"
                ),
            )
        )
    for method in reduction_methods:
        if method not in df.columns:
            continue
        df[method] = (
            df[method].apply(pd.Series)[0].astype(str)
            + " "
            + df[method].apply(pd.Series)[1].astype(str)
        )
    df["Baseline"] = (
        baseline_values[0].apply(lambda x: f"{x:.5f}")
        + " "
        + ((baseline_values[1]) * 100 / -baseline_values[0]).apply(
            lambda x: f"±{abs(x):.2f}%"
        )
    )
    return df
