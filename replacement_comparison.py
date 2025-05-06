import argparse
import numpy as np
import os
import re
import matplotlib.pyplot as plt

from pathlib import Path
from scipy.stats import gmean

RUN_REGEXP=re.compile(r"run_(\d+)")
L2_STATS_REGEXP = re.compile(
    r"cpu0->cpu0_L2C TOTAL\s+ACCESS:\s+(?P<accesses>\d+)\s+HIT:\s+(?P<hits>\d+)\s+MISS:\s+(?P<misses>\d+)"
)
INCORRECT_L2_MISS_RATE = -1

def extract_number(filename: str):
    match = re.search(RUN_REGEXP, filename)
    return int(match.group(1)) if match else float('inf')

def parse_l2_miss_rate(filename: Path):
    with open(filename, "r") as ifile:
        ilines=ifile.readlines()

    cur_l2_miss_rate = INCORRECT_L2_MISS_RATE

    for iline in ilines:
        if (match := re.search(L2_STATS_REGEXP,iline)):
            accesses = int(match["accesses"])
            misses = int(match["misses"])
            cur_l2_miss_rate = float(misses / accesses)

    return cur_l2_miss_rate


def plot_results(all_results, labels):
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))

    num_labels = len(labels)
    file_idxs = sorted(list(set(el["file_idx"] for results in all_results for el in results)))
    bar_width = 0.8 / num_labels

    for i, (results, label) in enumerate(zip(all_results, labels)):
        l2_mr_dict = {el["file_idx"]: el["l2mr"] for el in results}
        l2mrs = [l2_mr_dict.get(idx, 0) for idx in file_idxs]
        res_gmean_l2mr = np.round(gmean([v for v in l2mrs if v > 0]), 3)
        positions = np.arange(len(file_idxs)) + i * bar_width
        ax.bar(positions, l2mrs, bar_width, label=f"{label} (gmean L2MR={res_gmean_l2mr})")

    ax.set_ylabel("L2MR")
    ax.set_xlabel("File Index")
    ax.set_title("L2 Miss Rate Comparison")
    ax.legend()
    ax.grid(True)
    plt.yticks(np.arange(0,1,0.1))
    plt.xticks(range(len(file_idxs)), file_idxs, size='small')
    plt.tight_layout()
    plt.savefig("replacement_comparison.png")
    plt.close()

def run_analysis(input_dir: Path):
    input_files = os.listdir(input_dir)
    input_files = sorted(input_files, key=extract_number)

    results = []
    for ifile in input_files:
        cur_l2_miss_rate = parse_l2_miss_rate(Path(f"{input_dir}/{ifile}"))
        if cur_l2_miss_rate == INCORRECT_L2_MISS_RATE:
            continue
        if (file_idx := str(extract_number(ifile))) == float('inf'):
            continue

        results.append({
            "file_idx": file_idx,
            "l2mr": cur_l2_miss_rate,
        })

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs-dirs", type=str, help="comma-separated list of directories with results")
    args = parser.parse_args()

    runs_dirs = [Path(p.strip()) for p in args.runs_dirs.split(",")]

    all_results = []
    labels = []

    labels_correct={"lru_runs": "LRU", 
                    "plru_runs": "PLRU",
                    "drrip_runs": "DRRIP",
                    "lfu_aging_runs": "LFU_AGING"}

    for dir_path in runs_dirs:
        results = run_analysis(dir_path)
        all_results.append(results)
        labels.append(labels_correct[dir_path.name] if dir_path.name in labels_correct.keys() else dir_path.name)

    plot_results(all_results, labels)

