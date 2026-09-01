from __future__ import annotations

import html
import unicodedata

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.brand import BRIGHT_TEAL, PRIMARY_NAVY, PRIMARY_ORANGE


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


def _normalize_search(value: object) -> str:
    normalized = unicodedata.normalize("NFKD", str(value))
    return "".join(
        character for character in normalized if not unicodedata.combining(character)
    ).casefold().strip()


def _filter_stations(df: pd.DataFrame, query: str) -> pd.DataFrame:
    ranked = df.sort_values(["total_score", "station"], ascending=[False, True])
    normalized_query = _normalize_search(query)
    if not normalized_query:
        return ranked

    tokens = normalized_query.split()
    searchable = ranked[["station", "city", "country"]].fillna("").agg(" ".join, axis=1)
    normalized_rows = searchable.map(_normalize_search)
    mask = normalized_rows.map(lambda value: all(token in value for token in tokens))
    return ranked[mask]


def _format_station_label(row: pd.Series) -> str:
    return f'{row["station"]} — {row["city"]}, {row["country"]}'


def _sync_selection_state(key: str, options: list[object]) -> None:
    current = st.session_state.get(key)
    if len(options) == 1:
        st.session_state[key] = options[0]
    elif current not in options:
        st.session_state[key] = None


def _score_maxima(df: pd.DataFrame) -> pd.Series:
    columns = list(SCORE_COMPONENTS.values())
    return df[columns].apply(pd.to_numeric, errors="coerce").max().replace(0, pd.NA)


def _criterion_frame(row: pd.Series, maxima: pd.Series) -> pd.DataFrame:
    frame = pd.DataFrame(
        {
            "Criterion": list(SCORE_COMPONENTS.keys()),
            "column": list(SCORE_COMPONENTS.values()),
        }
    )
    frame["Points"] = frame["column"].map(lambda column: pd.to_numeric(row[column], errors="coerce"))
    frame["Available"] = frame["column"].map(maxima)
    frame["Percent"] = (frame["Points"] / frame["Available"] * 100).clip(0, 100)
    return frame.drop(columns="column")


def _takeaways(frame: pd.DataFrame) -> tuple[list[str], list[str]]:
    scored = frame.dropna(subset=["Percent"])
    strongest = scored.sort_values(["Percent", "Criterion"], ascending=[False, True])
    weakest = scored.sort_values(["Percent", "Criterion"], ascending=[True, True])
    return strongest["Criterion"].head(2).tolist(), weakest["Criterion"].head(2).tolist()


def _format_metric(value: object, suffix: str = "", decimals: int = 1) -> str:
    if pd.isna(value):
        return "—"
    return f"{float(value):.{decimals}f}{suffix}"


def _station_card(row: pd.Series, frame: pd.DataFrame, *, compact: bool = False) -> None:
    station = html.escape(str(row["station"]))
    city = html.escape(str(row["city"]))
    country = html.escape(str(row["country"]))
    rank = "—" if pd.isna(row["rank_2026"]) else f'#{int(row["rank_2026"])}'
    score = _format_metric(row["total_score"], decimals=1)
    delay = _format_metric(row["delay_percent_2026"], suffix="%", decimals=1)
    wait = _format_metric(row["wait_minutes_2026"], suffix=" min", decimals=2)
    strongest, weakest = _takeaways(frame)
    strongest_text = html.escape(" and ".join(strongest)) or "No comparable values"
    weakest_text = html.escape(" and ".join(weakest)) or "No comparable values"
    compact_class = " station-finder-card-compact" if compact else ""

    st.markdown(
        f'''
        <article class="station-finder-card{compact_class}" aria-live="polite">
          <div class="station-finder-identity">
            <span class="station-finder-location">{city} · {country}</span>
            <h3>{station}</h3>
            <span class="station-finder-rank">{rank} in the 2026 index</span>
          </div>
          <div class="station-finder-body">
            <div class="station-finder-metrics" aria-label="Station headline results">
              <div><span>Total score</span><strong>{score}</strong></div>
              <div><span>Delayed trains</span><strong>{delay}</strong></div>
              <div><span>Average wait</span><strong>{wait}</strong></div>
            </div>
            <div class="station-finder-takeaways">
              <div><span>Strongest relative scores</span><p>{strongest_text}</p></div>
              <div><span>Areas with most room to improve</span><p>{weakest_text}</p></div>
            </div>
          </div>
        </article>
        ''',
        unsafe_allow_html=True,
    )


