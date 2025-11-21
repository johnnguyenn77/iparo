from pathlib import Path
from typing import Literal

import pandas as pd

from simulation.LinkingStrategy import *
from simulation.VersionDensity import *

RESULTS_FOLDER = Path("../results")

OP_NAMES = {"First": "Retrieve First", "Latest": "Retrieve Latest", "Nth": "Retrieve by Sequence Number",
            "Store": "Add Node", "Time": "Retrieve by Time", "List": "List All"}
OP_NAMES_ABBREVIATED = OP_NAMES.copy()
OP_NAMES_ABBREVIATED['Nth'] = "Retrieve at Nth"
OP_TYPES = list(OP_NAMES.keys())
DENSITY_NAMES = {"bhlt": "BHLT", "linear": "Linear", "multipeak": "Multipeak", "uniform": "Uniform"}
ACTIONS = ["IPNS Get", "IPNS Update", "IPFS Store", "IPFS Retrieve", "Links"]
POLICY_GROUPS_FILES = {subpath.name:
                           [param for param in subpath.iterdir() if param.is_dir()]
                       for subpath in RESULTS_FOLDER.iterdir() if subpath.is_dir()}
POLICY_GROUPS = {subpath.name:
                     [param.name for param in subpath.iterdir() if param.is_dir()]
                 for subpath in RESULTS_FOLDER.iterdir() if subpath.is_dir()}
POLICY_GROUP_NAMES = {"single": "Single", "previous": "Previous", "comprehensive": "Comprehensive",
                      "random": "Random", "sequniform": "Sequential Uniform",
                      "seqmaxgap": "Sequential Max-Gap", "seqexp": "Sequential Exponential",
                      "tempuniform": "Temporal Uniform", "tempmingap": "Temporal Min-Gap",
                      "tempexp": "Temporal Exponential"}

POLICY_GROUP_COMBINATIONS = [(group, param)
                             for group, params in POLICY_GROUPS.items()
                             for param in params]

ENVIRONMENTS = [file.name[:file.name.find(".csv")].split("-")
                for subpath in RESULTS_FOLDER.iterdir() if subpath.is_dir()
                for param in subpath.iterdir() if param.is_dir()
                for file in param.iterdir() if file.is_file()]

SCALES = list(set([int(x[0]) for x in ENVIRONMENTS]))
DENSITIES = list(set([x[1] for x in ENVIRONMENTS]))
COLOR_SCHEME = "category10"
COLOR_SCHEME_PAIRED = "tableau20"
NUM_COLUMNS = 3
DENSITIES_HELP = {"BHLT": "Big Head Long Tail, which is a scaled and shifted loguniform distribution with "
                          "20 as its parameter.",
                  "Linear": "A distribution where the later nodes are more densely distributed "
                            "than the earlier nodes.",
                  "Multipeak": ("A mixture of two normal distributions, one with a mean "
                                "of 0 seconds and a standard deviation of 300 seconds, and "
                                "the other with a mean of 1000 seconds and a standard deviation "
                                "of 400 seconds.")}


class Action(IntEnum):
    IPNS_GET = 1
    IPNS_UPDATE = 2
    IPFS_STORE = 3
    IPFS_RETRIEVE = 4
    LINKS = 5

ACTION_LIST = [ACTIONS[action - 1] for action in Action]
RETRIEVE_ACTION_LIST = [action for action in Action if action != Action.LINKS]
UNSAFE_LIST_ALL_ACTIONS = [5]

def shorten_group_name(policy_group: str):
    return policy_group.replace("Temporal", "Temp.").replace("Exponential", "Exp.")


def shorten_parameter_name(policy_param: str):
    return policy_param.replace("Seconds", "s")


