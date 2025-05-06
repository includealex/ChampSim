import argparse
import os
from multiprocessing import Pool

BINARY = './bin/champsim'
WARMUP_INSTR = 10_000_000
SIM_INSTR = 50_000_000

def run_trace(args):
    trace_file, traces_dir, output_dir = args
    trace_path = os.path.join(traces_dir, trace_file)
    output_path = os.path.join(output_dir, f'run_{trace_file}.txt')
    cmd = f"{BINARY} --warmup_instructions {WARMUP_INSTR} --simulation_instructions {SIM_INSTR} {trace_path} > {output_path}"
    print(f"Running: {cmd}")
    os.system(cmd)

def main():
    parser = argparse.ArgumentParser(description='Run ChampSim traces in parallel.')
    parser.add_argument('--traces-dir', required=True, help='Directory containing trace files')
    parser.add_argument('--output-dir', required=True, help='Directory to store output logs')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    traces = [f for f in os.listdir(args.traces_dir) if f.endswith('.champsimtrace.xz')]
    task_args = [(trace, args.traces_dir, args.output_dir) for trace in traces]

    with Pool() as pool:
        pool.map(run_trace, task_args)

if __name__ == '__main__':
    main()
