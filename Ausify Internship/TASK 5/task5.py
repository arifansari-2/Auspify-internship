
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


# Load dataset
file_options = [
    "Netflix_Cleaned.csv",
    "Dataset.csv"
]

file_path = None

for name in file_options:
    if os.path.isfile(name):
        file_path = name
        break

if file_path is None:
    raise FileNotFoundError(
        "Dataset not found. Keep Netflix_Cleaned.csv "
        "or Dataset.csv in the same folder as task5.py."
    )

data = pd.read_csv(file_path, encoding="utf-8-sig")
data.columns = data.columns.str.strip()

print("Dataset loaded successfully!")
print("Dataset shape:", data.shape)


# Check required columns
required_columns = ["type", "rating", "listed_in"]

for column in required_columns:
    if column not in data.columns:
        raise ValueError(f"Required column missing: {column}")


# Clean important columns
data["type"] = (
    data["type"]
    .astype("string")
    .str.strip()
    .str.casefold()
    .replace({
        "tv shows": "tv show"
    })
    .map({
        "movie": "Movie",
        "tv show": "TV Show"
    })
)

data["rating"] = (
    data["rating"]
    .astype("string")
    .str.strip()
    .replace("", pd.NA)
    .fillna("Not Rated")
)

data["listed_in"] = (
    data["listed_in"]
    .astype("string")
    .fillna("")
)

content_data = data[
    data["type"].isin(["Movie", "TV Show"])
].copy()

if content_data.empty:
    raise ValueError("No valid Movie or TV Show records found.")


# Rating distribution
rating_count = (
    content_data["rating"]
    .value_counts()
    .sort_values(ascending=False)
)

rating_type = pd.crosstab(
    content_data["rating"],
    content_data["type"]
)

rating_type = rating_type.reindex(
    columns=["Movie", "TV Show"],
    fill_value=0
)

rating_type["Total"] = (
    rating_type["Movie"] + rating_type["TV Show"]
)

rating_type = rating_type.sort_values(
    "Total",
    ascending=False
)


# Extract individual genres
genre_data = content_data[
    ["type", "listed_in"]
].copy()

genre_data["genre"] = genre_data["listed_in"].str.split(",")

genre_data = genre_data.explode("genre")

genre_data["genre"] = (
    genre_data["genre"]
    .astype("string")
    .str.strip()
)

genre_data = genre_data[
    genre_data["genre"].notna()
    & genre_data["genre"].ne("")
].copy()

if genre_data.empty:
    raise ValueError("No valid genre information found.")


# Genre distribution
genre_count = (
    genre_data["genre"]
    .value_counts()
    .sort_values(ascending=False)
)

genre_type = pd.crosstab(
    genre_data["genre"],
    genre_data["type"]
)

genre_type = genre_type.reindex(
    columns=["Movie", "TV Show"],
    fill_value=0
)

genre_type["Total"] = (
    genre_type["Movie"] + genre_type["TV Show"]
)

genre_type = genre_type.sort_values(
    "Total",
    ascending=False
)


# Select top categories
top_ratings = rating_count.head(10)

top_genres = genre_count.head(10)


# IMPORTANT: Sort using Total BEFORE selecting chart columns
rating_plot = (
    rating_type
    .nlargest(8, "Total")
    .sort_values("Total", ascending=True)
)

genre_plot = (
    genre_type
    .nlargest(10, "Total")
    .sort_values("Total", ascending=True)
)


# Calculate KPIs
total_titles = len(content_data)

total_movies = int(
    (content_data["type"] == "Movie").sum()
)

total_shows = int(
    (content_data["type"] == "TV Show").sum()
)

total_ratings = content_data["rating"].nunique()

total_genres = genre_data["genre"].nunique()

most_common_rating = rating_count.index[0]

most_common_genre = genre_count.index[0]

top_rating_count = int(rating_count.iloc[0])

top_genre_count = int(genre_count.iloc[0])


# Business findings
findings = [
    f"1. Total valid Netflix titles analyzed: {total_titles:,}.",

    f"2. Movies: {total_movies:,} | TV Shows: {total_shows:,}.",

    f"3. Most common rating: {most_common_rating} "
    f"({top_rating_count:,} titles).",

    f"4. Most common genre: {most_common_genre} "
    f"({top_genre_count:,} title associations).",

    f"5. Dataset contains {total_ratings} rating categories "
    f"and {total_genres} different genres."
]


# Create output folder
os.makedirs("Output", exist_ok=True)


