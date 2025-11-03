from dash import html, Input, Output, State

from meteo import defs
from meteo.conditions import WeatherDescription
from meteo.forecast import Forecast

from .widget import Widget


class DailyForecastWidget(Widget):
    def _create_summary_card(self, data: Forecast.DailyWeather) -> html.Div:
        weather_condition = WeatherDescription.get_condition(data.weather_code, False)
        return html.Div(
            className="flex flex-col items-center gap-2 bg-secondary rounded-xl p-4",
            children=[
                html.Div(data.date.strftime("%a. %d"), className="font-bold"),
                html.Div(html.Img(src=weather_condition.image), className="text-3xl"),
                html.Div(
                    f"{round(data.temperature_min)} / {round(data.temperature_max)} °{data.unit}",
                    className="text-lg font-semibold grow w-full text-center",
                ),
                html.Div(
                    f"☂️ {round(data.precipitation_probability, 1 if data.precipitation_probability > 0 else 0)}%",
                    className="text-s text-cyan-500/75",
                ),
            ],
        )

    def layout(self) -> html.Div:
        """Returns the layout of the daily forecast widget."""
        data_all = [Forecast.DailyWeather() for _ in range(8)]

        return super()._create_layout(
            html.H2(
                "7-Day Forecast",
                className="text-xl font-semibold mb-4",
            ),
            html.Spacer(),
            html.Div(
                id="daily-forecast-container",
                className="grid grid-cols-7 gap-4 overflow-x-auto pb-2",
                children=[self._create_summary_card(data) for data in data_all[1:]],
            ),
        )

    def setup_callbacks(self, app):
        super().setup_callbacks(app)

        @app.callback(
            Output("daily-forecast-container", "children"),
            Input(defs.LONG_FORECAST_INTERVAL_ID, "n_intervals"),
        )
        def update_daily_forecast(n_intervals: int):
            data_all = self.config.forecast.fetch_daily_weather(forecast_days=8)

            return [self._create_summary_card(data) for data in data_all[1:]]


__all__ = ["DailyForecastWidget"]
