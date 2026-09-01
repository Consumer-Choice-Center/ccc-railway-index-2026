from __future__ import annotations

import base64
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
ASSETS = ROOT / "assets"

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


def uri(path: Path) -> str | None:
    if not path.exists():
        return None
    suffix = path.suffix.lower()
    mime = "image/png" if suffix == ".png" else "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


def section(kicker: str, title: str, text: str) -> None:
    st.markdown(
        f'<div class="section-kicker">{kicker}</div><h2>{title}</h2><p class="lede">{text}</p>',
        unsafe_allow_html=True,
    )


def fmt_pct(v):
    return "—" if pd.isna(v) else f"{v:.1f}%"


def fmt_min(v):
    return "—" if pd.isna(v) else f"{v:.2f} min".replace(".00 min", " min")


logo_uri = uri(ASSETS / "ccc-logo.png")
if logo_uri:
    brand = f'<img src="{logo_uri}" alt="Consumer Choice Center">'
else:
    brand = '<div class="fallback-brand"><span class="fallback-mark"></span><span>CONSUMER<br>CHOICE<br>CENTER</span></div>'

hero_uri = uri(ASSETS / "zurich-railway-station.jpg")
if hero_uri:
    hero_class = "hero-highlight hero-image"
    hero_style = (
        "background-image:linear-gradient(180deg,rgba(34,38,78,.10) 0%,"
        "rgba(34,38,78,.92) 100%),url('" + hero_uri + "');"
    )
else:
    hero_class = "hero-highlight"
    hero_style = ""

st.markdown(
    f'''
    <nav class="topnav">
      <div class="nav-brand">{brand}<span class="tracker-label">RAILWAY STATION INDEX</span></div>
      <div class="nav-links">
        <a href="#about">About</a>
        <a href="#index">Index</a>
        <a href="#reliability">Punctuality</a>
        <a href="#explorer">Explorer</a>
        <a href="#method">Methodology</a>
      </div>
    </nav>
    ''',
    unsafe_allow_html=True,
)

top = df.sort_values(["total_score", "station"], ascending=[False, True]).copy()
leader = top.iloc[0]
best_delay = df.nsmallest(1, "delay_percent_2026").iloc[0]
best_wait = df.nsmallest(1, "wait_minutes_2026").iloc[0]

st.markdown(
    f'''
    <section class="rail-hero">
      <div class="rail-hero-copy">
        <div class="eyebrow">EUROPEAN RAILWAY STATION INDEX · 2026</div>
        <h1>Passenger convenience, station by station.</h1>
        <p>
          Compare major European railway stations across the things passengers experience directly:
          <b>reliability, waiting times, accessibility, ticketing, amenities, connectivity, competition, and mobility options.</b>
        </p>
        <div class="hero-actions">
          <a class="button primary" href="#index">Explore the index →</a>
          <a class="button secondary" href="#about">About the research</a>
        </div>
      </div>
      <div class="{hero_class}" style="{hero_style}">
        <span class="highlight-label">2026 LEADER</span>
        <strong>{leader["station"]}</strong>
        <span>{leader["country"]} · {leader["total_score"]:.1f} points</span>
        <div class="highlight-rule"></div>
        <small>Working 2026 research edition</small>
      </div>
    </section>
    ''',
    unsafe_allow_html=True,
)

st.markdown(
    '''
    <div class="definition-band">
      <b>What does the index capture?</b>
      Passenger-facing convenience at major European rail hubs. Passenger volume determines which stations enter
      the index, while the score reflects service and access characteristics rather than station size itself.
    </div>
    ''',
    unsafe_allow_html=True,
)

st.markdown('<div id="about"></div>', unsafe_allow_html=True)
about_left, about_right = st.columns([0.40, 0.60], gap="large", vertical_alignment="top")
with about_left:
    st.markdown(
        '''<section class="about-title">
          <div class="section-kicker compact">ABOUT THE INDEX</div>
          <h2>What is the European Railway Station Index?</h2>
          <p>A research-driven comparison of major European rail hubs from the perspective of passenger convenience. The dashboard turns the annual index into an interactive, source-conscious research tool.</p>
        </section>''',
        unsafe_allow_html=True,
    )