def _breakdown_chart(frame: pd.DataFrame, station: str) -> go.Figure:
    ordered = frame.sort_values(["Points", "Criterion"], ascending=[True, True])
    figure = go.Figure(
        go.Bar(
            x=ordered["Points"],
            y=ordered["Criterion"],
            orientation="h",
            marker={"color": PRIMARY_ORANGE, "line": {"color": "#FFFFFF", "width": 1.2}},
            customdata=ordered[["Available", "Percent"]],
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Points: %{x:.1f} of %{customdata[0]:.1f}<br>"
                "Share of available points: %{customdata[1]:.0f}%"
                "<extra></extra>"
            ),
        )
    )
    figure.update_traces(marker_cornerradius=4)
    figure.update_layout(
        title=f"{station} score breakdown",
        height=520,
        showlegend=False,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFF7EF",
        font={"family": "Montserrat", "color": PRIMARY_NAVY},
        title_font={"size": 20, "color": PRIMARY_NAVY},
        margin={"l": 10, "r": 10, "t": 55, "b": 10},
        bargap=0.3,
        xaxis={"showgrid": True, "gridcolor": "#E7ECF4", "zeroline": False, "title": "Points"},
        yaxis={"showgrid": False, "title": ""},
    )
    return figure


def _comparison_frame(
    row_a: pd.Series,
    row_b: pd.Series,
    maxima: pd.Series,
) -> pd.DataFrame:
    first = _criterion_frame(row_a, maxima).assign(Station=_format_station_label(row_a))
    second = _criterion_frame(row_b, maxima).assign(Station=_format_station_label(row_b))
    return pd.concat([first, second], ignore_index=True)


def _comparison_chart(frame: pd.DataFrame, station_a: str, station_b: str) -> go.Figure:
    figure = px.bar(
        frame,
        x="Percent",
        y="Criterion",
        color="Station",
        orientation="h",
        barmode="group",
        color_discrete_map={station_a: PRIMARY_ORANGE, station_b: BRIGHT_TEAL},
        custom_data=["Points", "Available"],
        labels={"Percent": "Share of available points (%)"},
        category_orders={"Criterion": list(reversed(SCORE_COMPONENTS.keys()))},
    )
    figure.update_traces(
        marker_line_color="#FFFFFF",
        marker_line_width=1.2,
        marker_cornerradius=4,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "%{fullData.name}: %{customdata[0]:.1f} of %{customdata[1]:.1f} points<br>"
            "Share of available points: %{x:.0f}%"
            "<extra></extra>"
        ),
    )
    figure.update_layout(
        height=620,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFF7EF",
        font={"family": "Montserrat", "color": PRIMARY_NAVY},
        margin={"l": 10, "r": 10, "t": 25, "b": 10},
        bargap=0.24,
        bargroupgap=0.08,
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.01, "xanchor": "left", "x": 0},
        xaxis={
            "range": [0, 100],
            "showgrid": True,
            "gridcolor": "#E7ECF4",
            "zeroline": False,
            "title": "Share of available points (%)",
        },
        yaxis={"showgrid": False, "title": ""},
    )
    return figure


