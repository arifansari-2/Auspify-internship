
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from matplotlib.patches import FancyBboxPatch

# Load Netflix dataset
data = pd.read_csv("Netflix_Cleaned.csv")

print("Netflix dataset loaded successfully!")
print("Dataset shape:", data.shape)


# Clean country information
data["country"] = (
    data["country"]
    .astype("string")
    .str.strip()
    .replace({
        "Unknown": pd.NA,
        "": pd.NA
    })
)

# Separate multiple countries
country_data = data.dropna(subset=["country"]).copy()

country_data["country"] = country_data["country"].str.split(",")

country_data = country_data.explode("country")

country_data["country"] = (
    country_data["country"]
    .astype("string")
    .str.strip()
    .str.replace(r"\s+", " ", regex=True)
)

# Remove unavailable country values
country_data = country_data[
    country_data["country"].notna()
    & (country_data["country"] != "")
    & (country_data["country"].str.lower() != "unknown")
].copy()

# Remove duplicate title-country combinations
country_data = country_data.drop_duplicates(
    subset=["show_id", "country"]
)


# Count content by country
country_count = (
    country_data.groupby("country")
    .size()
    .sort_values(ascending=False)
)

if country_count.empty:
    raise ValueError("No valid country information found.")

# Get top 10 countries
top_countries = country_count.head(10)

# Create country ranking
ranking = country_count.reset_index()

ranking.columns = ["Country", "Content Count"]

ranking.insert(
    0,
    "Rank",
    range(1, len(ranking) + 1)
)

# Prepare content type comparison
country_data["type"] = (
    country_data["type"]
    .astype("string")
    .str.strip()
    .str.lower()
    .map({
        "movie": "Movie",
        "tv show": "TV Show"
    })
)

type_data = country_data.dropna(subset=["type"])

country_type = pd.crosstab(
    type_data["country"],
    type_data["type"]
)

country_type = country_type.reindex(
    columns=["Movie", "TV Show"],
    fill_value=0
)

top_type = country_type.reindex(
    top_countries.index,
    fill_value=0
)


# Calculate key metrics
total_countries = len(country_count)
total_associations = len(country_data)

top_country = country_count.index[0]
top_count = int(country_count.iloc[0])

movie_total = int(country_data["type"].eq("Movie").sum())
tv_total = int(country_data["type"].eq("TV Show").sum())


# Create output folder
os.makedirs("Output", exist_ok=True)

# Corporate blue theme
sns.set_theme(style="whitegrid")

navy = "#163A5F"
blue = "#2878B5"
light_blue = "#58B4D9"
background = "#F1F5F9"
white = "#FFFFFF"
text_color = "#243B53"
muted = "#627D98"


# Create dashboard
fig = plt.figure(figsize=(18, 11), facecolor=background)

fig.text(
    0.06, 0.95,
    "NETFLIX COUNTRY-WISE CONTENT ANALYSIS",
    fontsize=21,
    fontweight="bold",
    color=navy
)

fig.text(
    0.06, 0.915,
    "Geographic distribution | Country rankings | Content comparison",
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
        transform=fig.transFigure
    )

    fig.add_artist(card)

    # Card heading
    fig.text(
        x + 0.025,
        y + height - 0.025,
        heading,
        fontsize=10,
        color=muted,
        fontweight="bold",
        verticalalignment="top"
    )

    # Card value
    value_size = 17 if len(str(value)) > 12 else 22

    fig.text(
        x + 0.025,
        y + 0.052,
        str(value),
        fontsize=value_size,
        color=blue,
        fontweight="bold",
        verticalalignment="center"
    )

    # Card subtitle
    fig.text(
        x + 0.025,
        y + 0.018,
        subtitle,
        fontsize=9,
        color=muted,
        verticalalignment="bottom"
    )



# Dashboard KPI cards
add_card(
    0.06, 0.77, 0.27, 0.12,
    "COUNTRIES ANALYZED",
    f"{total_countries:,}",
    "Unique country entries"
)

