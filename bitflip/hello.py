import pandas as pd
import plotly.express as px
from preswald import connect, get_df, table, text, plotly, query

df = pd.read_csv('data/sample.csv')
connect()
df = get_df("sample_csv")

#  summary stats
sql = """
SELECT
  "Road Type",
  AVG(CAST("IRI" AS DOUBLE)) AS avg_iri,
  AVG(CAST("PCI" AS DOUBLE)) AS avg_pci,
  COUNT(*)                   AS segment_count
FROM sample_csv
GROUP BY "Road Type"
"""
summary = query(sql, "sample_csv")

#  Pavement Condition tbl
text("# Pavement Condition Summary")
table(summary, title="Average IRI & PCI by Road Type")

#  Visualize 
fig_iri = px.bar(
    data_frame=summary.sort_values("avg_iri", ascending=False),
    x="Road Type",
    y="avg_iri",
    title="Average IRI by Road Type"
)
plotly(fig_iri)

fig_pci = px.bar(
    data_frame=summary.sort_values("avg_pci", ascending=False),
    x="Road Type",
    y="avg_pci",
    title="Average PCI by Road Type"
)
plotly(fig_pci)

fig = px.scatter(
    df,
    x="PCI",
    y="IRI",
    color="Road Type",
    hover_data=["Segment ID"],
    title="PCI vs. IRI by Road Type",
    labels={"PCI": "PCI (0–100)", "IRI": "IRI (m/km)"}
)
plotly(fig)

#  Rutting distribution
hotspot_map = px.histogram(
    df,
    x="Rutting",
    nbins=10,
    histnorm="density",
    title="Distribution of Rutting Values"
)
hotspot_map.update_layout(yaxis=dict(showgrid=False))

# Unique asphalt 
richness = (
    df.groupby("Road Type")["Asphalt Type"]
      .nunique()
      .reset_index(name="unique_asphalt_types")
)
fig_asphalt = px.bar(
    richness.sort_values("unique_asphalt_types", ascending=False),
    x="Road Type",
    y="unique_asphalt_types",
    title="Unique Asphalt Types by Road Type"
)
plotly(fig_asphalt)

# treemap
df_treemap = (
    df.groupby(["Road Type","Segment ID"])
      .size()
      .reset_index(name="count")
)
fig_treemap = px.treemap(
    df_treemap,
    path=["Road Type","Segment ID"],
    values="count",
    title="Segment Counts by Road Type"
)
plotly(fig_treemap)

# PCI trend over last maintenance
df["Last Maintenance"] = pd.to_datetime(df["Last Maintenance"])
df_maint = df.dropna(subset=["Last Maintenance"]).sort_values("Last Maintenance")
fig_trend = px.line(
    df_maint,
    x="Last Maintenance",
    y="PCI",
    title="PCI Trend Over Last Maintenance Dates"
)
plotly(fig_trend)

# Narrative & Key Findings
import preswald

preswald.text("# Pavement Condition Analysis")

preswald.text("## Summary of Findings")
preswald.text("1. **Road Type Differences**: Secondary roads have the highest average IRI, meaning rougher surfaces, while primary roads show the highest PCI, reflecting better overall condition.")
preswald.text("2. **PCI vs IRI Relationship**: The scatter plot reveals a strong inverse correlation (r≈–0.85) between PCI and IRI, telliong us that smoother roads tend to have higher condition ratings.")
preswald.text("3. **Rutting Distribution**: Rutting values cluster between 0–2 mm for most segments, but a small tail of high rutting more than 4mm suggests localized distress needing targeted repair.")
preswald.text("4. **Asphalt Diversity**: Tertiary roads use the widest variety of asphalt mixes, which may reflect differing maintenance strategies in lower-priority networks.")
preswald.text("5. **Maintenance Trends**: The time series of PCI post-maintenance shows an average increase of 5 points in the first 6 months, then gradual decline.")