with about_right:
    st.markdown(
        '''<div class="rail-accordion">
          <details open><summary>Overview</summary><p>Challenging conditions reveal which stations can preserve reliability and passenger convenience under pressure, which are improving, and where persistent weaknesses remain. The index makes those differences visible station by station.</p></details>
          <details><summary>What does the index measure?</summary><p>Ticket-office availability, ticket options, waiting times, delayed trains, in-station information, accessibility, shops and restaurants, lounges, applications, Wi-Fi, connections, rail competition, and ride-hailing availability.</p></details>
          <details><summary>How are stations selected?</summary><p>Major railway stations are selected using passenger volume. Passenger volume is descriptive and determines inclusion; it does not itself award points in the index.</p></details>
          <details><summary>Why give punctuality and waiting times special attention?</summary><p>They are among the most immediate parts of a passenger's experience. Delays can also cascade into crowding and strain ticketing, digital services, shops, restaurants, and other station infrastructure.</p></details>
          <details><summary>Are all figures from calendar year 2026?</summary><p>No. The index uses the latest data available for each indicator. Source years may vary because many operators do not publish annual updates, and reporting standards differ across operators and countries. Where possible, the dashboard identifies the relevant source year and methodology.</p></details>
          <details><summary>How comparable are the data across countries?</summary><p>Reporting standards, definitions, and source years differ across jurisdictions. The dashboard identifies source timing and methodology notes wherever possible so those differences remain visible.</p></details>
        </div>''',
        unsafe_allow_html=True,
    )

st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)
section(
    "2026 · AT A GLANCE",
    "The signal behind the ranking",
    "The headline score is useful, but the most interesting stories are often underneath it: reliability, waiting time, traffic growth, and the gap between Europe's strongest and weakest-performing hubs.",
)

