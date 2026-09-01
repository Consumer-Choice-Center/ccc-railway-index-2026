import streamlit as st


def _score_style(value):
    if value is None or value != value:
        return ""
    if value >= 90:
        return "background-color:#DFEEE2;color:#157A35;font-weight:700"
    if value >= 80:
        return "background-color:#FFF2E8;color:#B9473A;font-weight:700"
    return "background-color:#F1F2F7;color:#22264E;font-weight:700"


def _delay_style(value):
    if value is None or value != value:
        return ""
    if value <= 10:
        return "background-color:#DFEEE2;color:#157A35;font-weight:600"
    if value < 20:
        return "background-color:#FFF4D6;color:#8A5A00;font-weight:600"
    if value < 40:
        return "background-color:#FFF2E8;color:#B9473A;font-weight:600"
    return "background-color:#F8DEDA;color:#9E332B;font-weight:700"


def _wait_style(value):
    if value is None or value != value:
        return ""
    if value <= 5:
        return "background-color:#DFEEE2;color:#157A35;font-weight:600"
    if value <= 10:
        return "background-color:#FFF4D6;color:#8A5A00;font-weight:600"
    return "background-color:#F8DEDA;color:#9E332B;font-weight:700"


def render_rankings_table(df):
    display = df.sort_values(
        ["total_score", "station"], ascending=[False, True]
    )[[
        "rank_2026", "country", "city", "station", "total_score",
        "passenger_volume_latest", "delay_percent_2026", "wait_minutes_2026"
    ]].rename(columns={
        "rank_2026": "Rank",
        "country": "Country",
        "city": "City",
        "station": "Station",
        "total_score": "Score",
        "passenger_volume_latest": "Passenger volume (m)",
        "delay_percent_2026": "Delayed trains (%)",
        "wait_minutes_2026": "Avg. wait (min)",
    })

    styled = (
        display.style
        .map(_score_style, subset=["Score"])
        .map(_delay_style, subset=["Delayed trains (%)"])
        .map(_wait_style, subset=["Avg. wait (min)"])
        .format({
            "Rank": "{:.0f}",
            "Score": "{:.1f}",
            "Passenger volume (m)": "{:.2f}",
            "Delayed trains (%)": "{:.1f}",
            "Avg. wait (min)": "{:.2f}",
        }, na_rep="—")
    )

    st.markdown(
        '''<div class="rankings-legend" aria-label="Table colour key">
          <span class="legend-chip strong">Stronger result</span>
          <span class="legend-chip middle">Mid-range</span>
          <span class="legend-chip weak">Needs attention</span>
        </div>''',
        unsafe_allow_html=True,
    )

    st.dataframe(
        styled,
        hide_index=True,
        width="stretch",
        height=460,
        column_config={
            "Rank": st.column_config.NumberColumn("Rank", width="small", format="%d"),
            "Country": st.column_config.TextColumn("Country", width="medium"),
            "City": st.column_config.TextColumn("City", width="medium"),
            "Station": st.column_config.TextColumn("Station", width="large"),
            "Score": st.column_config.NumberColumn(
                "Score", width="small", format="%.1f"
            ),
            "Passenger volume (m)": st.column_config.NumberColumn(
                "Passenger volume (m)", width="medium", format="%.2f"
            ),
            "Delayed trains (%)": st.column_config.NumberColumn(
                "Delayed trains (%)", width="medium", format="%.1f%%"
            ),
            "Avg. wait (min)": st.column_config.NumberColumn(
                "Avg. wait (min)", width="medium", format="%.2f"
            ),
        },
    )
