import unittest

import pandas as pd
from streamlit.testing.v1 import AppTest

from components.station_explorer import (
    SCORE_COMPONENTS,
    _comparison_frame,
    _criterion_frame,
    _filter_stations,
    _format_station_label,
    _normalize_search,
    _score_maxima,
    _takeaways,
)
from src.data_loader import load_stations


class StationFinderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = load_stations()

    def test_search_is_case_and_accent_insensitive(self):
        self.assertEqual(_normalize_search("Zürich"), "zurich")
        matches = _filter_stations(self.df, "zurich")
        self.assertIn("Zürich Hbf", matches["station"].tolist())

    def test_search_matches_city_station_country_and_multiple_tokens(self):
        self.assertFalse(_filter_stations(self.df, "Berlin").empty)
        self.assertFalse(_filter_stations(self.df, "Berlin Germany").empty)
        self.assertFalse(_filter_stations(self.df, "Gare du Nord").empty)

    def test_empty_and_missing_searches(self):
        self.assertEqual(len(_filter_stations(self.df, "")), len(self.df))
        self.assertTrue(_filter_stations(self.df, "not-a-real-station").empty)

    def test_station_labels_include_disambiguating_location(self):
        first = self.df.iloc[0]
        label = _format_station_label(first)
        self.assertIn(str(first["station"]), label)
        self.assertIn(str(first["city"]), label)
        self.assertIn(str(first["country"]), label)

    def test_breakdown_and_takeaways_cover_every_criterion(self):
        maxima = _score_maxima(self.df)
        frame = _criterion_frame(self.df.iloc[0], maxima)
        strongest, weakest = _takeaways(frame)
        self.assertEqual(len(frame), len(SCORE_COMPONENTS))
        self.assertEqual(len(strongest), 2)
        self.assertEqual(len(weakest), 2)
        self.assertTrue(frame["Percent"].dropna().between(0, 100).all())

    def test_comparison_uses_unique_station_labels(self):
        maxima = _score_maxima(self.df)
        first = self.df.iloc[0]
        second = self.df.iloc[1]
        frame = _comparison_frame(first, second, maxima)
        self.assertEqual(len(frame), len(SCORE_COMPONENTS) * 2)
        self.assertEqual(frame["Station"].nunique(), 2)


class StationFinderAppTest(unittest.TestCase):
    def test_city_search_selection_and_comparison(self):
        app = AppTest.from_file("/app/app.py").run(timeout=30)
        app.text_input[0].input("Berlin").run(timeout=30)
        app.selectbox[0].select(app.selectbox[0].options[0]).run(timeout=30)
        self.assertFalse(app.exception)
        self.assertEqual(len(app.toggle), 1)

        app.toggle[0].set_value(True).run(timeout=30)
        app.text_input[1].input("Zurich").run(timeout=30)
        app.selectbox[1].select(app.selectbox[1].options[0]).run(timeout=30)
        self.assertFalse(app.exception)
        self.assertGreaterEqual(len(app.get("plotly_chart")), 6)
        self.assertTrue(any("Zürich" in option for option in app.selectbox[1].options))

    def test_embed_mode_only_renders_finder(self):
        app = AppTest.from_file("/app/app.py")
        app.query_params["view"] = "station-finder"
        app.query_params["embed"] = "true"
        app.run(timeout=30)
        self.assertFalse(app.exception)
        self.assertEqual(len(app.text_input), 1)
        self.assertFalse(any('<nav class="topnav">' in item.value for item in app.markdown))
        self.assertFalse(any("Read the report" in item.value for item in app.markdown))


if __name__ == "__main__":
    unittest.main()