st.markdown(
    f"""
    <div class="stat-grid">
      <div class="stat-card">
        <div class="stat-label">Stations ranked</div>
        <div class="stat-value big">{len(df)}</div>
        <div class="stat-sub">Major European hubs</div>
      </div>

      <div class="stat-card">
        <div class="stat-label">2026 leader</div>
        <div class="stat-value">{leader["station"]}</div>
        <div class="stat-sub">{leader["total_score"]:.1f} pts</div>
      </div>

      <div class="stat-card">
        <div class="stat-label">Lowest delay rate</div>
        <div class="stat-value">{best_delay["station"]}</div>
        <div class="stat-sub">{fmt_pct(best_delay["delay_percent_2026"])}</div>
      </div>

      <div class="stat-card">
        <div class="stat-label">Shortest average wait</div>
        <div class="stat-value">{best_wait["station"]}</div>
        <div class="stat-sub">{fmt_min(best_wait["wait_minutes_2026"])}</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div id="index"></div>', unsafe_allow_html=True)
section(
    "01 · THE RANKINGS",
    "How does your station compare?",
    "Search the full 2026 working ranking and compare total score, passenger volume, delays, and average waiting time.",
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

st.markdown('<div class="section-spacer"></div>', unsafe_allow_html=True)
section(
    "03 · YOUR PRIORITIES",
    "What makes a railway station good for you?",
    "Adjust the weights to create an exploratory personalized ranking. This does not replace the official index; it simply shows how the ordering changes when passengers value different dimensions differently.",
)

weight_map = {
    "Reliability": ["delay_score"],
    "Waiting time": ["wait_score"],
    "Accessibility": ["elevators_score", "accessibility_score", "information_score"],
    "Ticketing": ["operating_hours_score", "ticket_score"],
    "Amenities": ["shops_score", "restaurants_score", "lounge_score"],
    "Connectivity": ["connections_score"],
    "Digital services": ["application_score", "wifi_score"],
    "Competition & mobility options": ["competition_score", "ride_hailing_score"],
}

slider_cols = st.columns(2)
weights = {}
for i, label in enumerate(weight_map):
    with slider_cols[i % 2]:
        weights[label] = st.slider(label, 0, 10, 5, key=f"weight_{label}")

weighted = df.copy()
weighted["personalized_score"] = 0.0
total_weight = sum(weights.values())
if total_weight > 0:
    for label, cols in weight_map.items():
        component = weighted[cols].fillna(0).sum(axis=1)
        max_component = component.max()
        normalized = component / max_component if max_component and max_component > 0 else 0
        weighted["personalized_score"] += normalized * weights[label]
    weighted["personalized_score"] = weighted["personalized_score"] / total_weight * 100

personal_top = weighted.sort_values("personalized_score", ascending=False).head(10).copy()
personal_top["match_rank"] = range(1, len(personal_top) + 1)
left, right = st.columns([0.36, 0.64], gap="large")
with left:
    st.markdown("### Your top matches")
    for rank, (_, row) in enumerate(personal_top.head(5).iterrows(), start=1):
        st.markdown(
            f'<div class="match-card"><span>#{rank}</span><div><strong>{row["station"]}</strong><small>{row["country"]}</small></div><b>{row["personalized_score"]:.1f}</b></div>',
            unsafe_allow_html=True,
        )
with right:
    fig = px.bar(
        personal_top.sort_values("personalized_score"),
        x="personalized_score",
        y="station",
        orientation="h",
        color="personalized_score",
        color_continuous_scale=[COOL_MIST, PRIMARY_ORANGE, BRICK_CORAL],
        custom_data=["match_rank", "station", "country", "personalized_score"],
        labels={"personalized_score": "Personalized match", "station": ""},
    )

    fig.update_traces(
        marker_line_color="#FFFFFF",
        marker_line_width=1.2,
        hovertemplate=(
            "<b>#%{customdata[0]} · %{customdata[1]}</b><br>"
            "%{customdata[2]}<br><br>"
            "Personalized match: <b>%{customdata[3]:.1f}</b>"
            "<extra></extra>"
        ),
    )

    fig.update_layout(
        height=430,
        coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_range=[0, 100],
        hoverlabel=dict(
            bgcolor=PRIMARY_NAVY,
            bordercolor=PRIMARY_ORANGE,
            font=dict(
                color="#FFFFFF",
                family="Montserrat, Arial, sans-serif",
                size=13,
            ),
            align="left",
        ),
    )
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

st.caption("Personalized results are exploratory and do not alter the official European Railway Station Index ranking.")

st.markdown('<div id="explorer"></div>', unsafe_allow_html=True)
section(
    "04 · STATION EXPLORER",
    "Understand the score",
    "Choose any station to see its headline performance and the components contributing to the overall index result.",
)
render_station_explorer(df)

section(
    "05 · COUNTRY PERFORMANCE",
    "Different countries, different passenger experiences",
    "Country averages provide context for broader patterns, but always reflect the set of stations included in the index rather than an entire national railway system.",
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
    hoverlabel=dict(
        bgcolor=PRIMARY_NAVY,
        bordercolor=PRIMARY_ORANGE,
        font=dict(color="#FFFFFF", family="Montserrat, Arial, sans-serif", size=13),
        align="left",
    ),
    coloraxis_colorbar=dict(title="Avg. wait<br>(minutes)", tickformat=".0f"),
)
st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

st.markdown('<div id="method"></div>', unsafe_allow_html=True)
section(
    "06 · METHODOLOGY",
    "Transparent by design",
    "The dashboard uses the 2026 research workbook for station-level values and the published 2025 methodology as the explanatory reference until the final 2026 edition is issued.",
)
method_left, method_right = st.columns([0.42, 0.58], gap="large", vertical_alignment="top")
with method_left:
    st.markdown(
        '''<div class="method-card method-freshness">
          <div class="section-kicker compact">DATA FRESHNESS</div>
          <h3>Latest available data</h3>
          <p class="method-intro">The index uses the latest data available for each indicator.</p>
          <div class="freshness-list">
            <div><span>Update schedules</span><p>Many operators do not publish new figures every year.</p></div>
            <div><span>Reporting standards</span><p>Definitions and methods can differ across operators and countries.</p></div>
            <div><span>Source transparency</span><p>The dashboard identifies source years and methodology wherever possible.</p></div>
          </div>
        </div>''',
        unsafe_allow_html=True,
    )
with method_right:
    st.markdown(
        '''<div class="rail-accordion method-accordion">
        <details open>
          <summary><span class="method-number">01</span>Waiting times</summary>
          <div class="threshold-grid three">
            <span><b>10 pts</b>&le; 5 min</span>
            <span><b>5 pts</b>&gt; 5 min and &le; 10 min</span>
            <span><b>0 pts</b>&gt; 10 min</span>
          </div>
        </details>
        <details>
          <summary><span class="method-number">02</span>Delayed trains</summary>
          <div class="threshold-grid four">
            <span><b>15 pts</b>&le; 10%</span>
            <span><b>10 pts</b>&gt; 10% and &le; 20%</span>
            <span><b>5 pts</b>&gt; 20% and &lt; 40%</span>
            <span><b>0 pts</b>&ge; 40%</span>
          </div>
        </details>
        <details>
          <summary><span class="method-number">03</span>Passenger volume</summary>
          <p>Passenger volume determines which major stations are included. It is descriptive and does not itself award points.</p>
        </details>
        <details>
          <summary><span class="method-number">04</span>Cross-country comparability</summary>
          <p>Definitions, reporting practices, and source years can differ across railway systems. The dashboard exposes timing and source context wherever possible.</p>
        </details>
        </div>
        <div class="report-callout">
          <div class="report-callout-copy">
            <span>CURRENT EDITION</span>
            <strong>See the published 2026 methodology and rankings.</strong>
          </div>
          <a class="button primary report-link-button"
             href="INSERT LINK HERE"
             target="_blank" rel="noopener noreferrer">
            Read the report →
          </a>
        </div>''',
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <footer>
      CONSUMER CHOICE CENTER
      <span>European Railway Station Index · 2026 working edition</span>
    </footer>
    """,
    unsafe_allow_html=True,
)
