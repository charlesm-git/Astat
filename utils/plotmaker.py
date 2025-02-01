import matplotlib.pyplot as plt
import numpy as np

from utils.calculation import (
    get_ascent_per_area,
    get_ascent_per_grade,
    get_ascent_per_year,
    get_total_ascent,
)


def graph_ascent_per_area():
    total_ascents = get_total_ascent()
    ascent_per_area = get_ascent_per_area()

    # Contain the labels for the legend
    legend_labels = []
    # Contain the number of ascents per area (number only)
    sizes = []

    # Append legend_label and sizes
    for item in ascent_per_area:
        pourcentage = item[1] / total_ascents * 100
        legend_labels.append(f"{pourcentage:.1f}% : {item[0]}")
        sizes.append(item[1])

    # Define Colormap
    cmap = plt.get_cmap("twilight_shifted")
    colors = [cmap(i / len(sizes)) for i in range(len(sizes))]

    # Create Figure
    fig, ax = plt.subplots()

    # Create pie chart
    wedges, texts = ax.pie(
        sizes,
        wedgeprops=dict(width=0.8),
        startangle=110,
        colors=colors,
    )

    # Define a variable distance from the center for the labels
    text_distances = [1.15 if i % 2 == 0 else 1.3 for i in range(len(sizes))]

    # Add the number of ascents as a label with variable distance from the
    # center to avoid overlapping
    for wedge, size, dist in zip(wedges, sizes, text_distances):
        ang = (
            wedge.theta2 + wedge.theta1
        ) / 2  # Get the middle angle of the wedge
        x = np.cos(np.radians(ang)) * dist  # Adjust x based on distance
        y = np.sin(np.radians(ang)) * dist  # Adjust y based on distance

        ax.text(
            x, y, size, ha="center", va="center", fontsize=8, fontweight="bold"
        )

    # Create chart legend
    ax.legend(
        wedges,
        legend_labels,
        title="Areas",
        loc="center left",
        bbox_to_anchor=(1.2, 0.5),
        fontsize="small",
    )
    # Shift the pie chart left to center all the content (chart + legend)
    fig.subplots_adjust(right=0.5)

    file_path = "utils/graphs/graph_ascent_per_area.png"
    fig.savefig(file_path, dpi=300, bbox_inches="tight", transparent=True)

    plt.close(fig)


def graph_ascent_per_grade():
    ascent_per_grade = get_ascent_per_grade()

    grade_value, number_of_ascents = zip(*ascent_per_grade)

    max_x_limit = max(number_of_ascents) + 20
    fig, ax = plt.subplots()
    bar_container = ax.barh(grade_value, number_of_ascents)

    ax.set(
        xlabel="Number of Ascents",
        xlim=(0, max_x_limit),
    )
    ax.bar_label(bar_container, number_of_ascents, padding=5)

    file_path = "utils/graphs/graph_ascent_per_grade.png"
    fig.savefig(file_path, dpi=300, bbox_inches="tight", transparent=True)

    plt.close(fig)


def graph_ascent_per_year():
    ascent_per_year = get_ascent_per_year()

    years, number_of_ascents = zip(*ascent_per_year)

    years_range = range(min(years), max(years) + 1)

    max_x_limit = max(number_of_ascents) + 20
    fig, ax = plt.subplots()
    bar_container = ax.bar(years, number_of_ascents)

    ax.set(
        ylabel="Number of Ascents",
        ylim=(0, max_x_limit),
    )
    ax.bar_label(bar_container, number_of_ascents, padding=5)
    ax.set_xticks(ticks=years_range, labels=years_range, rotation=45)

    file_path = "utils/graphs/graph_ascent_per_year.png"
    fig.savefig(file_path, dpi=300, bbox_inches="tight", transparent=True)

    plt.close(fig)


def graph_showing():
    area_chart = graph_ascent_per_area()
    plt.show()
    grade_chart = graph_ascent_per_grade()
    plt.show()
    year_chart = graph_ascent_per_year()
    plt.show()