# Export CSV reports
rating_count.rename_axis(
    "Rating"
).reset_index(
    name="Title Count"
).to_csv(
    "Output/Rating_Distribution.csv",
    index=False
)

genre_count.rename_axis(
    "Genre"
).reset_index(
    name="Title Associations"
).to_csv(
    "Output/Top_Genres.csv",
    index=False
)

rating_type.to_csv(
    "Output/Rating_By_Content_Type.csv"
)

genre_type.to_csv(
    "Output/Genre_By_Content_Type.csv"
)


# Save business findings
with open(
    "Output/Business_Findings.txt",
    "w",
    encoding="utf-8"
) as report:

    report.write("NETFLIX CONTENT RATING AND GENRE ANALYSIS\n\n")

    for finding in findings:
        report.write(finding + "\n")


# Corporate blue theme
navy = "#163A5F"
blue = "#2878B5"
light_blue = "#58B4D9"
background = "#F1F5F9"
white = "#FFFFFF"
muted = "#627D98"
text_color = "#243B53"
orange = "#E08A5B"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.labelsize": 10,
    "axes.facecolor": white,
    "figure.facecolor": background
})


# Create dashboard
fig = plt.figure(
    figsize=(18, 15),
    facecolor=background,
    layout="constrained"
)

grid = fig.add_gridspec(
    5, 2,
    height_ratios=[0.65, 1.05, 3.0, 3.0, 1.7]
)


# Dashboard heading
header_ax = fig.add_subplot(grid[0, :])
header_ax.axis("off")

header_ax.text(
    0.01, 0.78,
    "NETFLIX CONTENT RATING & GENRE ANALYSIS",
    fontsize=23,
    fontweight="bold",
    color=navy,
    transform=header_ax.transAxes
)

header_ax.text(
    0.01, 0.25,
    "Rating distribution | Genre exploration | Audience targeting",
    fontsize=11,
    color=muted,
    transform=header_ax.transAxes
)


# KPI cards
kpi_grid = grid[1, :].subgridspec(
    1, 4
)


def add_card(ax, heading, value, subtitle):

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    card = FancyBboxPatch(
        (0.025, 0.04),
        0.95,
        0.92,
        boxstyle="round,pad=0.015",
        facecolor=white,
        edgecolor="#D9E2EC",
        linewidth=1.3
    )

    ax.add_patch(card)

    ax.text(
        0.09, 0.78,
        heading,
        fontsize=9,
        fontweight="bold",
        color=muted,
        transform=ax.transAxes
    )

    value_size = 18 if len(str(value)) > 12 else 23

    ax.text(
        0.09, 0.47,
        str(value),
        fontsize=value_size,
        fontweight="bold",
        color=blue,
        transform=ax.transAxes
    )

    ax.text(
        0.09, 0.17,
        subtitle,
        fontsize=8,
        color=muted,
        transform=ax.transAxes
    )


card_details = [
    (
        "TOTAL TITLES",
        f"{total_titles:,}",
        "Valid content records"
    ),
    (
        "RATING CATEGORIES",
        total_ratings,
        "Distinct rating labels"
    ),
    (
        "UNIQUE GENRES",
        total_genres,
        "Extracted genre categories"
    ),
    (
        "MOST COMMON RATING",
        most_common_rating,
        f"{top_rating_count:,} associated titles"
    )
]

for i, details in enumerate(card_details):

    card_ax = fig.add_subplot(kpi_grid[0, i])

    add_card(
        card_ax,
        details[0],
        details[1],
        details[2]
    )


# Chart 1: Rating distribution
ax1 = fig.add_subplot(grid[2, 0])

rating_labels = top_ratings.index[::-1]
rating_values = top_ratings.values[::-1]

bars = ax1.barh(
    rating_labels,
    rating_values,
    color=blue,
    height=0.65
)

ax1.set_title(
    "Content Rating Distribution",
    color=navy,
    pad=15
)

ax1.set_xlabel("Number of Titles")
ax1.set_ylabel("Content Rating")

ax1.set_xlim(
    0,
    max(rating_values) * 1.20
)

ax1.bar_label(
    bars,
    fmt="%d",
    padding=4,
    fontsize=8
)

ax1.grid(
    axis="x",
    alpha=0.2
)

ax1.set_axisbelow(True)


# Chart 2: Top 10 genres
ax2 = fig.add_subplot(grid[2, 1])

genre_labels = top_genres.index[::-1]
genre_values = top_genres.values[::-1]

bars = ax2.barh(
    genre_labels,
    genre_values,
    color=light_blue,
    height=0.65
)

