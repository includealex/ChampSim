import argparse
import numpy as np
import os
import re
import matplotlib.pyplot as plt

from pathlib import Path
from scipy.stats import gmean

RUN_REGEXP=re.compile(r"run_(\d+)")
MPKI_REGEXP=re.compile(r"MPKI: (?P<mpki>\d+\.\d+) ")
IPC_REGEXP=re.compile(r"CPU 0 cumulative IPC: (?P<ipc>\d+\.\d+) instructions: (?P<instrs>\d+) cycles: (?P<cycles>\d+)")

INCORRECT_IPC=-1
INCORRECT_MPKI=-1

def extract_number(filename: str):
    match = re.search(RUN_REGEXP, filename)
    return int(match.group(1)) if match else float('inf')

def parse_mpki_and_ipc(filename: Path):
    with open(filename, "r") as ifile:
        ilines=ifile.readlines()

    cur_ipc = INCORRECT_IPC
    cur_mpki = INCORRECT_MPKI

    for iline in ilines:
        if (match:=re.search(IPC_REGEXP,iline)):
            cur_ipc = float(match["ipc"])
            continue

        # mpki info is after ipc
        if (match := re.search(MPKI_REGEXP, iline)):
            cur_mpki=float(match["mpki"])
            break

    return cur_ipc, cur_mpki

def plot_results(all_results, labels):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

    for results, label in zip(all_results, labels):
        file_idxs = [el["file_idx"] for el in results]
        mpkis = [el["mpki"] for el in results]
        ipcs = [el["ipc"] for el in results]

        res_gmean_mpki = np.round(gmean(mpkis), 3)
        res_gmean_ipc = np.round(gmean(ipcs), 3)

        ax1.plot(file_idxs, mpkis, marker='o', label=f"{label} (gmean MPKI={res_gmean_mpki})")
        ax2.plot(file_idxs, ipcs, marker='s', label=f"{label} (gmean IPC={res_gmean_ipc})")

    ax1.set_ylabel("MPKI")
    ax1.legend()
    ax1.grid(True)

    ax2.set_xlabel("File Index")
    ax2.set_ylabel("IPC")
    ax2.legend()
    ax2.grid(True)

    plt.suptitle("Branch predictor policies comparison.")
    plt.tight_layout()
    plt.savefig("branch_comparison.png")
    plt.close()


def run_analysis(input_dir: Path):
    input_files = os.listdir(input_dir)
    input_files = sorted(input_files, key=extract_number)

    results = []
    for ifile in input_files:
        cur_ipc, cur_mpki = parse_mpki_and_ipc(Path(f"{input_dir}/{ifile}"))
        if cur_ipc == INCORRECT_IPC or cur_mpki == INCORRECT_MPKI:
            continue
        if (file_idx := str(extract_number(ifile))) == float('inf'):
            continue

        results.append({
            "file_idx": file_idx,
            "ipc": cur_ipc,
            "mpki": cur_mpki
        })

    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs-dirs", type=str, help="comma-separated list of directories with results")
    args = parser.parse_args()

    runs_dirs = [Path(p.strip()) for p in args.runs_dirs.split(",")]

    all_results = []
    labels = []

    labels_correct={"baseline_runs": "bimodal", 
                    "markov_predictor_runs": "markov",
                    "markov_probable_runs": "markov with probability"}

    for dir_path in runs_dirs:
        results = run_analysis(dir_path)
        all_results.append(results)
        labels.append(labels_correct[dir_path.name])

    plot_results(all_results, labels)

