from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.io as pio
import streamlit as st

from src.brand import BRICK_CORAL, CHART_SEQUENCE, COOL_MIST, PRIMARY_NAVY, PRIMARY_ORANGE
from src.data_loader import load_stations
from components.rankings import render_rankings_table
from components.punctuality import render_punctuality
from components.station_explorer import render_station_explorer

ROOT = Path(__file__).parent

st.set_page_config(
    page_title="European Railway Station Index 2026 | CCC",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="collapsed",
)
stylesheet = (ROOT / "styles.css").read_text(encoding="utf-8")
st.markdown(f"<style>{stylesheet}</style>", unsafe_allow_html=True)

df = load_stations()

pio.templates["ccc"] = pio.templates["plotly_white"]
pio.templates["ccc"].layout.font.family = "Montserrat, Arial, sans-serif"
pio.templates["ccc"].layout.font.color = PRIMARY_NAVY
pio.templates["ccc"].layout.colorway = CHART_SEQUENCE
pio.templates["ccc"].layout.paper_bgcolor = "#FFFFFF"
pio.templates["ccc"].layout.plot_bgcolor = "#FFFFFF"
pio.templates.default = "ccc"


def section(kicker: str, title: str, text: str, tone: str) -> None:
    st.markdown(
        f'''<section class="section-banner {tone}">
          <div class="section-kicker">{kicker}</div>
          <h2>{title}</h2>
          <p class="lede">{text}</p>
        </section>''',
        unsafe_allow_html=True,
    )


st.markdown('<div id="index"></div>', unsafe_allow_html=True)
section(
    "01 · THE RANKINGS",
    "How does your station compare?",
    "Search the full 2026 working ranking and compare total score, passenger volume, delays, and average waiting time.",
    "ranking-banner",
)
render_rankings_table(df)

st.markdown('<div id="reliability"></div>', unsafe_allow_html=True)
germany = df[df["country"].eq("Germany")].copy()
eu_delay = df["delay_percent_2026"].mean()
eu_wait = df["wait_minutes_2026"].mean()
de_delay = germany["delay_percent_2026"].mean() if not germany.empty else float("nan")
de_wait = germany["wait_minutes_2026"].mean() if not germany.empty else float("nan")

st.markdown(
    f'''
    <section class="dark-story">
      <div class="section-kicker dark-kicker">02 · PUNCTUALITY & WAITING TIMES</div>
      <h2>Where do European rail passengers lose the most time?</h2>
      <p>Reliability is one of the clearest dividing lines in the index. Waiting times and delayed trains are scored separately because each affects the passenger experience in a different way.</p>
      <div class="dark-stats">
        <div><span>EUROPE AVG. DELAY RATE</span><strong>{eu_delay:.1f}%</strong></div>
        <div><span>EUROPE AVG. WAIT</span><strong>{eu_wait:.2f} min</strong></div>
        <div><span>GERMANY AVG. DELAY RATE</span><strong>{de_delay:.1f}%</strong></div>
        <div><span>GERMANY AVG. WAIT</span><strong>{de_wait:.2f} min</strong></div>
      </div>
    </section>
    ''',
    unsafe_allow_html=True,
)
render_punctuality(df)

if not germany.empty:
    st.markdown("### Germany snapshot")
    g1, g2, g3, g4 = st.columns(4)
    g1.metric("German stations", len(germany))
    g2.metric("Delay gap vs Europe", f"{de_delay-eu_delay:+.1f} pp")
    g3.metric("Wait gap vs Europe", f"{de_wait-eu_wait:+.2f} min")
    g4.metric("Highest-ranked German station", germany.sort_values("total_score", ascending=False).iloc[0]["station"])

st.markdown('<div id="explorer"></div>', unsafe_allow_html=True)
section(
    "03 · STATION EXPLORER",
    "Understand the score",
    "Choose any station to see its headline performance and the components contributing to the overall index result.",
    "explorer-banner",
)
render_station_explorer(df)

section(
    "04 · COUNTRY PERFORMANCE",
    "Different countries, different passenger experiences",
    "Country averages provide context for broader patterns, but always reflect the set of stations included in the index rather than an entire national railway system.",
    "country-banner",
)
country_source = df.copy()
country_source["country"] = (
    country_source["country"]
    .astype("string")
    .str.strip()
    .str.replace(r"\s+", " ", regex=True)
)
country = (
    country_source.groupby("country", as_index=False)
    .agg(stations=("station", "count"), avg_score=("total_score", "mean"), avg_delay=("delay_percent_2026", "mean"), avg_wait=("wait_minutes_2026", "mean"))
)
fig = px.scatter(
    country,
    x="avg_delay",
    y="avg_score",
    size="stations",
    text="country",
    color="avg_wait",
    color_continuous_scale=[COOL_MIST, PRIMARY_ORANGE, BRICK_CORAL],
    custom_data=["country", "avg_delay", "avg_score", "stations", "avg_wait"],
    labels={"avg_delay": "Average delayed trains (%)", "avg_score": "Average station score", "avg_wait": "Avg. wait"},
)
fig.update_traces(
    textposition="top center",
    marker=dict(line=dict(color="#FFFFFF", width=1.4)),
    hovertemplate=(
        "<b>%{customdata[0]}</b><br><br>"
        "Delayed trains: <b>%{customdata[1]:.1f}%</b><br>"
        "Station score: <b>%{customdata[2]:.1f}</b><br>"
        "Stations in index: <b>%{customdata[3]:.0f}</b><br>"
        "Average wait: <b>%{customdata[4]:.1f} min</b>"
        "<extra></extra>"
    ),
)
fig.update_layout(
    height=560,
    margin=dict(l=10, r=10, t=20, b=10),
    paper_bgcolor="#FFF7EF",
    plot_bgcolor="#FFF7EF",
    xaxis=dict(gridcolor="#E7ECF4", zeroline=False),
    yaxis=dict(gridcolor="#E7ECF4", zeroline=False),
    hoverlabel=dict(
        bgcolor=PRIMARY_NAVY,
        bordercolor=PRIMARY_ORANGE,
        font=dict(color="#FFFFFF", family="Montserrat, Arial, sans-serif", size=13),
        align="left",
    ),
    coloraxis_colorbar=dict(title="Avg. wait<br>(minutes)", tickformat=".0f"),
)
st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

st.markdown(
    """
    <footer>
      CONSUMER CHOICE CENTER
      <span>European Railway Station Index · 2026 working edition</span>
    </footer>
    """,
    unsafe_allow_html=True,
)
