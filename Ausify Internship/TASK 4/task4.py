
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import FancyBboxPatch


# Load cleaned Netflix dataset
data = pd.read_csv("Netflix_Cleaned.csv")

data["release_year"] = pd.to_numeric(
    data["release_year"], errors="coerce"
)

data = data.dropna(subset=["release_year"]).copy()
data["release_year"] = data["release_year"].astype(int)

data["type"] = (
    data["type"]
    .astype("string")
    .str.strip()
    .str.lower()
    .map({"movie": "Movie", "tv show": "TV Show"})
)

if data.empty:
    raise ValueError("No valid release year records found.")

print("Netflix dataset loaded successfully!")
print("Dataset shape:", data.shape)


# Yearly content calculation
yearly_count = data.groupby("release_year").size().sort_index()

all_years = list(range(
    yearly_count.index.min(),
    yearly_count.index.max() + 1
))

yearly_count = yearly_count.reindex(
    all_years, fill_value=0
)

yearly_count.index.name = "Release Year"

# Yearly growth and decline
yearly_change = yearly_count.diff().fillna(0)

yearly_growth = (
    yearly_count.pct_change(fill_method=None) * 100
).replace([np.inf, -np.inf], np.nan)


# Movies and TV Shows comparison
type_data = data.dropna(subset=["type"])

yearly_type = pd.crosstab(
    type_data["release_year"],
    type_data["type"]
)

yearly_type = yearly_type.reindex(
    index=all_years,
    columns=["Movie", "TV Show"],
    fill_value=0
)

yearly_type.index.name = "Release Year"


# Important statistics
total_titles = len(data)
total_years = data["release_year"].nunique()

peak_year = int(yearly_count.idxmax())
peak_count = int(yearly_count.max())

latest_year = int(yearly_count.index.max())
latest_count = int(yearly_count.loc[latest_year])

movie_total = int(data["type"].eq("Movie").sum())
tv_total = int(data["type"].eq("TV Show").sum())

yearly_change_valid = yearly_change.iloc[1:]

biggest_increase_year = int(yearly_change_valid.idxmax())
biggest_increase = int(yearly_change_valid.max())

biggest_decrease_year = int(yearly_change_valid.idxmin())
biggest_decrease = int(yearly_change_valid.min())


# Output folder
os.makedirs("Output", exist_ok=True)


# Corporate blue colors
sns.set_theme(style="whitegrid")

navy = "#163A5F"
blue = "#2878B5"
light_blue = "#58B4D9"
background = "#F1F5F9"
white = "#FFFFFF"
text_color = "#243B53"
muted = "#627D98"
orange = "#E08A5B"


# Create dashboard canvas
fig = plt.figure(
    figsize=(18, 13),
    facecolor=background
)


# Main heading
fig.text(
    0.06, 0.958,
    "NETFLIX YEARLY TREND ANALYSIS",
    fontsize=23,
    fontweight="bold",
    color=navy
)

fig.text(
    0.06, 0.927,
    "Release year distribution | Growth tracking | Content comparison",
    fontsize=11,
    color=muted
)


# KPI card function
def add_card(x, y, width, height, heading, value, subtitle):

    card = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.012",
        facecolor=white,
        edgecolor="#D9E2EC",
        linewidth=1.2,
        transform=fig.transFigure,
        zorder=1
    )

    fig.add_artist(card)

    # Card heading
    fig.text(
        x + 0.022,
        y + height - 0.018,
        heading,
        fontsize=9,
        color=muted,
        fontweight="bold",
        verticalalignment="top",
        zorder=2
    )

    # Card value
    value_size = 18 if len(str(value)) > 12 else 22

    fig.text(
        x + 0.022,
        y + 0.050,
        str(value),
        fontsize=value_size,
        color=blue,
        fontweight="bold",
        verticalalignment="center",
        zorder=2
    )

    # Card subtitle
    fig.text(
        x + 0.022,
        y + 0.014,
        subtitle,
        fontsize=8,
        color=muted,
        verticalalignment="bottom",
        zorder=2
    )


# Four KPI cards
card_y = 0.795
card_height = 0.105
card_width = 0.205

add_card(
    0.06, card_y, card_width, card_height,
    "TOTAL TITLES ANALYZED",
    f"{total_titles:,}",
    "Titles with valid release years"
)

add_card(
    0.305, card_y, card_width, card_height,
    "YEARS COVERED",
    total_years,
    "Distinct release years"
)

add_card(
    0.55, card_y, card_width, card_height,
    "PEAK RELEASE YEAR",
    peak_year,
    f"{peak_count:,} titles released"
)

add_card(
    0.795, card_y, card_width, card_height,
    "LATEST RELEASE YEAR",
    latest_year,
    f"{latest_count:,} titles released"
)


# Common year tick interval
year_span = yearly_count.index.max() - yearly_count.index.min()
tick_step = 5 if year_span <= 50 else 10

year_ticks = list(range(
    int(yearly_count.index.min()),
    int(yearly_count.index.max()) + 1,
    tick_step
))


# Chart 1: Yearly content trend
ax1 = fig.add_axes([0.09, 0.545, 0.84, 0.19])

ax1.plot(
    yearly_count.index,
    yearly_count.values,
    color=blue,
    linewidth=2.5,
    marker="o",
    markersize=3,
    label="Yearly Releases"
)

# Trend line
if len(yearly_count) > 1:
    trend_values = np.polyfit(
        yearly_count.index,
        yearly_count.values,
        1
    )

    trend_line = np.poly1d(trend_values)

    ax1.plot(
        yearly_count.index,
        trend_line(yearly_count.index),
        color=orange,
        linestyle="--",
        linewidth=2,
        label="Overall Trend"
    )

