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


def calculate_optimal_threads_by_function(csv_file, function_name):
    """
    Calculate optimal thread configurations from benchmark data for a specific function.

    Args:
        csv_file: Path to CSV file with benchmark data
                 Expected columns: "function", "blocks", "threads", "time(ms)", "per_op(ms)"
        function_name: Name of the function to analyze

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

    # Filter data for the specified function
    function_df = df[df["function"] == function_name]

    if function_df.empty:
        raise ValueError(f"No data found for function '{function_name}'")

    # Calculate total threads
    function_df["total_threads"] = function_df["blocks"] * function_df["threads"]

    # Find the best measured configuration
    best_config = function_df.loc[function_df["time(ms)"].idxmin()]

    # Extract data for model fitting
    t_values = function_df["total_threads"].values
    times = function_df["time(ms)"].values

    # Initial parameter guesses
    p0 = [50, 5000, 0.0001]

    # Fit the model parameters
    try:
        params, covariance = curve_fit(performance_model, t_values, times, p0=p0)
        alpha, beta, gamma = params

        # Calculate theoretical optimal thread count
        t_optimal = np.sqrt(beta / gamma)

        # Calculate optimal block count for each thread size
        thread_sizes = sorted(function_df["threads"].unique())
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
        print(f"Error fitting model for {function_name}: {e}")
        return None


def print_results_by_function(results, function_name):
    """
    Print the results of the thread optimization for a specific function.

    Args:
        results: Tuple returned by calculate_optimal_threads_by_function
        function_name: Name of the function analyzed
    """
    if results is None:
        print(f"Could not calculate optimization parameters for {function_name}.")
        return

    params, t_optimal, best_config, optimal_configs = results
    alpha, beta, gamma = params

    print(f"Results for {function_name}:")
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
    print(f"  Per operation: {best_config['per_op(ms)']:.4f}ms")

    print("\nOptimal configurations for different thread counts:")
    for thread_size, config in sorted(optimal_configs.items()):
        print(
            f"  {config['blocks']} blocks × {thread_size} threads = {config['total_threads']} total threads"
        )
        print(f"    Estimated time: {config['estimated_time']:.2f}ms")
    print("=" * 50)

    # Calculate optimal time using the performance model
    optimal_time = performance_model(t_optimal, alpha, beta, gamma)

    # Prepare the result row
    result_row = {
        "operation": function_name,
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
        if function_name in df["operation"].values:
            # Replace existing row
            df.loc[df["operation"] == function_name] = pd.Series(result_row)
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
    csv_output += f"{function_name},{alpha},{beta},{gamma},{t_optimal},{optimal_time},{best_config['total_threads']},{best_config['time(ms)']},{best_config['blocks']},{best_config['threads']}"
    print("\nCSV Output:")
    print(csv_output)


def get_unique_functions(csv_file):
    """
    Get list of unique functions from a CSV file.

    Args:
        csv_file: Path to CSV file with benchmark data

    Returns:
        list: List of unique function names
    """
    try:
        df = pd.read_csv(csv_file, skipinitialspace=True)
        return df["function"].unique().tolist()
    except Exception as e:
        print(f"Error retrieving functions from {csv_file}: {e}")
        return []


def main():
    """
    Main function to demonstrate usage of the calculator.
    """
    # Path to the input CSV file
    input_file = "../data/192S-SLH-DSA-32768.csv"

    try:
        # Get unique functions from the CSV
        functions = get_unique_functions(input_file)

        if not functions:
            print(f"No function data found in {input_file}")
            return

        print(
            f"Found {len(functions)} functions in the input file: {', '.join(functions)}\n"
        )

        # Process each function
        for function_name in functions:
            try:
                print(f"Processing {function_name}...")
                results = calculate_optimal_threads_by_function(
                    input_file, function_name
                )
                print_results_by_function(results, function_name)
                print("\n")
            except Exception as e:
                print(f"Error processing {function_name}: {e}")

        print("All functions processed successfully!")

    except FileNotFoundError:
        print(f"Input file not found: {input_file}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
