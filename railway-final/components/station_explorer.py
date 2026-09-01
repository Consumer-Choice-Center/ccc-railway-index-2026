import pandas as pd
import plotly.express as px
import streamlit as st
from src.brand import PRIMARY_ORANGE, PRIMARY_NAVY

SCORE_COMPONENTS = {
    "Ticket office hours": "operating_hours_score",
    "Ticket options": "ticket_score",
    "Waiting times": "wait_score",
    "Delayed trains": "delay_score",
    "In-station information": "information_score",
    "Elevators / escalators": "elevators_score",
    "Accessibility": "accessibility_score",
    "Shops / kiosks": "shops_score",
    "Restaurants / takeaway": "restaurants_score",
    "First-class lounge": "lounge_score",
    "Application": "application_score",
    "Free Wi-Fi": "wifi_score",
    "Connections / coverage": "connections_score",
    "Rail competition": "competition_score",
    "Ride hailing": "ride_hailing_score",
}

def render_station_explorer(df):
    st.subheader("Station Explorer")
    options = df.sort_values("total_score", ascending=False)["station"].tolist()
    selected = st.selectbox("Choose a station", options)
    row = df[df["station"].eq(selected)].iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rank", f"#{int(row['rank_2026'])}")
    c2.metric("Total score", f"{row['total_score']:.1f}")
    c3.metric("Delayed trains", f"{row['delay_percent_2026']:.1f}%")
    c4.metric("Average wait", f"{row['wait_minutes_2026']:.2f} min")

    comp = pd.DataFrame({
        "Criterion": list(SCORE_COMPONENTS.keys()),
        "Points": [row[col] for col in SCORE_COMPONENTS.values()],
    }).sort_values("Points")

    fig = px.bar(
    comp,
    x="Points",
    y="Criterion",
    orientation="h",
    title=f"{selected} score breakdown",
)
    fig.update_traces(
        marker_color=PRIMARY_ORANGE,
        marker_line_color="white",
        marker_line_width=1.0,
        hovertemplate="<b>%{y}</b><br>%{x:.1f} points<extra></extra>",
    )
    fig.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFF7EF",
        font=dict(family="Montserrat", color=PRIMARY_NAVY),
        title_font=dict(size=20, color=PRIMARY_NAVY),
        margin=dict(l=10, r=10, t=55, b=10),
        height=520,
        xaxis=dict(showgrid=True, gridcolor="#E7ECF4", zeroline=False, title=""),
        yaxis=dict(showgrid=False, title=""),
    )
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
