
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the cleaned Netflix dataset
data = pd.read_csv("Netflix_Cleaned.csv")

print("Dataset loaded successfully!")
print(data.head())

# Check the dataset
print("\nDataset shape:")
print(data.shape)

print("\nAvailable content types:")
print(data["type"].value_counts(dropna=False))


# Standardize content type values
data["type_clean"] = (
    data["type"]
    .astype("string")
    .str.strip()
    .str.lower()
    .map({
        "movie": "Movie",
        "tv show": "TV Show"
    })
)

# Check for unexpected or missing content types
invalid_rows = data["type_clean"].isna().sum()
print("\nInvalid or missing content types:", invalid_rows)

# Keep only valid Movie and TV Show records
content_data = data.dropna(subset=["type_clean"])

# Count Movies and TV Shows
content_count = (
    content_data["type_clean"]
    .value_counts()
    .reindex(["Movie", "TV Show"], fill_value=0)
)

total_content = content_count.sum()

if total_content == 0:
    raise ValueError("No valid Movie or TV Show records found.")

# Calculate percentage
content_percent = (content_count / total_content) * 100

# Create summary table
summary = pd.DataFrame({
    "Content Type": content_count.index,
    "Count": content_count.values,
    "Percentage": content_percent.values.round(2)
})

print("\nContent Type Summary:")
print(summary.to_string(index=False))

# Find the most common content type
main_type = content_count.idxmax()
main_count = content_count.max()
main_percent = content_percent[main_type]

print("\nTotal Content:", total_content)
print("Most common content type:", main_type)
print("Number of titles:", main_count)
print("Percentage:", round(main_percent, 2), "%")


# Set chart style
sns.set_theme(style="whitegrid")

# Create dashboard layout
fig, axes = plt.subplots(
    1, 3,
    figsize=(16, 6),
    gridspec_kw={"width_ratios": [1.1, 1, 1.2]}
)

fig.suptitle(
    "Netflix Content Type Analysis Dashboard",
    fontsize=18,
    fontweight="bold"
)

# Bar chart
sns.barplot(
    data=summary,
    x="Content Type",
    y="Count",
    color="steelblue",
    ax=axes[0]
)

axes[0].set_title("Movies vs TV Shows", fontsize=13)
axes[0].set_xlabel("Content Type")
axes[0].set_ylabel("Number of Titles")

for container in axes[0].containers:
    axes[0].bar_label(container, fmt="%.0f")

# Donut chart
axes[1].pie(
    summary["Count"],
    labels=summary["Content Type"],
    autopct="%1.1f%%",
    startangle=90,
    wedgeprops={"width": 0.4},
    textprops={"fontsize": 10}
)

axes[1].set_title("Content Type Percentage", fontsize=13)

# Summary panel
axes[2].axis("off")

movie_count = int(content_count["Movie"])
tv_count = int(content_count["TV Show"])

movie_percent = content_percent["Movie"]
tv_percent = content_percent["TV Show"]

findings = (
    "KEY FINDINGS\n\n"
    f"Total Titles: {total_content:,}\n\n"
    f"Movies: {movie_count:,}\n"
    f"Movie Share: {movie_percent:.2f}%\n\n"
    f"TV Shows: {tv_count:,}\n"
    f"TV Show Share: {tv_percent:.2f}%\n\n"
    f"Highest Content Type: {main_type}\n\n"
    "Analysis based on the cleaned Netflix dataset."
)

axes[2].text(
    0.05, 0.95,
    findings,
    fontsize=12,
    verticalalignment="top",
    linespacing=1.5
)

plt.tight_layout(rect=[0, 0, 1, 0.92])

# Save dashboard
plt.savefig(
    "Netflix_Content_Type_Dashboard.png",
    dpi=300,
    bbox_inches="tight"
)

# Save summary table
summary.to_csv("Content_Type_Summary.csv", index=False)

print("\nDashboard saved successfully!")
print("Summary saved successfully!")

plt.show()
