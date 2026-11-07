import pandas as pd

# Load the Netflix dataset
data = pd.read_csv("Dataset.csv")

print("First 5 rows:")
print(data.head())

print("\nDataset shape:")
print(data.shape)

print("\nColumn names:")
print(data.columns.tolist())

print("\nDataset information:")
data.info()


# Check missing values
print("\nMissing values:")
print(data.isnull().sum())


# In this dataset, some missing values are written as "Not Given"
data = data.replace("Not Given", pd.NA)

print("\nMissing values after checking 'Not Given':")
print(data.isnull().sum())


# Fill missing text values with Unknown
data["director"] = data["director"].fillna("Unknown")
data["country"] = data["country"].fillna("Unknown")
data["rating"] = data["rating"].fillna("Unknown")


# Check and remove duplicate rows
print("\nDuplicate rows:", data.duplicated().sum())

data = data.drop_duplicates()

print("Duplicate rows after cleaning:", data.duplicated().sum())


# Remove unnecessary spaces from text columns
columns = [
    "show_id",
    "type",
    "title",
    "director",
    "country",
    "rating",
    "duration",
    "listed_in"
]

for col in columns:
    data[col] = data[col].astype("string").str.strip()


# Make Type values consistent
data["type"] = data["type"].replace({
    "movie": "Movie",
    "MOVIE": "Movie",
    "tv show": "TV Show",
    "TV SHOW": "TV Show",
    "Tv Show": "TV Show"
})


# Make ratings consistent
data["rating"] = data["rating"].str.upper()


# Clean country names where multiple countries are present
data["country"] = data["country"].str.replace(
    r"\s*,\s*", ", ", regex=True
)


# Convert date_added into proper date format
data["date_added"] = pd.to_datetime(
    data["date_added"],
    errors="coerce"
)


# Final checks
print("\nFinal dataset shape:")
print(data.shape)

print("\nMissing values after cleaning:")
print(data.isnull().sum())

print("\nDuplicate rows after cleaning:")
print(data.duplicated().sum())

print("\nData types:")
print(data.dtypes)


# Save the cleaned dataset
data.to_csv("Netflix_Cleaned.csv", index=False)

print("\nCleaned dataset saved successfully as Netflix_Cleaned.csv")