ax2.set_title(
    "Top 10 Netflix Genres",
    color=navy,
    pad=15
)

ax2.set_xlabel("Number of Title Associations")
ax2.set_ylabel("Genre")

ax2.set_xlim(
    0,
    max(genre_values) * 1.20
)

ax2.bar_label(
    bars,
    fmt="%d",
    padding=4,
    fontsize=8
)

ax2.grid(
    axis="x",
    alpha=0.2
)

ax2.set_axisbelow(True)


# Chart 3: Movie vs TV Show ratings
ax3 = fig.add_subplot(grid[3, 0])

y = np.arange(len(rating_plot))
bar_height = 0.36

ax3.barh(
    y - bar_height / 2,
    rating_plot["Movie"],
    height=bar_height,
    color=blue,
    label="Movie"
)

ax3.barh(
    y + bar_height / 2,
    rating_plot["TV Show"],
    height=bar_height,
    color=light_blue,
    label="TV Show"
)

ax3.set_yticks(y)
ax3.set_yticklabels(rating_plot.index)

ax3.set_title(
    "Movie vs TV Show Rating Comparison",
    color=navy,
    pad=15
)

ax3.set_xlabel("Number of Titles")
ax3.set_ylabel("Rating")

rating_max = rating_plot[
    ["Movie", "TV Show"]
].to_numpy().max()

ax3.set_xlim(
    0,
    max(rating_max * 1.20, 1)
)

ax3.legend(
    loc="lower right",
    frameon=False
)

ax3.grid(
    axis="x",
    alpha=0.2
)

ax3.set_axisbelow(True)


# Chart 4: Movie vs TV Show genres
ax4 = fig.add_subplot(grid[3, 1])

y = np.arange(len(genre_plot))

ax4.barh(
    y - bar_height / 2,
    genre_plot["Movie"],
    height=bar_height,
    color=blue,
    label="Movie"
)

ax4.barh(
    y + bar_height / 2,
    genre_plot["TV Show"],
    height=bar_height,
    color=light_blue,
    label="TV Show"
)

ax4.set_yticks(y)
ax4.set_yticklabels(genre_plot.index)

ax4.set_title(
    "Genre Distribution by Content Type",
    color=navy,
    pad=15
)

ax4.set_xlabel("Number of Title Associations")
ax4.set_ylabel("Genre")

genre_max = genre_plot[
    ["Movie", "TV Show"]
].to_numpy().max()

ax4.set_xlim(
    0,
    max(genre_max * 1.20, 1)
)

ax4.legend(
    loc="lower right",
    frameon=False
)

ax4.grid(
    axis="x",
    alpha=0.2
)

ax4.set_axisbelow(True)


# Business findings section
findings_ax = fig.add_subplot(grid[4, :])

findings_ax.set_xlim(0, 1)
findings_ax.set_ylim(0, 1)
findings_ax.axis("off")

findings_ax.add_patch(
    FancyBboxPatch(
        (0.01, 0.03),
        0.98,
        0.94,
        boxstyle="round,pad=0.012",
        facecolor=white,
        edgecolor="#D9E2EC",
        linewidth=1.2
    )
)

findings_ax.text(
    0.035, 0.82,
    "KEY BUSINESS FINDINGS",
    fontsize=13,
    fontweight="bold",
    color=navy
)

for i, finding in enumerate(findings):

    findings_ax.text(
        0.045,
        0.65 - (i * 0.12),
        finding,
        fontsize=9.5,
        color=text_color
    )


# Save dashboard
plt.savefig(
    "Output/Netflix_Rating_Genre_Dashboard.png",
    dpi=300,
    facecolor=background,
    bbox_inches="tight"
)


# Display terminal results
print("\n========== TASK 5 ANALYSIS ==========")

print("\nRating Distribution:")
print(rating_count.to_string())

print("\nTop 10 Genres:")
print(top_genres.to_string())

print("\nMovie vs TV Show Rating Comparison:")
print(rating_type.to_string())

print("\nMovie vs TV Show Genre Comparison:")
print(genre_type.head(10).to_string())

print("\nBusiness Findings:")

for finding in findings:
    print(finding)

print("\n========== TASK 5 COMPLETED ==========")

print("\nGenerated files:")

print("1. Netflix_Rating_Genre_Dashboard.png")
print("2. Rating_Distribution.csv")
print("3. Top_Genres.csv")
print("4. Rating_By_Content_Type.csv")
print("5. Genre_By_Content_Type.csv")
print("6. Business_Findings.txt")

print("\nAll files saved inside Output folder.")

plt.show()
