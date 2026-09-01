import plotly.express as px
import streamlit as st
from src.brand import PRIMARY_NAVY, PRIMARY_ORANGE, BRICK_CORAL, DEEP_TEAL

def render_punctuality(df):
    st.subheader("Punctuality & Waiting Times")

    left, right = st.columns(2)

    best = df.nsmallest(10, "delay_percent_2026")
    worst = df.nlargest(10, "delay_percent_2026")

    fig = px.bar(
        best.sort_values("delay_percent_2026", ascending=False),
        x="delay_percent_2026",
        y="station",
        orientation="h",
        labels={"delay_percent_2026": "Delayed trains (%)", "station": ""},
        title="Most punctual: fewest delayed trains",
    )
    fig.update_traces(
        marker_color=DEEP_TEAL,
        marker_line_color="white",
        marker_line_width=1.2,
        hovertemplate="<b>%{y}</b><br>%{x:.1f}<extra></extra>",
    )
    fig.update_layout(
        paper_bgcolor="#FFF7EF",
        plot_bgcolor="#FFF7EF",
        font=dict(family="Montserrat", color=PRIMARY_NAVY),
        title_font=dict(size=20, color=PRIMARY_NAVY),
        margin=dict(l=10, r=10, t=60, b=10),
        height=420,
        xaxis=dict(showgrid=True, gridcolor="#E7ECF4", zeroline=False, title=""),
        yaxis=dict(showgrid=False, title=""),
    )
    left.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    fig = px.bar(
        worst.sort_values("delay_percent_2026", ascending=True),
        x="delay_percent_2026",
        y="station",
        orientation="h",
        labels={"delay_percent_2026": "Delayed trains (%)", "station": ""},
        title="Least punctual: most delayed trains",
    )
    fig.update_traces(
        marker_color=BRICK_CORAL,
        marker_line_color="white",
        marker_line_width=1.2,
        hovertemplate="<b>%{y}</b><br>%{x:.1f}<extra></extra>",
    )
    fig.update_layout(
        paper_bgcolor="#FFF7EF",
        plot_bgcolor="#FFF7EF",
        font=dict(family="Montserrat", color=PRIMARY_NAVY),
        title_font=dict(size=20, color=PRIMARY_NAVY),
        margin=dict(l=10, r=10, t=60, b=10),
        height=420,
        xaxis=dict(showgrid=True, gridcolor="#E7ECF4", zeroline=False, title=""),
        yaxis=dict(showgrid=False, title=""),
    )
    right.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
