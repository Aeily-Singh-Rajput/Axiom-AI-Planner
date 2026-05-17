"""
Visualization Module
Generates a workload bar chart for the next 7 days using Matplotlib.
Saves the chart as a PNG in the static/images folder for display in the UI.
"""

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend (required for Flask)

import matplotlib.pyplot as plt
import os

OUTPUT_DIR = os.path.join("static", "images")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_workload_chart(schedule):
    """
    Accepts the schedule list from scheduler.generate_schedule().
    Generates a bar chart and saves it to static/images/workload_chart.png.
    Returns the relative path to the image file.
    """
    dates = [day["date"] for day in schedule]
    workloads = [day["total_workload"] for day in schedule]
    colors = ["#e74c3c" if day["exam_warning"] else "#3498db" for day in schedule]

    fig, ax = plt.subplots(figsize=(9, 4))
    bars = ax.bar(dates, workloads, color=colors, edgecolor="white", linewidth=0.5)

    ax.set_xlabel("Day", fontsize=11)
    ax.set_ylabel("Workload Score", fontsize=11)
    ax.set_title("7-Day Workload Distribution", fontsize=13, fontweight="bold")
    ax.set_ylim(0, max(workloads + [1]) * 1.3)

    # Add value labels on bars
    for bar, value in zip(bars, workloads):
        if value > 0:
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.1,
                str(value),
                ha="center",
                va="bottom",
                fontsize=9,
            )

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor="#3498db", label="Normal Day"),
        Patch(facecolor="#e74c3c", label="Exam Warning Day"),
    ]
    ax.legend(handles=legend_elements, loc="upper right", fontsize=9)

    plt.tight_layout()

    output_path = os.path.join(OUTPUT_DIR, "workload_chart.png")
    plt.savefig(output_path, dpi=100, bbox_inches="tight")
    plt.close()

    return "static/images/workload_chart.png"
