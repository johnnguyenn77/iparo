import os
import pathlib

import pandas as pd

RESULTS_FOLDER = "../results"


def get_iteration_summary_split(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    # Number of rows dedicated to summary is 8 (count, mean, std, min, 25%, 50%, 75%, max).
    summary_stats_labels = ["count", "mean", "std", "min", "25%", "50%", "75%", "max"]
    # Key Assumption: the summary stats labels are located in the bottom of the file.
    # Cutoff is negative from that key assumption.
    cutoff = -len(summary_stats_labels)
    df_iter = df.iloc[:cutoff]
    df_summary = df.iloc[cutoff:]

    return df_iter, df_summary


def policy_name_to_file_name(policy_name: str):
    path = os.path.join(RESULTS_FOLDER, policy_name)
    my_dir = pathlib.Path(path)

    # Assume alphabetical order.
    first_file = next((x for x in my_dir.iterdir() if x.is_file()), None).name
    policy_length = first_file.find("-Hyperlarge")
    # Strip the portion to the right of the filename.
    filename = first_file[:policy_length]
    return filename