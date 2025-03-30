#!/usr/bin/env python3
"""
Generate thread efficiency figure for the SPHINCS+ paper.

This script creates a publication-quality vector figure showing how performance varies
with thread allocation for different SLH-DSA operations, highlighting the optimized
thread configurations that validate the theoretical model.
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import matplotlib
from matplotlib.ticker import MaxNLocator
from argparse import ArgumentParser

# Use LaTeX fonts for publication-quality output
plt.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": ["Times", "Computer Modern Roman"],
        "font.size": 11,
        "text.usetex": True,  # Comment this out if LaTeX is not installed
        "figure.dpi": 300,
    }
)


# Define the performance model: T(t) = alpha + beta/t + gamma*t
def performance_model(t, alpha, beta, gamma):
    return alpha + beta / t + gamma * t


def process_data_file(filepath):
    """Process a CSV data file for thread performance."""
    if not os.path.exists(filepath):
        print(f"Error: File not found - {filepath}")
        return None

    # Load data
    df = pd.read_csv(filepath, skipinitialspace=True)
    df.columns = df.columns.str.strip()
    df["total_threads"] = df["blocks"] * df["threads"]

    # Calculate optimal threads
    t_values = df["total_threads"].values
    times = np.array(df["time(ms)"].values)

    # Initial parameter guesses
    p0 = [50, 5000, 0.0001]

    # Fit the model
    try:
        params, _ = curve_fit(performance_model, t_values, times, p0=p0)
        alpha, beta, gamma = params

        # Calculate theoretical optimal
        t_optimal = np.sqrt(beta / gamma)
        optimal_time = performance_model(t_optimal, alpha, beta, gamma)

        # Find best measured configuration
        best_idx = np.argmin(times)
        best_t = t_values[best_idx]
        best_time = times[best_idx]

        # Generate smooth curve from model
        t_range = np.linspace(min(t_values), max(t_values), 1000)
        predicted_times = performance_model(t_range, alpha, beta, gamma)

        return {
            "t_values": t_values,
            "times": times,
            "model": {
                "params": (alpha, beta, gamma),
                "t_range": t_range,
                "predicted": predicted_times,
            },
            "optimal": {"t": t_optimal, "time": optimal_time},
            "best_measured": {"t": best_t, "time": best_time},
        }
    except Exception as e:
        print(f"Failed to fit model: {e}")
        return None


def generate_figure(data_config, output_path, normalize=True, show_legend=True):
    """Generate the thread efficiency figure for publication."""
    fig, ax = plt.subplots(figsize=(8, 5))

    # Track min/max values for better scaling
    all_times = []
    all_threads = []

    # Process each operation
    for op_name, op_config in data_config.items():
        if not os.path.exists(op_config["file"]):
            print(f"Warning: Skipping {op_name}, file not found")
            continue

        # Process the data
        result = process_data_file(op_config["file"])
        if result is None:
            continue

        # Get the data
        t_values = result["t_values"]
        times = result["times"]

        all_times.extend(times)
        all_threads.extend(t_values)

        # Normalize if requested
        if normalize:
            times = times / np.max(times)
            result["model"]["predicted"] = result["model"]["predicted"] / np.max(times)
            result["optimal"]["time"] = result["optimal"]["time"] / np.max(times)
            result["best_measured"]["time"] = result["best_measured"]["time"] / np.max(
                times
            )

        # Plot sparse data points for clarity
        step = max(1, len(t_values) // 20)  # Show at most ~20 points
        # ax.scatter(
        #     t_values[::step],
        #     times[::step],
        #     color=op_config["color"],
        #     alpha=0.3,
        #     s=30,
        #     label=None,
        # )

        # Plot the model curve
        ax.plot(
            result["model"]["t_range"],
            result["model"]["predicted"],
            color=op_config["color"],
            linestyle=op_config.get("linestyle", "-"),
            linewidth=2,
            label=f"{op_name}",
        )

        # Mark the optimal point
        ax.scatter(
            [result["optimal"]["t"]],
            [result["optimal"]["time"]],
            color=op_config["color"],
            edgecolors="black",
            linewidths=1.5,
            s=120,
            marker=op_config.get("marker", "o"),
            zorder=10,
            label=None,
        )

    # Set up the axis labels and title
    if normalize:
        ax.set_ylabel("Normalized Execution Time (ms)")
    else:
        ax.set_ylabel("Execution Time (ms)")

    ax.set_xlabel("Total Thread Count")
    ax.grid(True, alpha=0.3, linestyle="--")

    # Set integer tick marks on x-axis
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))

    # Add legend if requested
    if show_legend:
        ax.legend(loc="upper right")

    # Tight layout and save
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Figure saved to {output_path}")

    return fig


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Generate thread efficiency figure for SLH-DSA operations"
    )
    parser.add_argument(
        "--output",
        default="/home/xjh/misc/sphincs-plus/fig/thread_efficiency.pdf",
        help="Output file path (default: fig/thread_efficiency.pdf)",
    )
    parser.add_argument(
        "--data-dir",
        default="/home/xjh/misc/sphincs-plus/data",
        help="Directory containing performance data CSV files",
    )
    parser.add_argument(
        "--show", action="store_true", help="Display the figure after generation"
    )
    args = parser.parse_args()

    # Create output directory if needed
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    # Configure operations
    operations = {
        "Sign": {
            "file": os.path.join(args.data_dir, "sign-32768.csv"),
            "color": "blue",
            "marker": "o",
            "linestyle": "-",
        },
        "Verify": {
            "file": os.path.join(args.data_dir, "verify-32768.csv"),
            "color": "green",
            "marker": "s",
            "linestyle": "--",
        },
        "Keypair": {
            "file": os.path.join(args.data_dir, "kaypair-32768.csv"),
            "color": "red",
            "marker": "^",
            "linestyle": "-.",
        },
    }

    # Generate the figure
    fig = generate_figure(operations, args.output)

    # Show if requested
    if args.show:
        plt.show()
    else:
        plt.close(fig)