add_card(
    0.365, 0.77, 0.27, 0.12,
    "CONTENT ASSOCIATIONS",
    f"{total_associations:,}",
    "Country-title combinations"
)

add_card(
    0.67, 0.77, 0.27, 0.12,
    "TOP CONTENT COUNTRY",
    top_country,
    f"{top_count:,} associated titles"
)


# Create chart layout
ax1 = fig.add_axes([0.07, 0.39, 0.40, 0.31])
ax2 = fig.add_axes([0.55, 0.39, 0.39, 0.31])

# Top 10 countries chart
sns.barplot(
    x=top_countries.values,
    y=top_countries.index,
    color=blue,
    ax=ax1
)

ax1.set_title(
    "Top 10 Content-Producing Countries",
    fontsize=14,
    fontweight="bold",
    color=navy,
    pad=15
)

ax1.set_xlabel("Number of Titles", color=text_color)
ax1.set_ylabel("Country", color=text_color)

ax1.grid(axis="x", alpha=0.2)
ax1.grid(axis="y", visible=False)

# Add space for values at the end of bars
ax1.set_xlim(0, top_countries.max() * 1.18)

for container in ax1.containers:
    ax1.bar_label(
        container,
        fmt="%.0f",
        padding=5,
        fontsize=9,
        color=text_color
    )


# Movies vs TV Shows chart
top_type.plot(
    kind="barh",
    stacked=True,
    ax=ax2,
    color=[blue, light_blue],
    width=0.7
)

ax2.set_title(
    "Movies vs TV Shows by Country",
    fontsize=14,
    fontweight="bold",
    color=navy,
    pad=15
)

ax2.set_xlabel("Number of Titles", color=text_color)
ax2.set_ylabel("Country", color=text_color)

ax2.legend(
    title="Content Type",
    frameon=False,
    loc="lower right"
)

ax2.grid(axis="x", alpha=0.2)
ax2.grid(axis="y", visible=False)
ax2.invert_yaxis()


# Key findings section
fig.text(
    0.07, 0.29,
    "KEY BUSINESS FINDINGS",
    fontsize=14,
    fontweight="bold",
    color=navy
)

findings = [
    f"1. {top_country} ranks first with {top_count:,} associated titles.",
    f"2. The dataset contains {total_countries:,} distinct countries.",
    f"3. Movie associations: {movie_total:,}.",
    f"4. TV Show associations: {tv_total:,}.",
    "5. Country counts include titles associated with multiple countries."
]

for i, finding in enumerate(findings):
    fig.text(
        0.08,
        0.245 - (i * 0.038),
        finding,
        fontsize=11,
        color=text_color
    )


# Dashboard footer
fig.text(
    0.06, 0.035,
    "DATA SOURCE: NETFLIX CLEANED DATASET | PYTHON • PANDAS • MATPLOTLIB • SEABORN",
    fontsize=9,
    color=muted
)

# Save dashboard
plt.savefig(
    "Output/Netflix_Country_Analysis.png",
    dpi=300,
    bbox_inches="tight",
    facecolor=background
)


# Export ranking and comparison
ranking.to_csv(
    "Output/Country_Wise_Ranking.csv",
    index=False
)

top_type.to_csv(
    "Output/Country_Content_Type_Comparison.csv"
)


# Print final results
print("\n========== COUNTRY ANALYSIS ==========")

print("\nTop 10 Countries:")
print(top_countries.to_string())

print("\nTotal Countries:", total_countries)
print("Total Country-Title Associations:", total_associations)

print("\nTop Content Country:", top_country)
print("Associated Titles:", top_count)

print("\nMovies:", movie_total)
print("TV Shows:", tv_total)

print("\n========== ANALYSIS COMPLETED ==========")

print("\nFiles generated successfully:")
print("1. Netflix_Country_Analysis.png")
print("2. Country_Wise_Ranking.csv")
print("3. Country_Content_Type_Comparison.csv")

plt.show()
