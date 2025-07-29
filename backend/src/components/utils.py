from enum import IntEnum
from pathlib import Path

import pandas as pd

RESULTS_FOLDER = Path("../results")

SCALES = ["Single", "Small", "Medium", "Large", "Huge"]
SCALES_DICT = {k: v for k, v in zip(SCALES, [1, 10, 100, 1000, 10000])}
POLICY_GROUPS = {subpath.name:
                     [param for param in subpath.iterdir() if param.is_dir()]
                 for subpath in RESULTS_FOLDER.iterdir() if subpath.is_dir()}


class BasicOpType(IntEnum):
    IPNS_GET = 1
    IPNS_UPDATE = 2
    IPFS_STORE = 3
    IPFS_RETRIEVE = 4
    LINKS = 5


def get_summary_data(policy_group_names: list[str],
                     listed_densities: list[str],
                     operation: str,
                     scales: list[str] | None = None,
                     col_index: BasicOpType = BasicOpType.IPFS_RETRIEVE):
    """
    Gets the summary data conveniently located at the bottom of the CSV file.

    :param policy_group_names: The name of every policy listed (defined as a folder in the 'Results' directory).
    :param listed_densities: The name of every listed density.
    :param operation: The operation, capitalized. This parameter is case-sensitive.
    :param scales: The scales to iterate through, defaults to SCALES.
    :param col_index: The column index.
    """
    if scales is None:
        scales = SCALES

    partial_dfs = []

    for policy_group in policy_group_names:
        for policy_param in POLICY_GROUPS[policy_group]:
            for scale in scales:
                for density in listed_densities:
                    # Get number of iterations based on operation
                    n_iter = SCALES_DICT[scale] if operation == "Store" else 10
                    filename = f"{policy_group}/{policy_param}/{scale}-{density}-{operation}.csv"
                    partial_df = (pd.read_csv(filename,
                                              skiprows=n_iter, usecols=[0, col_index], index_col=0).transpose()
                                  .assign(Group=policy_group, Param=policy_param, Scale=scale, Density=density)
                                  .rename(columns={"25%": "q1", "50%": "median", "75%": "q3"})
                                  .set_index(['Policy', 'Scale', 'Density'], drop=False))
                    partial_dfs.append(partial_df)
    df = pd.concat(partial_dfs)
    return df
