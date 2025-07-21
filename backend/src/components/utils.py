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

# Helpful constants
SCALES = ["Single", "Small", "Medium", "Large", "Hyperlarge"]
SCALES_DICT = dict(zip(SCALES, [1, 10, 100, 1000, 10000]))
DENSITIES = ["Uniform", "Linear", "BHLT", "Multipeak"]
NUM_COLUMNS = 2

OP_TYPES = {
    "Get First Node": "First",
    "Get Latest Node": "Latest",
    "List All Nodes": "List",
    "Get Nth Node": "Nth",
    "Get Node at Time T": "Time",
    "Store Nodes": "Store"
}

POLICIES = set()
for filename in os.scandir(RESULTS_FOLDER):
    POLICIES.add(filename.name)


def temp_min_gap_help(seconds: int):
    return (f"A strategy that prioritizes each node that is at least {seconds} seconds apart, "
            "but also includes the first and previous nodes.")


def previous_help(k: int):
    return f"A strategy that uses the links to the {k} prior nodes and the first node."


def random_help(k: int):
    return (f"A strategy that uses the links to the {k} random nodes, the previous node, and the first node"
            f" (and so has up to {k + 2} different links).")


def sequential_exponential_help(k: float):
    return (f"A strategy that uses the links to the previous node, the first node, and the prior nodes whose "
            f"difference in sequence number is a power of {k}, rounded down to an integer. All intermediate "
            f"multiplications in calculating the powers of {k} are not rounded.")

def sequential_max_gap_help(k: float):
    return (f"A strategy where the number of hops from each node to any prior node is guaranteed "
            f"to be no greater than {k}.")

def temp_uniform_help(k: int):
    return (f"A strategy that uses the links to the previous node, the first node, and the {k} prior nodes that are "
            f"uniformly spaced in the window of time between the first node and the previous node, meaning "
            f"up to {k + 2} links are stored with the node.")

def sequential_uniform_help(k: int):
    return (f"A strategy that uses the links to the previous node, the first node, and the {k} prior nodes that are "
            f"uniformly spaced in the sequence number between the first node and the previous node, meaning "
            f"up to {k + 2} links are stored with the node.")


def temp_exponential_help(k: float):
    return (f"A strategy that uses the links to the previous node, the first node, and the prior nodes whose "
            f"difference in time is a power of {k} times the base time unit (1 second). All intermediate "
            f"multiplications in calculating the powers of {k} are not rounded.")

POLICIES_HELP = {
    "Single": "A strategy that only links to the previous node.",
    "2-Random": random_help(2),
    "4-Random": random_help(4),
    "8-Random": random_help(8),
    "16-Random": random_help(16),
    "32-Random": random_help(32),
    "2-Previous": previous_help(2),
    "4-Previous": previous_help(4),
    "8-Previous": previous_help(8),
    "16-Previous": previous_help(16),
    "Sequential-Exponential-Base-1.25": sequential_exponential_help(1.25),
    "Sequential-Exponential-Base-1.5": sequential_exponential_help(1.5),
    "Sequential-Exponential-Base-2": sequential_exponential_help(2),
    "Sequential-Exponential-Base-2.5": sequential_exponential_help(2.5),
    "Sequential-Exponential-Base-3": sequential_exponential_help(3),
    "Sequential-Exponential-Base-4": sequential_exponential_help(4),
    "Previous": "A strategy that uses the links to the previous node and the first node.",
    "Comprehensive": "A strategy where each node is linked to all prior nodes.",
    "Temporally-Min-Gap-10": temp_min_gap_help(10),
    "Temporally-Min-Gap-20": temp_min_gap_help(20),
    "Temporally-Min-Gap-40": temp_min_gap_help(40),
    "Temporally-Min-Gap-80": temp_min_gap_help(80),
    "Temporally-Min-Gap-160": temp_min_gap_help(160),
    "Temporally-2-Uniform": temp_uniform_help(2),
    "Temporally-4-Uniform": temp_uniform_help(4),
    "Temporally-8-Uniform": temp_uniform_help(8),
    "Temporally-16-Uniform": temp_uniform_help(16),
    "Temporally-32-Uniform": temp_uniform_help(32),
    "Sequential-2-Max-Gap": sequential_max_gap_help(2),
    "Sequential-4-Max-Gap": sequential_max_gap_help(4),
    "Sequential-8-Max-Gap": sequential_max_gap_help(8),
    "Sequential-16-Max-Gap": sequential_max_gap_help(16),
    "Sequential-2-Uniform": sequential_uniform_help(2),
    "Sequential-4-Uniform": sequential_uniform_help(4),
    "Sequential-8-Uniform": sequential_uniform_help(8),
    "Sequential-16-Uniform": sequential_uniform_help(16),
    "Sequential-32-Uniform": sequential_uniform_help(32),
    "Temporally-Exponential-Base-1.25": temp_exponential_help(1.25),
    "Temporally-Exponential-Base-1.5": temp_exponential_help(1.5),
    "Temporally-Exponential-Base-2": temp_exponential_help(2),
    "Temporally-Exponential-Base-2.5": temp_exponential_help(2.5),
    "Temporally-Exponential-Base-3": temp_exponential_help(3),
    "Temporally-Exponential-Base-4": temp_exponential_help(4)
}