def get_summary_data(policies: pd.DataFrame,
                     density: str,
                     operation: str,
                     scales: list[int] | int | None = None,
                     actions: list[int | Action] | None = None,
                     agg_func: Literal['mean', 'max', 'median', 'all'] = 'all',
                     analyze_all_iterations: bool = False) -> pd.Series | pd.DataFrame:
    """
    Gets the summary data from the generated CSV files. The default setting is to analyze the summary
    conveniently located at the bottom of the CSV file, but it can also analyze all iterations instead, and
    in doing so, ignores the ``agg_func`` argument.

    :param policies: The name of all listed densities (defined as a nx2 DataFrame whose columns are 'Group' and 'Param')
    :param density: The density to use.
    :param operation: The operation, capitalized. This parameter is case-sensitive.
    :param scales: The scales to iterate through, defaults to SCALES.
    :param actions: The action indices, which defaults to [Action.IPFS_RETRIEVE]. Index 0 is automatically added.
    :param agg_func: The aggregate function. Currently set to mean by default.
    :param analyze_all_iterations: Whether to analyze all iterations instead of just the summary.
    """
    partial_dfs = []

    if actions is None:
        actions = [Action.IPFS_RETRIEVE]
    actions.append(0)
    index = ['Policy', 'Scale']
    if scales is None:
        scales = SCALES
    elif isinstance(scales, int):
        scales = [scales]
        index.remove('Scale')
    for i, row in policies.iterrows():
        policy_group = row['Group']
        policy_param = row['Param']
        for scale in scales:
            # Get number of iterations based on operation
            if operation == "Store":
                n_iter = scale
            elif operation == "Unsafe-List":
                n_iter = scale - 1
            else:
                n_iter = 10
            filename = RESULTS_FOLDER / policy_group / policy_param / f"{scale}-{density}-{operation}.csv"
            policy_name = (shorten_group_name(policy_group) + " - " +
                           shorten_parameter_name(policy_param)) if policy_param != "None" else policy_group
            if analyze_all_iterations:
                if 'Iteration' not in index:
                    index.append('Iteration')
                partial_df = (pd.read_csv(filename, nrows=n_iter, usecols=actions)
                              .assign(Iteration=pd.Series(np.arange(1, n_iter + 1)), Policy=policy_name,
                                      Scale=scale, Density=density))
            else:
                partial_df = (pd.read_csv(filename, skiprows=n_iter, usecols=actions, index_col=0).transpose()
                              .assign(Policy=policy_name, Scale=scale, Density=density)
                              .rename(columns={"25%": "q1", "50%": "median", "75%": "q3"}))
                if len(actions) > 2:
                    action_names = [ACTIONS[action - 1] for action in actions[:-1]]
                    partial_df = partial_df.assign(Action=action_names)
                    if 'Action' not in index:
                        index.append('Action')

            partial_df = partial_df.set_index(index, drop=False)

            if agg_func == 'all' or analyze_all_iterations:
                partial_dfs.append(partial_df)
            else:
                partial_dfs.append(partial_df[agg_func])
    df = pd.concat(partial_dfs)

    return df


def capitalize(x: str):
    return x[0].upper() + x[1:].lower()


def rank_and_sort_tradeoff(df: pd.DataFrame):
    """
    Post-processing step for ranking and sorting the space-time tradeoff dataframes.
    """
    ranked_df = df.copy()
    ranked_df.set_index(["Policy"])
    ranked_df["Rank"] = ranked_df["Tradeoff"].rank(method="dense").astype(int)
    ranked_df.sort_values(["Tradeoff"], inplace=True)
    return ranked_df


def select_policy(strategy_type: str, param: str) -> LinkingStrategy:
    match strategy_type.lower():
        case 'single':
            return SingleStrategy()
        case 'comprehensive':
            return ComprehensiveStrategy()
        case 'previous':
            return KPreviousStrategy(int(param))
        case 'random':
            return KRandomStrategy(int(param))
        case 'sequential-uniform':
            return SequentialUniformNPriorStrategy(int(param))
        case 'sequential-max-gap':
            return SequentialSMaxGapStrategy(int(param))
        case 'sequential-exponential':
            return SequentialExponentialStrategy(float(param))
        case 'temporal-uniform':
            return TemporalUniformStrategy(int(param))
        case 'temporal-min-gap':
            return TemporalMinGapStrategy(float(param))
        case _:
            base = float(param)
            return TemporalExponentialStrategy(base, 10)


def select_version_density(version_density: str) -> VersionDensity:
    match version_density.lower():
        case 'bhlt':
            return BigHeadLongTailVersionDensity(20)
        case 'linear':
            return LinearVersionDensity(2)
        case 'multipeak':
            return MultipeakVersionDensity(np.array([0.5, 0.5]), np.array([[1000, 300], [2000, 400]]))
        case _:
            return UniformVersionDensity()