ax1.set_title(
    "Netflix Content Distribution by Release Year",
    fontsize=14,
    fontweight="bold",
    color=navy,
    pad=12
)

ax1.set_ylabel("Number of Titles", labelpad=8)

ax1.set_xticks(year_ticks)
ax1.tick_params(axis="x", rotation=35, labelsize=9)
ax1.tick_params(axis="y", labelsize=9)

ax1.grid(axis="both", alpha=0.2)

ax1.legend(
    loc="upper left",
    frameon=False,
    fontsize=9
)


# Chart 2: Movies vs TV Shows
ax2 = fig.add_axes([0.09, 0.285, 0.38, 0.17])

ax2.stackplot(
    yearly_type.index,
    yearly_type["Movie"].values,
    yearly_type["TV Show"].values,
    labels=["Movies", "TV Shows"],
    colors=[blue, light_blue],
    alpha=0.9
)

ax2.set_title(
    "Movies vs TV Shows Over Time",
    fontsize=12,
    fontweight="bold",
    color=navy,
    pad=12
)

ax2.set_xlabel("Release Year", labelpad=6)
ax2.set_ylabel("Number of Titles", labelpad=6)

ax2.set_xticks(year_ticks)
ax2.tick_params(axis="x", rotation=35, labelsize=8)
ax2.tick_params(axis="y", labelsize=8)

ax2.legend(
    loc="upper left",
    frameon=False,
    fontsize=8
)

ax2.grid(axis="y", alpha=0.2)


# Chart 3: Yearly growth and decline
ax3 = fig.add_axes([0.55, 0.285, 0.38, 0.17])

bar_colors = [
    blue if value >= 0 else orange
    for value in yearly_change.values
]

ax3.bar(
    yearly_change.index,
    yearly_change.values,
    color=bar_colors,
    width=0.8
)

ax3.axhline(
    y=0,
    color=navy,
    linewidth=1
)

ax3.set_title(
    "Yearly Change in Content Releases",
    fontsize=12,
    fontweight="bold",
    color=navy,
    pad=12
)

ax3.set_xlabel("Release Year", labelpad=6)
ax3.set_ylabel("Change in Titles", labelpad=6)

ax3.set_xticks(year_ticks)
ax3.tick_params(axis="x", rotation=35, labelsize=8)
ax3.tick_params(axis="y", labelsize=8)

ax3.grid(axis="y", alpha=0.2)


# Key business findings
fig.text(
    0.07, 0.215,
    "KEY BUSINESS FINDINGS",
    fontsize=14,
    fontweight="bold",
    color=navy
)

findings = [
    f"1. Peak release year: {peak_year} with {peak_count:,} titles.",
    f"2. Total Movies: {movie_total:,} | Total TV Shows: {tv_total:,}.",
    f"3. Biggest yearly increase: {biggest_increase:,} titles in {biggest_increase_year}.",
    f"4. Biggest yearly decrease: {biggest_decrease:,} titles in {biggest_decrease_year}.",
    f"5. Latest release year: {latest_year} with {latest_count:,} titles."
]

for i, finding in enumerate(findings):

    fig.text(
        0.08,
        0.178 - (i * 0.027),
        finding,
        fontsize=9.5,
        color=text_color
    )


# Footer
fig.text(
    0.06, 0.031,
    "DATA SOURCE: NETFLIX CLEANED DATASET | PYTHON | PANDAS | MATPLOTLIB | SEABORN",
    fontsize=9,
    color=muted
)

fig.text(
    0.06, 0.014,
    "Note: Release year represents the original title release year, not the date added to Netflix.",
    fontsize=8,
    color=muted
)


# Save dashboard
plt.savefig(
    "Output/Netflix_Yearly_Trend_Dashboard.png",
    dpi=300,
    bbox_inches="tight",
    facecolor=background
)


# Export yearly content count
yearly_report = pd.DataFrame({
    "Release Year": yearly_count.index,
    "Content Count": yearly_count.values,
    "Yearly Change": yearly_change.values,
    "Growth Rate (%)": yearly_growth.values
})

yearly_report[
    ["Release Year", "Content Count"]
].to_csv(
    "Output/Yearly_Content_Count.csv",
    index=False
)


# Export content type comparison
yearly_type.to_csv(
    "Output/Yearly_Content_Type.csv"
)


# Export growth analysis
yearly_report.to_csv(
    "Output/Yearly_Growth_Analysis.csv",
    index=False
)


# Terminal results
print("\n========== YEARLY TREND ANALYSIS ==========")

print("\nYearly Content Count:")
print(yearly_report.to_string(index=False))

print("\nTotal Titles:", total_titles)
print("Years Covered:", total_years)

print("\nPeak Release Year:", peak_year)
print("Peak Year Content Count:", peak_count)

print("\nTotal Movies:", movie_total)
print("Total TV Shows:", tv_total)

print("\nBiggest Yearly Increase:")
print(biggest_increase_year, ":", biggest_increase)

print("\nBiggest Yearly Decrease:")
print(biggest_decrease_year, ":", biggest_decrease)

print("\n========== ANALYSIS COMPLETED ==========")

print("\nFiles generated successfully:")
print("1. Netflix_Yearly_Trend_Dashboard.png")
print("2. Yearly_Content_Count.csv")
print("3. Yearly_Content_Type.csv")
print("4. Yearly_Growth_Analysis.csv")

plt.show()
