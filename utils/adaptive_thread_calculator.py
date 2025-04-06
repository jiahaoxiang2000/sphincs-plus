#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Adaptive Thread Calculator for SPHINCS+

This script implements the adaptive threading model for CUDA kernels in SPHINCS+.
It calculates optimal thread configurations based on performance data.

The model uses the function: T(t) = alpha + beta/t + gamma*t
Where:
- alpha: fixed overhead cost
- beta/t: parallel speedup component
- gamma*t: thread management overhead
- t: thread count
"""

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit


def performance_model(t, alpha, beta, gamma):
    """
    Performance model for thread optimization.

    Args:
        t: Total thread count (blocks × threads per block)
        alpha: Fixed overhead cost
        beta: Parallel workload coefficient
        gamma: Thread management overhead coefficient

    Returns:
        Predicted execution time
    """
    return alpha + beta / t + gamma * t


def calculate_optimal_threads(csv_file):
    """
    Calculate optimal thread configurations from benchmark data.

    Args:
        csv_file: Path to CSV file with benchmark data
                 Expected columns: "blocks", "threads", "time(ms)"

    Returns:
        tuple: (model_params, optimal_thread_count, best_config, optimal_configs)
        - model_params: (alpha, beta, gamma)
        - optimal_thread_count: Theoretical optimal total thread count
        - best_config: Best measured configuration from data
        - optimal_configs: Dictionary of optimal block counts for each thread size
    """
    # Load the dataset
    df = pd.read_csv(csv_file, skipinitialspace=True)

    # Clean column names by removing whitespace
    df.columns = df.columns.str.strip()

    # Calculate total threads
    df["total_threads"] = df["blocks"] * df["threads"]

    # Find the best measured configuration
    best_config = df.loc[df["time(ms)"].idxmin()]

    # Extract data for model fitting
    t_values = df["total_threads"].values
    times = df["time(ms)"].values

    # Initial parameter guesses
    p0 = [50, 5000, 0.0001]

    # Fit the model parameters
    try:
        params, covariance = curve_fit(performance_model, t_values, times, p0=p0)
        alpha, beta, gamma = params

        # Calculate theoretical optimal thread count
        t_optimal = np.sqrt(beta / gamma)

        # Calculate optimal block count for each thread size
        thread_sizes = sorted(df["threads"].unique())
        optimal_configs = {}

        for thread_size in thread_sizes:
            optimal_blocks = max(1, round(t_optimal / thread_size))
            total_threads = optimal_blocks * thread_size
            expected_time = performance_model(total_threads, alpha, beta, gamma)
            optimal_configs[thread_size] = {
                "blocks": optimal_blocks,
                "total_threads": total_threads,
                "estimated_time": expected_time,
            }

        return (params, t_optimal, best_config, optimal_configs)

    except RuntimeError as e:
        print(f"Error fitting model: {e}")
        return None


def print_results(results, file_name):
    """
    Print the results of the thread optimization.

    Args:
        results: Tuple returned by calculate_optimal_threads
        file_name: Name of the benchmark file (for reporting)
    """
    if results is None:
        print("Could not calculate optimization parameters.")
        return

    params, t_optimal, best_config, optimal_configs = results
    alpha, beta, gamma = params

    print(f"Results for {file_name}:")
    print("=" * 50)
    print(f"Model parameters:")
    print(f"  alpha = {alpha:.4f} (fixed overhead)")
    print(f"  beta = {beta:.2f} (parallel workload coefficient)")
    print(f"  gamma = {gamma:.8f} (thread overhead coefficient)")
    print(f"\nTheoretical optimal total thread count: {t_optimal:.2f}")
    print(f"\nBest configuration in measured data:")
    print(f"  Blocks: {best_config['blocks']}, Threads: {best_config['threads']}")
    print(f"  Total threads: {best_config['total_threads']}")
    print(f"  Execution time: {best_config['time(ms)']:.2f}ms")

    print("\nOptimal configurations for different thread counts:")
    for thread_size, config in sorted(optimal_configs.items()):
        print(
            f"  {config['blocks']} blocks × {thread_size} threads = {config['total_threads']} total threads"
        )
        print(f"    Estimated time: {config['estimated_time']:.2f}ms")
    print("=" * 50)

    # Get operation name from filename (strip path and extension)
    operation = file_name.split("/")[-1].split(".")[0]

    # Calculate optimal time using the performance model
    optimal_time = performance_model(t_optimal, alpha, beta, gamma)

    # Prepare the result row
    result_row = {
        "operation": operation,
        "alpha": alpha,
        "beta": beta,
        "gamma": gamma,
        "t_optimal": t_optimal,
        "optimal_time": optimal_time,
        "best_measured_threads": best_config["total_threads"],
        "best_measured_time": best_config["time(ms)"],
        "best_blocks": best_config["blocks"],
        "best_threads": best_config["threads"],
    }

    # Path to parameter.csv
    parameter_csv = "../data/parameter.csv"

    try:
        # Try to read existing data
        df = pd.read_csv(parameter_csv)

        # Check if operation already exists
        if operation in df["operation"].values:
            # Replace existing row
            df.loc[df["operation"] == operation] = pd.Series(result_row)
        else:
            # Append new row
            df = pd.concat([df, pd.DataFrame([result_row])], ignore_index=True)
    except (FileNotFoundError, pd.errors.EmptyDataError):
        # Create new dataframe if file doesn't exist or is empty
        df = pd.DataFrame([result_row])

    # Write updated dataframe to CSV
    df.to_csv(parameter_csv, index=False)
    print(f"Results saved to {parameter_csv}")

    # Generate CSV output string for display
    csv_output = "operation,alpha,beta,gamma,t_optimal,optimal_time,best_measured_threads,best_measured_time,best_blocks,best_threads\n"
    csv_output += f"{operation},{alpha},{beta},{gamma},{t_optimal},{optimal_time},{best_config['total_threads']},{best_config['time(ms)']},{best_config['blocks']},{best_config['threads']}"
    print("\nCSV Output:")
    print(csv_output)


def main():
    """
    Main function to demonstrate usage of the calculator.
    """
    # List of benchmark files to analyze
    files = [
        "../data/128f-kaypair-32768.csv",
        "../data/128f-sign-32768.csv",
        "../data/128f-verify-32768.csv",
    ]

    for file_path in files:
        try:
            results = calculate_optimal_threads(file_path)
            print_results(results, file_path)
            print("\n")
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except Exception as e:
            print(f"Error processing {file_path}: {e}")


if __name__ == "__main__":
    main()
