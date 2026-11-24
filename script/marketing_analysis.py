# -----------------------------------------------------------
# SOCIAL MEDIA ENGAGEMENT ANALYSIS - PYTHON EDA
# -----------------------------------------------------------

# 1. Import Libraries
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

pd.set_option('display.max_columns', None)

# -----------------------------------------------------------
# 2. Load Dataset
# -----------------------------------------------------------
from pathlib import Path
DATA = Path(__file__).resolve().parent.parent / "data" / "social_media_engagement_dataset.csv"
df = pd.read_csv(DATA)
print(df.head())

# -----------------------------------------------------------
# 3. Basic Information
# -----------------------------------------------------------
print(df.info())
print(df.describe())
print(df.isnull().sum())
print(df.nunique())

# -----------------------------------------------------------
# 4. Data Cleaning
# -----------------------------------------------------------

# Remove duplicates
df = df.drop_duplicates()

# Check for negative numeric values (fixed)
negative_check = (df.select_dtypes(include=['int64','float64']) < 0).sum()
print("\nNegative Check:\n", negative_check)

# Create Engagement metric
df["Engagement"] = df["Likes"] + df["Comments"] + df["Shares"]

# Engagement Rate (%)
df["Engagement_Rate"] = (df["Engagement"] / df["Impressions"]) * 100

print(df.head())

# -----------------------------------------------------------
# 5. Univariate Analysis
# -----------------------------------------------------------

print("\nPost Type Counts:\n", df["Post_Type"].value_counts())
print("\nContent Category Counts:\n", df["Content_Category"].value_counts())

plt.figure(figsize=(6,4))
sns.countplot(data=df, x="Post_Type")
plt.title("Count of Post Types")
plt.show()

plt.figure(figsize=(6,4))
sns.countplot(data=df, x="Content_Category")
plt.title("Distribution of Content Categories")
plt.show()

# -----------------------------------------------------------
# 6. Bivariate Analysis
# -----------------------------------------------------------

# Post Type vs Engagement
plt.figure(figsize=(7,5))
sns.barplot(data=df, x="Post_Type", y="Engagement", estimator=np.mean)
plt.title("Average Engagement by Post Type")
plt.show()

# Posting Hour vs Impressions
plt.figure(figsize=(10,5))
sns.lineplot(data=df, x="Posted_Hour", y="Impressions", estimator=np.mean)
plt.title("Impressions vs Posting Hour")
plt.xticks(range(0, 24))
plt.show()

# Hashtag Count vs Engagement
plt.figure(figsize=(7,5))
sns.scatterplot(data=df, x="Hashtags_Count", y="Engagement")
plt.title("Hashtags vs Engagement")
plt.show()

# -----------------------------------------------------------
# 7. Correlation Matrix (FIXED)
# -----------------------------------------------------------

numeric_df = df.select_dtypes(include=['int64', 'float64'])

plt.figure(figsize=(10,6))
sns.heatmap(numeric_df.corr(), annot=True, cmap="coolwarm")
plt.title("Correlation Heatmap")
plt.show()


# -----------------------------------------------------------
# 8. Key Results Table (for report)
# -----------------------------------------------------------

results = df.groupby("Post_Type")[["Likes", "Comments", "Shares", "Engagement", "Impressions"]].mean()
print("\nSummary Table by Post Type:\n", results)

# -----------------------------------------------------------
# 9. Statistical checks and rate-based findings (for README)
# -----------------------------------------------------------
from scipy import stats

# Weighted engagement rate (total engagement / total impressions),
# the basis used in the dashboard. Not the average of post-level rates.
def weighted_rate(group):
    return group["Engagement"].sum() / group["Impressions"].sum() * 100

print("\nOverall weighted engagement rate (%):",
      round(df["Engagement"].sum() / df["Impressions"].sum() * 100, 2))

print("\nWeighted engagement rate by Content_Category (%):")
print(df.groupby("Content_Category").apply(weighted_rate).round(2))

print("\nWeighted engagement rate by Post_Type (%):")
print(df.groupby("Post_Type").apply(weighted_rate).round(2))

# Time bands (night wraps across midnight)
hour = df["Posted_Hour"]
conditions = [
    hour.between(0, 5) | hour.between(21, 23),
    hour.between(6, 11),
    hour.between(12, 16),
    hour.between(17, 20),
]
labels = ["Night (21:00-05:59)", "Morning (06:00-11:59)",
          "Afternoon (12:00-16:59)", "Evening (17:00-20:59)"]
df["Time_Band"] = np.select(conditions, labels, default="Unclassified")
print("\nWeighted engagement rate by time band (%):")
band = df.groupby("Time_Band", sort=False).apply(weighted_rate).round(2)
print(band)
print("Posts per band:\n", df["Time_Band"].value_counts().reindex(labels))

# Kruskal-Wallis tests on post-level engagement rates (non-parametric,
# because engagement rates are skewed and groups are unequal in size)
print("\nKruskal-Wallis, post-level engagement rate across Content_Category:")
groups = [g["Engagement_Rate"].values for _, g in df.groupby("Content_Category")]
print(f"  H = {stats.kruskal(*groups).statistic:.2f}, p = {stats.kruskal(*groups).pvalue:.3f}")

print("Kruskal-Wallis, post-level engagement rate across Post_Type:")
groups = [g["Engagement_Rate"].values for _, g in df.groupby("Post_Type")]
print(f"  H = {stats.kruskal(*groups).statistic:.2f}, p = {stats.kruskal(*groups).pvalue:.3f}")

# Correlations (Pearson, post level)
print("\nCorrelations (post level):")
print(f"  Hashtags_Count vs Engagement:      {df['Hashtags_Count'].corr(df['Engagement']):.3f}")
print(f"  Hashtags_Count vs Engagement_Rate: {df['Hashtags_Count'].corr(df['Engagement_Rate']):.3f}")
print(f"  Impressions vs Engagement:         {df['Impressions'].corr(df['Engagement']):.3f}")
print(f"  Impressions vs Engagement_Rate:    {df['Impressions'].corr(df['Engagement_Rate']):.3f}")