def _score_table(frame: pd.DataFrame) -> None:
    display = frame[["Criterion", "Points", "Available", "Percent"]].copy()
    st.dataframe(
        display,
        hide_index=True,
        width="stretch",
        column_config={
            "Criterion": st.column_config.TextColumn("Criterion", width="large"),
            "Points": st.column_config.NumberColumn("Points", format="%.1f"),
            "Available": st.column_config.NumberColumn("Observed maximum", format="%.1f"),
            "Percent": st.column_config.ProgressColumn(
                "Share of available points",
                min_value=0,
                max_value=100,
                format="%.0f%%",
            ),
        },
    )


def _comparison_table(frame: pd.DataFrame, station_a: str, station_b: str) -> None:
    display = frame.pivot(index="Criterion", columns="Station", values="Points").reset_index()
    ordered_columns = ["Criterion", station_a, station_b]
    st.dataframe(display[ordered_columns], hide_index=True, width="stretch")


def render_station_explorer(df: pd.DataFrame) -> None:
    maxima = _score_maxima(df)
    query = st.text_input(
        "Enter a city or station",
        placeholder="Try Berlin, Paris, Zürich, or a station name",
        key="station_finder_query",
    )
    matches = _filter_stations(df, query)

    if matches.empty:
        st.warning("No stations match that search. Try another city, station, or country.")
        return

    option_indices = matches.index.tolist()
    _sync_selection_state("station_finder_selection", option_indices)
    selected_index = st.selectbox(
        "Choose a matching station",
        option_indices,
        index=None,
        format_func=lambda index: _format_station_label(matches.loc[index]),
        placeholder=f"Choose from {len(option_indices)} matching stations",
        key="station_finder_selection",
    )

    if selected_index is None:
        st.info(f"{len(option_indices)} stations match. Choose one to see its results.")
        return

    selected = df.loc[selected_index]
    selected_frame = _criterion_frame(selected, maxima)
    _station_card(selected, selected_frame)

    with st.expander("See the complete score breakdown"):
        chart_tab, table_tab = st.tabs(["Chart", "Accessible data table"])
        with chart_tab:
            st.plotly_chart(
                _breakdown_chart(selected_frame, str(selected["station"])),
                width="stretch",
                config={"displayModeBar": False},
            )
        with table_tab:
            _score_table(selected_frame)

    compare_enabled = st.toggle(
        "Compare another station",
        key="station_finder_compare_enabled",
    )
    if not compare_enabled:
        return

    st.markdown("### Choose a comparison station")
    comparison_query = st.text_input(
        "Enter another city or station",
        placeholder="Search the remaining stations",
        key="station_comparison_query",
    )
    comparison_matches = _filter_stations(df.drop(index=selected_index), comparison_query)
    if comparison_matches.empty:
        st.warning("No other stations match that comparison search.")
        return

    comparison_indices = comparison_matches.index.tolist()
    _sync_selection_state("station_comparison_selection", comparison_indices)
    comparison_index = st.selectbox(
        "Choose a station to compare",
        comparison_indices,
        index=None,
        format_func=lambda index: _format_station_label(comparison_matches.loc[index]),
        placeholder=f"Choose from {len(comparison_indices)} matching stations",
        key="station_comparison_selection",
    )
    if comparison_index is None:
        return

    comparison = df.loc[comparison_index]
    comparison_frame = _criterion_frame(comparison, maxima)
    card_a, card_b = st.columns(2, gap="large")
    with card_a:
        _station_card(selected, selected_frame, compact=True)
    with card_b:
        _station_card(comparison, comparison_frame, compact=True)

    station_a = _format_station_label(selected)
    station_b = _format_station_label(comparison)
    combined = _comparison_frame(selected, comparison, maxima)
    chart_tab, table_tab = st.tabs(["Comparison chart", "Accessible comparison table"])
    with chart_tab:
        st.plotly_chart(
            _comparison_chart(combined, station_a, station_b),
            width="stretch",
            config={"displayModeBar": False},
        )
    with table_tab:
        _comparison_table(combined, station_a, station_b)
